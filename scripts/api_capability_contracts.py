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

# 操作日志已在 Django 与 FastAPI 双实现，不再属于单后端独占能力，目录暂为空。
# 该机制保留用于登记未来可能出现的单后端独占 API 能力。
API_CAPABILITY_CONTRACTS: tuple[ApiCapabilityContract, ...] = ()


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
