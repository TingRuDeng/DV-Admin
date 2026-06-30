from pathlib import Path

from scripts.api_capability_contracts import (
    assert_api_capability_contract_catalog,
    iter_api_capability_contracts,
)


def test_fastapi_capability_contract_sources_exist():
    """若存在单后端独占能力契约，必须指向真实 FastAPI 源码与证据片段。"""
    assert_api_capability_contract_catalog()

    root = Path(__file__).resolve().parents[2]
    for contract in iter_api_capability_contracts():
        source = root / contract.fastapi_source
        assert source.exists(), f"{contract.key} 缺少 FastAPI 源文件: {contract.fastapi_source}"
        text = source.read_text(encoding="utf-8")
        for snippet in contract.fastapi_snippets:
            assert snippet in text, f"{contract.key} 缺少 FastAPI 证据片段: {snippet}"
