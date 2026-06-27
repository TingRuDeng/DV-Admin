from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiCapabilityContract:
    """描述单后端独占 API 能力边界。"""

    key: str
    method: str
    path: str
    owner_backend: str
    reason: str
    fastapi_source: str
    fastapi_snippets: frozenset[str]
    django_absent_source: str
    django_forbidden_snippets: frozenset[str]


LOG_CAPABILITY_REASON = "Django 当前只有文件日志中间件，没有可查询 OperationLog 模型或日志管理 API。"


API_CAPABILITY_CONTRACTS: tuple[ApiCapabilityContract, ...] = (
    ApiCapabilityContract(
        key="system_logs_page",
        method="GET",
        path="/api/v1/system/logs/page",
        owner_backend="FastAPI",
        reason=LOG_CAPABILITY_REASON,
        fastapi_source="fastapi/app/api/v1/system/log_routes/query.py",
        fastapi_snippets=frozenset(("@router.get(", '"/page"', "system:logs:query")),
        django_absent_source="backend/drf_admin/apps/system/urls.py",
        django_forbidden_snippets=frozenset(("logs", "system/logs")),
    ),
    ApiCapabilityContract(
        key="system_logs_visit_trend",
        method="GET",
        path="/api/v1/system/logs/visit-trend",
        owner_backend="FastAPI",
        reason=LOG_CAPABILITY_REASON,
        fastapi_source="fastapi/app/api/v1/system/log_routes/analytics.py",
        fastapi_snippets=frozenset(("@router.get(", '"/visit-trend"', "system:logs:query")),
        django_absent_source="backend/drf_admin/apps/system/urls.py",
        django_forbidden_snippets=frozenset(("logs", "system/logs")),
    ),
    ApiCapabilityContract(
        key="system_logs_visit_stats",
        method="GET",
        path="/api/v1/system/logs/visit-stats",
        owner_backend="FastAPI",
        reason=LOG_CAPABILITY_REASON,
        fastapi_source="fastapi/app/api/v1/system/log_routes/analytics.py",
        fastapi_snippets=frozenset(("@router.get(", '"/visit-stats"', "system:logs:query")),
        django_absent_source="backend/drf_admin/apps/system/urls.py",
        django_forbidden_snippets=frozenset(("logs", "system/logs")),
    ),
    ApiCapabilityContract(
        key="system_logs_delete",
        method="DELETE",
        path="/api/v1/system/logs/{ids}",
        owner_backend="FastAPI",
        reason=LOG_CAPABILITY_REASON,
        fastapi_source="fastapi/app/api/v1/system/log_routes/mutation.py",
        fastapi_snippets=frozenset(("@router.delete(", '"/{ids}"', "system:logs:delete")),
        django_absent_source="backend/drf_admin/apps/system/urls.py",
        django_forbidden_snippets=frozenset(("logs", "system/logs")),
    ),
    ApiCapabilityContract(
        key="system_logs_clear",
        method="DELETE",
        path="/api/v1/system/logs/clear/{days}",
        owner_backend="FastAPI",
        reason=LOG_CAPABILITY_REASON,
        fastapi_source="fastapi/app/api/v1/system/log_routes/mutation.py",
        fastapi_snippets=frozenset(("@router.delete(", '"/clear/{days}"', "system:logs:delete")),
        django_absent_source="backend/drf_admin/apps/system/urls.py",
        django_forbidden_snippets=frozenset(("logs", "system/logs")),
    ),
)


def iter_api_capability_contracts() -> tuple[ApiCapabilityContract, ...]:
    """返回不可变 API 能力边界契约目录。"""
    return API_CAPABILITY_CONTRACTS


def assert_api_capability_contract_catalog() -> None:
    """校验能力边界契约目录自身一致性。"""
    keys = {contract.key for contract in API_CAPABILITY_CONTRACTS}
    assert len(keys) == len(API_CAPABILITY_CONTRACTS)
    for contract in API_CAPABILITY_CONTRACTS:
        _assert_api_capability_contract(contract)


def _assert_api_capability_contract(contract: ApiCapabilityContract) -> None:
    """校验单个能力边界契约的基础结构。"""
    assert contract.key
    assert contract.method in {"GET", "POST", "PUT", "DELETE", "PATCH"}
    assert contract.path.startswith("/api/v1/")
    assert contract.owner_backend == "FastAPI"
    assert contract.reason
    assert contract.fastapi_source
    assert contract.fastapi_snippets
    assert contract.django_absent_source
    assert contract.django_forbidden_snippets
