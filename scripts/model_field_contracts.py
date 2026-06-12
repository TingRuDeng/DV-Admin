from __future__ import annotations

from dataclasses import dataclass

from scripts.model_contract_sentinel import NO_DEFAULT
from scripts.model_field_constraint_contracts import (
    assert_field_constraint_contract_catalog,
    iter_django_field_constraint_contracts,
    iter_fastapi_field_constraint_contracts,
)


@dataclass(frozen=True)
class FastapiFieldMetadataContract:
    """FastAPI 字段元数据契约，锁定关键字段类型、null 和 default。"""

    fastapi_model: str
    field_name: str
    field_type: str
    null: bool
    default: object = NO_DEFAULT


@dataclass(frozen=True)
class DjangoFieldMetadataContract:
    """Django 字段元数据契约，锁定关键字段类型、null 和 default。"""

    django_model: str
    field_name: str
    field_type: str
    null: bool
    default: object = NO_DEFAULT


FASTAPI_FIELD_METADATA_CONTRACTS: tuple[FastapiFieldMetadataContract, ...] = (
    FastapiFieldMetadataContract(
        fastapi_model="BaseModel",
        field_name="created_at",
        field_type="DatetimeField",
        null=False,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="BaseModel",
        field_name="updated_at",
        field_type="DatetimeField",
        null=False,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="Permissions",
        field_name="keep_alive",
        field_type="BooleanField",
        null=True,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="Permissions",
        field_name="always_show",
        field_type="BooleanField",
        null=True,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="DictData",
        field_name="dict_code",
        field_type="CharField",
        null=False,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="DictData",
        field_name="remark",
        field_type="CharField",
        null=False,
        default="",
    ),
)

DJANGO_FIELD_METADATA_CONTRACTS: tuple[DjangoFieldMetadataContract, ...] = (
    DjangoFieldMetadataContract(
        django_model="system.permissions",
        field_name="keepAlive",
        field_type="BooleanField",
        null=True,
    ),
    DjangoFieldMetadataContract(
        django_model="system.permissions",
        field_name="alwaysShow",
        field_type="BooleanField",
        null=True,
    ),
    DjangoFieldMetadataContract(
        django_model="system.dicts",
        field_name="dict_code",
        field_type="CharField",
        null=False,
    ),
    DjangoFieldMetadataContract(
        django_model="system.dicts",
        field_name="remark",
        field_type="CharField",
        null=False,
        default="",
    ),
)

def iter_fastapi_field_metadata_contracts() -> tuple[FastapiFieldMetadataContract, ...]:
    """返回只读 FastAPI 字段元数据契约目录。"""
    return FASTAPI_FIELD_METADATA_CONTRACTS


def iter_django_field_metadata_contracts() -> tuple[DjangoFieldMetadataContract, ...]:
    """返回只读 Django 字段元数据契约目录。"""
    return DJANGO_FIELD_METADATA_CONTRACTS


def assert_field_contract_catalog() -> None:
    """校验字段契约目录自身完整，避免无效契约进入验证门禁。"""
    metadata_keys = {
        (contract.fastapi_model, contract.field_name)
        for contract in FASTAPI_FIELD_METADATA_CONTRACTS
    }
    django_metadata_keys = {
        (contract.django_model, contract.field_name)
        for contract in DJANGO_FIELD_METADATA_CONTRACTS
    }
    assert len(metadata_keys) == len(FASTAPI_FIELD_METADATA_CONTRACTS)
    assert len(django_metadata_keys) == len(DJANGO_FIELD_METADATA_CONTRACTS)
    assert_field_constraint_contract_catalog()
    for contract in FASTAPI_FIELD_METADATA_CONTRACTS:
        assert contract.fastapi_model
        assert contract.field_name
        assert contract.field_type.endswith("Field")
    for contract in DJANGO_FIELD_METADATA_CONTRACTS:
        assert contract.django_model.startswith("system.")
        assert contract.field_name
        assert contract.field_type.endswith("Field")
