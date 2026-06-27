from pathlib import Path

from scripts.api_capability_contracts import (
    assert_api_capability_contract_catalog,
    iter_api_capability_contracts,
)


def test_fastapi_log_capability_contract_sources_exist():
    """FastAPI 独占能力契约必须指向真实路由源码。"""
    assert_api_capability_contract_catalog()

    root = Path(__file__).resolve().parents[2]
    contracts = iter_api_capability_contracts()
    assert contracts
    for contract in contracts:
        source = root / contract.fastapi_source
        assert source.exists(), f"{contract.key} 缺少 FastAPI 源文件: {contract.fastapi_source}"
        text = source.read_text(encoding="utf-8")
        for snippet in contract.fastapi_snippets:
            assert snippet in text, f"{contract.key} 缺少 FastAPI 证据片段: {snippet}"
