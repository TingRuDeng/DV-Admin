from scripts.api_capability_contracts import (
    assert_api_capability_contract_catalog,
    iter_api_capability_contracts,
)


def test_log_capabilities_are_no_longer_fastapi_only():
    """操作日志已在 Django 与 FastAPI 双实现，不得再登记为单后端独占能力。"""
    assert_api_capability_contract_catalog()

    contracts = iter_api_capability_contracts()
    keys = {contract.key for contract in contracts}
    assert not (
        keys
        & {
            "system_logs_page",
            "system_logs_visit_trend",
            "system_logs_visit_stats",
            "system_logs_delete",
            "system_logs_clear",
        }
    )
