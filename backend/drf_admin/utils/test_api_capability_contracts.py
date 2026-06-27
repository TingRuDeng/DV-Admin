from scripts.api_capability_contracts import (
    assert_api_capability_contract_catalog,
    iter_api_capability_contracts,
)


def test_django_absent_log_capabilities_stay_marked_fastapi_only():
    """Django 未实现日志管理路由时，操作日志能力必须保持 FastAPI 独占登记。"""
    assert_api_capability_contract_catalog()

    contracts = iter_api_capability_contracts()
    assert {contract.owner_backend for contract in contracts} == {"FastAPI"}
    assert {contract.key for contract in contracts} >= {
        "system_logs_page",
        "system_logs_visit_trend",
        "system_logs_visit_stats",
        "system_logs_delete",
        "system_logs_clear",
    }
    assert all("OperationLog" in contract.reason for contract in contracts)
