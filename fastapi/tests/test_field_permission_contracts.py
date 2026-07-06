from pathlib import Path

from scripts.field_permission_contract_validation import validate_field_permission_contracts
from scripts.field_permission_contracts import (
    assert_field_permission_contract_catalog,
    iter_field_permission_contracts,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_field_permission_contract_catalog_lists_enforced_codes():
    """字段权限码目录必须覆盖当前已接入的字段级权限。"""
    assert_field_permission_contract_catalog()
    codes = {contract.perm for contract in iter_field_permission_contracts()}

    assert "system:users:field:plain" in codes
    assert "system:users:field:write" in codes
    assert "system:logs:field:plain" in codes
    assert "system:notices:target:write" in codes
    assert "system:notices:target:plain" in codes
    assert "system:notices:content:plain" in codes


def test_field_permission_contracts_match_seed_and_fixture_catalogs():
    """运行时字段权限必须能在权限目录中被授予。"""
    assert validate_field_permission_contracts(PROJECT_ROOT) == []
