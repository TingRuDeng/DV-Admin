from pathlib import Path

from scripts.api_endpoint_contract_types import EndpointContract
from scripts.api_route_coverage_validation import (
    extract_django_path_routes,
    validate_fastapi_contract_route,
)

ROOT = Path(__file__).resolve().parents[3]


def test_contract_entrypoint_validation_is_split_from_docs_cli():
    """文档契约入口校验必须独立维护，避免 validate_docs.py 保留项目分叉。"""
    entrypoint = read_text("scripts/validate_docs.py")
    assert "from docs_contract_validation import validate_contract_entrypoints" not in entrypoint
    assert "CONTRACT_REQUIRED_FILES =" not in entrypoint
    assert "PNPM_ACTION_SETUP_REQUIRED =" not in entrypoint
    assert "def validate_contract_entrypoints(" not in entrypoint
    assert (ROOT / "scripts/docs_contract_validation.py").exists()


def test_cross_document_fact_validation_is_split_from_docs_cli():
    """跨文档事实校验必须独立维护，避免 validate_docs.py 保留项目分叉。"""
    entrypoint = read_text("scripts/validate_docs.py")
    fact_validator = read_text("scripts/docs_fact_validation.py")
    assert "from docs_fact_validation import validate_doc_facts" not in entrypoint
    assert "validate_doc_facts(base)" not in entrypoint
    assert "FORBIDDEN_DOC_FACTS =" not in entrypoint
    assert "Django 当前只有文件日志中间件" in fact_validator
    assert "FastAPI 独占日志模型" in fact_validator


def test_api_route_coverage_validation_is_split_from_api_contract_cli():
    """API 路由覆盖校验必须独立维护，避免契约 CLI 继续膨胀。"""
    entrypoint = read_text("scripts/validate_api_contracts.py")
    assert "from scripts.api_route_coverage_validation import validate_route_coverage" in entrypoint
    assert "validate_route_coverage(root)" in entrypoint
    assert "DJANGO_ROUTER_RESOURCES" not in entrypoint
    assert (ROOT / "scripts/api_route_coverage_validation.py").exists()


def test_fastapi_route_coverage_requires_exact_endpoint_path():
    """FastAPI 覆盖校验不能只因为资源 router 已 include 就放过缺失子路由。"""
    contract = EndpointContract(
        key="roles_menu_assign",
        method="PUT",
        path="/api/v1/system/roles/{id}/menus/",
        auth_required=True,
    )
    routes = {"v1": "system.router", "system": 'prefix="/roles"', "fastapi_endpoints": set()}

    issues = validate_fastapi_contract_route(contract, routes)

    assert issues
    assert "roles_menu_assign" in issues[0]


def test_django_ids_to_id_alias_is_limited_to_notice_routes():
    """只有通知公告共用 ids 路由可兼容单 ID 契约，其他资源不能泛化。"""
    notice_routes = extract_django_path_routes("urlpatterns = [path('notices/<str:ids>', view)]")
    log_routes = extract_django_path_routes("urlpatterns = [path('logs/<str:ids>', view)]")

    assert "notices/{id}" in notice_routes
    assert "logs/{id}" not in log_routes


def read_text(relative_path: str) -> str:
    """读取仓库内文本文件。"""
    return (ROOT / relative_path).read_text(encoding="utf-8")
