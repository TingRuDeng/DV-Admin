from __future__ import annotations

from dataclasses import dataclass

from scripts.model_contract_sentinel import NO_DEFAULT


@dataclass(frozen=True)
class FastapiFieldConstraintContract:
    """FastAPI 字段约束契约，锁定长度、唯一性和索引声明。"""

    fastapi_model: str
    field_name: str
    max_length: object = NO_DEFAULT
    unique: object = NO_DEFAULT
    index: object = NO_DEFAULT


@dataclass(frozen=True)
class DjangoFieldConstraintContract:
    """Django 字段约束契约，锁定长度、唯一性和索引声明。"""

    django_model: str
    field_name: str
    max_length: object = NO_DEFAULT
    unique: object = NO_DEFAULT
    index: object = NO_DEFAULT


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
        field_name="dict_code",
        max_length=32,
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

DJANGO_FIELD_CONSTRAINT_CONTRACTS: tuple[DjangoFieldConstraintContract, ...] = (
    DjangoFieldConstraintContract(
        django_model="system.permissions",
        field_name="name",
        max_length=30,
    ),
    DjangoFieldConstraintContract(
        django_model="system.permissions",
        field_name="route_path",
        max_length=200,
    ),
    DjangoFieldConstraintContract(
        django_model="system.permissions",
        field_name="perm",
        max_length=200,
    ),
    DjangoFieldConstraintContract(
        django_model="system.roles",
        field_name="name",
        max_length=32,
        unique=True,
    ),
    DjangoFieldConstraintContract(
        django_model="system.dicts",
        field_name="dict_code",
        max_length=32,
        unique=True,
    ),
    DjangoFieldConstraintContract(
        django_model="system.users",
        field_name="username",
        max_length=150,
        unique=True,
    ),
    DjangoFieldConstraintContract(
        django_model="system.users",
        field_name="mobile",
        max_length=11,
        unique=True,
    ),
    DjangoFieldConstraintContract(
        django_model="system.users",
        field_name="email",
        max_length=254,
    ),
)


def iter_fastapi_field_constraint_contracts() -> tuple[FastapiFieldConstraintContract, ...]:
    """返回只读 FastAPI 字段约束契约目录。"""
    return FASTAPI_FIELD_CONSTRAINT_CONTRACTS


def iter_django_field_constraint_contracts() -> tuple[DjangoFieldConstraintContract, ...]:
    """返回只读 Django 字段约束契约目录。"""
    return DJANGO_FIELD_CONSTRAINT_CONTRACTS


def assert_field_constraint_contract_catalog() -> None:
    """校验字段约束契约目录自身完整。"""
    constraint_keys = {
        (contract.fastapi_model, contract.field_name)
        for contract in FASTAPI_FIELD_CONSTRAINT_CONTRACTS
    }
    django_constraint_keys = {
        (contract.django_model, contract.field_name)
        for contract in DJANGO_FIELD_CONSTRAINT_CONTRACTS
    }
    assert len(constraint_keys) == len(FASTAPI_FIELD_CONSTRAINT_CONTRACTS)
    assert len(django_constraint_keys) == len(DJANGO_FIELD_CONSTRAINT_CONTRACTS)
    for contract in FASTAPI_FIELD_CONSTRAINT_CONTRACTS:
        assert contract.fastapi_model
        assert contract.field_name
        assert has_field_constraint(contract)
    for contract in DJANGO_FIELD_CONSTRAINT_CONTRACTS:
        assert contract.django_model.startswith("system.")
        assert contract.field_name
        assert has_field_constraint(contract)


def has_field_constraint(contract) -> bool:
    """判断字段约束契约至少声明一种约束。"""
    return (
        contract.max_length is not NO_DEFAULT
        or contract.unique is not NO_DEFAULT
        or contract.index is not NO_DEFAULT
    )
