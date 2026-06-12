from __future__ import annotations

from dataclasses import dataclass

NO_DEFAULT = object()


@dataclass(frozen=True)
class FastapiFieldMetadataContract:
    """FastAPI 字段元数据契约，锁定关键字段类型、null 和 default。"""

    fastapi_model: str
    field_name: str
    field_type: str
    null: bool
    default: object = NO_DEFAULT


@dataclass(frozen=True)
class FastapiFieldConstraintContract:
    """FastAPI 字段约束契约，锁定长度、唯一性和索引声明。"""

    fastapi_model: str
    field_name: str
    max_length: object = NO_DEFAULT
    unique: object = NO_DEFAULT
    index: object = NO_DEFAULT


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
        field_name="code",
        field_type="CharField",
        null=False,
        default=None,
    ),
    FastapiFieldMetadataContract(
        fastapi_model="DictData",
        field_name="desc",
        field_type="CharField",
        null=False,
        default="",
    ),
)

FASTAPI_FIELD_CONSTRAINT_CONTRACTS: tuple[FastapiFieldConstraintContract, ...] = (
    FastapiFieldConstraintContract(
        fastapi_model="Permissions",
        field_name="name",
        max_length=30,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Permissions",
        field_name="route_path",
        max_length=200,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Permissions",
        field_name="perm",
        max_length=200,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Roles",
        field_name="name",
        max_length=32,
        unique=True,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="DictData",
        field_name="code",
        max_length=50,
        unique=True,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Users",
        field_name="username",
        max_length=150,
        unique=True,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Users",
        field_name="mobile",
        max_length=11,
        unique=True,
    ),
    FastapiFieldConstraintContract(
        fastapi_model="Users",
        field_name="email",
        max_length=254,
    ),
)


def iter_fastapi_field_metadata_contracts() -> tuple[FastapiFieldMetadataContract, ...]:
    """返回只读 FastAPI 字段元数据契约目录。"""
    return FASTAPI_FIELD_METADATA_CONTRACTS


def iter_fastapi_field_constraint_contracts() -> tuple[FastapiFieldConstraintContract, ...]:
    """返回只读 FastAPI 字段约束契约目录。"""
    return FASTAPI_FIELD_CONSTRAINT_CONTRACTS


def assert_field_contract_catalog() -> None:
    """校验字段契约目录自身完整，避免无效契约进入验证门禁。"""
    metadata_keys = {
        (contract.fastapi_model, contract.field_name)
        for contract in FASTAPI_FIELD_METADATA_CONTRACTS
    }
    constraint_keys = {
        (contract.fastapi_model, contract.field_name)
        for contract in FASTAPI_FIELD_CONSTRAINT_CONTRACTS
    }
    assert len(metadata_keys) == len(FASTAPI_FIELD_METADATA_CONTRACTS)
    assert len(constraint_keys) == len(FASTAPI_FIELD_CONSTRAINT_CONTRACTS)
    for contract in FASTAPI_FIELD_METADATA_CONTRACTS:
        assert contract.fastapi_model
        assert contract.field_name
        assert contract.field_type.endswith("Field")
    for contract in FASTAPI_FIELD_CONSTRAINT_CONTRACTS:
        assert contract.fastapi_model
        assert contract.field_name
        has_constraint = (
            contract.max_length is not NO_DEFAULT
            or contract.unique is not NO_DEFAULT
            or contract.index is not NO_DEFAULT
        )
        assert has_constraint
