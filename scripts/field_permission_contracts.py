from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldPermissionContract:
    """字段级权限码目录，确保运行时校验的权限可在角色权限树中分配。"""

    key: str
    name: str
    perm: str
    parent_pk: int
    django_source: str
    fastapi_source: str


FIELD_PERMISSION_CONTRACTS: tuple[FieldPermissionContract, ...] = (
    FieldPermissionContract(
        key="user_field_plain",
        name="用户敏感字段原文读取",
        perm="system:users:field:plain",
        parent_pk=2,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
    FieldPermissionContract(
        key="user_field_write",
        name="用户敏感字段写入",
        perm="system:users:field:write",
        parent_pk=2,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
    FieldPermissionContract(
        key="log_field_plain",
        name="日志敏感字段原文读取",
        perm="system:logs:field:plain",
        parent_pk=181,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
    FieldPermissionContract(
        key="notice_target_write",
        name="通知目标字段写入",
        perm="system:notices:target:write",
        parent_pk=184,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
    FieldPermissionContract(
        key="notice_target_plain",
        name="通知目标字段原文读取",
        perm="system:notices:target:plain",
        parent_pk=184,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
    FieldPermissionContract(
        key="notice_content_plain",
        name="通知正文字段原文读取",
        perm="system:notices:content:plain",
        parent_pk=184,
        django_source="backend/drf_admin/apps/system/services/field_permission.py",
        fastapi_source="fastapi/app/services/system/field_permission.py",
    ),
)


def iter_field_permission_contracts() -> tuple[FieldPermissionContract, ...]:
    """返回字段权限码契约目录。"""
    return FIELD_PERMISSION_CONTRACTS


def assert_field_permission_contract_catalog() -> None:
    """校验字段权限码契约目录自身一致性。"""
    keys = {contract.key for contract in FIELD_PERMISSION_CONTRACTS}
    perms = {contract.perm for contract in FIELD_PERMISSION_CONTRACTS}
    assert len(keys) == len(FIELD_PERMISSION_CONTRACTS)
    assert len(perms) == len(FIELD_PERMISSION_CONTRACTS)
    for contract in FIELD_PERMISSION_CONTRACTS:
        _assert_field_permission_contract(contract)


def _assert_field_permission_contract(contract: FieldPermissionContract) -> None:
    """校验单个字段权限码契约的基础结构。"""
    assert contract.key
    assert contract.name
    assert contract.perm.startswith("system:")
    assert contract.parent_pk > 0
    assert contract.django_source.endswith("field_permission.py")
    assert contract.fastapi_source.endswith("field_permission.py")
