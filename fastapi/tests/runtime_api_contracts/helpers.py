"""FastAPI 运行时 API 契约测试共享工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from scripts.api_contracts import (
    assert_page_payload,
    assert_success_envelope,
    iter_critical_endpoint_contracts,
)

HTTP_OK = 200
PAGE_SIZE_SAMPLE = 1
READ_SAMPLE_KEYS = (
    "auth_info",
    "auth_routes",
    "users_page",
    "roles_page",
    "depts_tree",
    "menus_tree",
    "dicts_page",
    "dict_items_page",
    "notices_page",
    "logs_page",
)
USER_WRITE_SAMPLE_KEYS = ("users_create", "users_update", "users_delete")
ROLE_WRITE_SAMPLE_KEYS = ("roles_create", "roles_update", "roles_delete", "roles_menu_assign")
DEPT_WRITE_SAMPLE_KEYS = ("depts_create", "depts_update", "depts_delete")
MENU_WRITE_SAMPLE_KEYS = ("menus_create", "menus_update", "menus_delete")
DICT_WRITE_SAMPLE_KEYS = ("dicts_create", "dicts_update", "dicts_delete")
DICT_ITEM_WRITE_SAMPLE_KEYS = ("dict_items_create", "dict_items_update", "dict_items_delete")
NOTICE_WRITE_SAMPLE_KEYS = (
    "notices_create",
    "notices_update",
    "notices_delete",
    "notices_publish",
    "notices_revoke",
)


@dataclass(frozen=True)
class UserWriteContext:
    """用户写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]
    role_id: int
    role_name: str
    dept_id: int


@dataclass(frozen=True)
class RoleWriteContext:
    """角色写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]
    permission_id: int


@dataclass(frozen=True)
class SimpleWriteContext:
    """无需额外依赖的写接口运行时契约上下文。"""

    client: Any
    contracts: dict[str, Any]


def contracts_by_key() -> dict[str, Any]:
    """按 key 索引关键端点契约，避免测试重复维护端点清单细节。"""
    return {contract.key: contract for contract in iter_critical_endpoint_contracts()}


def assert_success_payload(response, contract) -> Any:
    """断言运行时响应满足 FastAPI 成功信封，并返回 data 载荷。"""
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert_success_envelope(payload, backend="fastapi")
    data = payload["data"]
    if contract.paginated:
        assert_page_payload(data)
    return data


def assert_response_fields(data: Any, fields: tuple[str, ...]) -> None:
    """抽样检查响应关键字段，空列表仅验证外层结构。"""
    if isinstance(data, Mapping):
        for field in fields:
            assert field in data
        return
    if isinstance(data, list) and data:
        for field in fields:
            assert field in data[0]


def sample_query_params(contract) -> dict[str, Any]:
    """按前端共享契约构造查询参数，避免误用后端私有参数名。"""
    params: dict[str, Any] = {}
    if "pageNum" in contract.query_params:
        params["pageNum"] = 1
    if "pageSize" in contract.query_params:
        params["pageSize"] = PAGE_SIZE_SAMPLE
    return params
