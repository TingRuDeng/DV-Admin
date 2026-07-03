from __future__ import annotations

import re
import sys
from pathlib import Path

from scripts.api_endpoint_contract_types import EndpointContract


FASTAPI_ONLY_ENDPOINT_KEYS = {"files_upload", "files_delete"}
DJANGO_ROUTER_RESOURCES = {"users", "roles", "menus", "dicts", "dict-items", "departments"}
FASTAPI_SYSTEM_PREFIXES = {
    "users": 'prefix="/users"',
    "roles": 'prefix="/roles"',
    "menus": 'prefix="/menus"',
    "departments": 'prefix="/departments"',
    "dicts": 'prefix="/dicts"',
    "dict-items": 'prefix="/dict-items"',
    "notices": 'prefix="/notices"',
    "logs": 'prefix="/logs"',
}


def validate_route_coverage(root: Path) -> list[str]:
    """校验关键端点契约至少能对应到 Django/FastAPI 路由入口。"""
    issues: list[str] = []
    contracts = load_endpoint_contracts(root)
    django_routes = load_django_routes(root)
    fastapi_routes = load_fastapi_routes(root)

    for contract in contracts:
        if contract.key not in FASTAPI_ONLY_ENDPOINT_KEYS:
            issues.extend(validate_django_contract_route(contract, django_routes))
        issues.extend(validate_fastapi_contract_route(contract, fastapi_routes))
    return issues


def validate_django_contract_route(contract: EndpointContract, routes: dict[str, object]) -> list[str]:
    """校验单个共享端点在 Django URLConf 或 AdminRouter 中有覆盖。"""
    route = normalized_contract_route(contract)
    if route.startswith("oauth/"):
        return validate_django_oauth_route(contract, route, routes)
    if route.startswith("system/"):
        return validate_django_system_route(contract, route, routes)
    return [f"{contract.key}: Django 路由覆盖校验暂不支持路径 {contract.path}"]


def validate_fastapi_contract_route(contract: EndpointContract, routes: dict[str, str]) -> list[str]:
    """校验单个端点在 FastAPI v1 router 树中有覆盖。"""
    route = normalized_contract_route(contract)
    if route.startswith("oauth/"):
        return validate_fastapi_prefixed_route(contract, routes, "oauth")
    if route.startswith("system/"):
        route_tail = route.removeprefix("system/")
        resource = route_tail.split("/", 1)[0]
        expected_prefix = FASTAPI_SYSTEM_PREFIXES.get(resource)
        if expected_prefix and expected_prefix in routes["system"]:
            return []
        return [f"{contract.key}: FastAPI system router 未覆盖资源前缀 {resource!r}"]
    if route == "files" or route.startswith("files/"):
        return validate_fastapi_prefixed_route(contract, routes, "files")
    return [f"{contract.key}: FastAPI 路由覆盖校验暂不支持路径 {contract.path}"]


def validate_django_oauth_route(
    contract: EndpointContract,
    route: str,
    routes: dict[str, object],
) -> list[str]:
    """校验 Django OAuth 显式 path 路由。"""
    oauth_routes = routes["oauth_explicit"]
    route_tail = route.removeprefix("oauth/")
    if route_tail in oauth_routes:
        return []
    return [f"{contract.key}: Django OAuth URLConf 未覆盖路径 {route_tail!r}"]


def validate_django_system_route(
    contract: EndpointContract,
    route: str,
    routes: dict[str, object],
) -> list[str]:
    """校验 Django system URLConf、AdminRouter 或 detail action 路由。"""
    route_tail = route.removeprefix("system/")
    normalized_tail = route_tail.rstrip("/")
    segments = [segment for segment in normalized_tail.split("/") if segment]
    if not segments:
        return [f"{contract.key}: Django system 路由路径为空"]

    resource = segments[0]
    if is_django_router_crud_route(resource, segments, routes):
        return []
    if normalized_tail in routes["system_explicit"]:
        return []
    if is_django_detail_action_route(resource, segments, routes):
        return []
    return [f"{contract.key}: Django system URLConf 未覆盖路径 {route_tail!r}"]


def is_django_router_crud_route(
    resource: str,
    segments: list[str],
    routes: dict[str, object],
) -> bool:
    """判断路径是否由 AdminRouter 的列表、详情或批量删除路由覆盖。"""
    registered = routes["system_router_resources"]
    if resource not in registered:
        return False
    if len(segments) == 1:
        return True
    if len(segments) == 2 and is_placeholder(segments[1]):
        return True
    return False


def is_django_detail_action_route(
    resource: str,
    segments: list[str],
    routes: dict[str, object],
) -> bool:
    """判断路径是否由 DRF detail @action 动态路由覆盖。"""
    if len(segments) != 3 or not is_placeholder(segments[1]):
        return False
    action_key = (resource, segments[2])
    return action_key in routes["system_detail_actions"]


def validate_fastapi_prefixed_route(
    contract: EndpointContract,
    routes: dict[str, str],
    prefix_name: str,
) -> list[str]:
    """校验 FastAPI v1 总入口包含指定一级 router。"""
    expected = f"{prefix_name}.router"
    if expected in routes["v1"]:
        return []
    return [f"{contract.key}: FastAPI v1 router 未 include {expected}"]


def load_django_routes(root: Path) -> dict[str, object]:
    """读取 Django OAuth/system 路由注册信息。"""
    oauth_text = read_text(root / "backend/drf_admin/apps/oauth/urls.py")
    system_text = read_text(root / "backend/drf_admin/apps/system/urls.py")
    role_view_text = read_text(root / "backend/drf_admin/apps/system/views/roles.py")
    return {
        "oauth_explicit": extract_django_path_routes(oauth_text),
        "system_explicit": extract_django_path_routes(system_text),
        "system_router_resources": extract_django_router_resources(system_text),
        "system_detail_actions": extract_django_detail_actions(role_view_text, resource="roles"),
    }


def load_fastapi_routes(root: Path) -> dict[str, str]:
    """读取 FastAPI v1 和 system router 入口文本。"""
    return {
        "v1": read_text(root / "fastapi/app/api/v1/__init__.py"),
        "system": read_text(root / "fastapi/app/api/v1/system/__init__.py"),
    }


def extract_django_path_routes(text: str) -> set[str]:
    """从 Django urls.py 文本中提取 path('...') 路由并统一占位符。"""
    routes: set[str] = set()
    for match in re.finditer(r"path\('([^']+)'", text):
        route = normalize_django_path(match.group(1))
        routes.add(route)
        if "{ids}" in route:
            routes.add(route.replace("{ids}", "{id}"))
    return routes


def extract_django_router_resources(text: str) -> set[str]:
    """从 AdminRouter.register 调用中提取资源前缀。"""
    return set(re.findall(r"router\.register\(r'([^']+)'", text))


def extract_django_detail_actions(text: str, resource: str) -> set[tuple[str, str]]:
    """从 DRF @action(detail=True, url_path='...') 中提取 detail action。"""
    actions: set[tuple[str, str]] = set()
    pattern = r"@action\(\s*detail=True,\s*methods=\[[^\]]+\],\s*url_path='([^']+)'"
    for match in re.finditer(pattern, text):
        actions.add((resource, match.group(1)))
    return actions


def normalize_django_path(route: str) -> str:
    """把 Django path converter 统一成端点契约的占位符风格。"""
    route = re.sub(r"<(?:int|str):pk>", "{id}", route)
    route = re.sub(r"<(?:int|str):id>", "{id}", route)
    route = re.sub(r"<str:ids>", "{ids}", route)
    route = re.sub(r"<int:days>", "{days}", route)
    return route.rstrip("/")


def normalized_contract_route(contract: EndpointContract) -> str:
    """去掉 /api/v1 前缀并统一路径尾部斜杠。"""
    return contract.path.removeprefix("/api/v1/").rstrip("/")


def is_placeholder(segment: str) -> bool:
    """判断路径片段是否为端点契约占位符。"""
    return segment.startswith("{") and segment.endswith("}")


def load_endpoint_contracts(root: Path) -> tuple[EndpointContract, ...]:
    """从仓库根目录加载端点契约目录。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_contracts import assert_endpoint_contract_catalog, iter_critical_endpoint_contracts

    assert_endpoint_contract_catalog()
    return iter_critical_endpoint_contracts()


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
