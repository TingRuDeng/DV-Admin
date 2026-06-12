from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from scripts.model_field_contracts import (
    NO_DEFAULT,
    assert_field_contract_catalog,
    iter_django_field_constraint_contracts,
    iter_django_field_metadata_contracts,
    iter_fastapi_field_constraint_contracts,
    iter_fastapi_field_metadata_contracts,
)
from scripts.model_index_contracts import (
    assert_model_index_contract_catalog,
    iter_fastapi_model_index_contracts,
    iter_fastapi_unique_together_contracts,
)


COMMON_DJANGO_FIELD_ALIASES = MappingProxyType(
    {
        "create_time": "created_at",
        "update_time": "updated_at",
    }
)


@dataclass(frozen=True)
class DjangoFastapiModelContract:
    """Django 到 FastAPI 的模型映射契约，集中声明迁移边界差异。"""

    django_model: str
    fastapi_model: str
    django_table: str
    fastapi_table: str
    field_aliases: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DjangoFastapiRelationContract:
    """Django 到 FastAPI 的多对多关联表契约，集中声明 through 表差异。"""

    django_model: str
    django_field: str
    django_through_table: str
    fastapi_model: str
    fastapi_field: str
    fastapi_through_table: str


def merged_aliases(*aliases: Mapping[str, str]) -> Mapping[str, str]:
    """合并字段别名，返回只读映射，避免调用方修改共享契约。"""
    result: dict[str, str] = {}
    for alias in aliases:
        result.update(alias)
    return MappingProxyType(result)


DJANGO_FASTAPI_MODEL_CONTRACTS: tuple[DjangoFastapiModelContract, ...] = (
    DjangoFastapiModelContract(
        django_model="system.departments",
        fastapi_model="Departments",
        django_table="system_departments",
        fastapi_table="system_departments",
        field_aliases=COMMON_DJANGO_FIELD_ALIASES,
    ),
    DjangoFastapiModelContract(
        django_model="system.permissions",
        fastapi_model="Permissions",
        django_table="system_permissions",
        fastapi_table="system_permissions",
        field_aliases=merged_aliases(
            COMMON_DJANGO_FIELD_ALIASES,
            {
                "keepAlive": "keep_alive",
                "alwaysShow": "always_show",
            },
        ),
    ),
    DjangoFastapiModelContract(
        django_model="system.roles",
        fastapi_model="Roles",
        django_table="system_roles",
        fastapi_table="system_roles",
        field_aliases=COMMON_DJANGO_FIELD_ALIASES,
    ),
    DjangoFastapiModelContract(
        django_model="system.users",
        fastapi_model="Users",
        django_table="system_users",
        fastapi_table="system_users",
        field_aliases=COMMON_DJANGO_FIELD_ALIASES,
    ),
    DjangoFastapiModelContract(
        django_model="system.dicts",
        fastapi_model="DictData",
        django_table="system_dicts",
        fastapi_table="system_dicts",
        field_aliases=COMMON_DJANGO_FIELD_ALIASES,
    ),
    DjangoFastapiModelContract(
        django_model="system.dictitems",
        fastapi_model="DictItems",
        django_table="system_dict_items",
        fastapi_table="system_dict_items",
        field_aliases=merged_aliases(
            COMMON_DJANGO_FIELD_ALIASES,
            {
                "dict": "dict_data",
            },
        ),
    ),
    DjangoFastapiModelContract(
        django_model="system.notices",
        fastapi_model="Notices",
        django_table="system_notices",
        fastapi_table="system_notices",
        field_aliases=COMMON_DJANGO_FIELD_ALIASES,
    ),
)

DJANGO_FASTAPI_RELATION_CONTRACTS: tuple[DjangoFastapiRelationContract, ...] = (
    DjangoFastapiRelationContract(
        django_model="system.roles",
        django_field="permissions",
        django_through_table="system_roles_to_system_permissions",
        fastapi_model="Roles",
        fastapi_field="permissions",
        fastapi_through_table="system_roles_permissions",
    ),
    DjangoFastapiRelationContract(
        django_model="system.users",
        django_field="roles",
        django_through_table="system_users_to_system_roles",
        fastapi_model="Users",
        fastapi_field="roles",
        fastapi_through_table="system_users_roles",
    ),
)

def iter_django_fastapi_model_contracts() -> tuple[DjangoFastapiModelContract, ...]:
    """返回 Django 到 FastAPI 的只读模型契约目录。"""
    return DJANGO_FASTAPI_MODEL_CONTRACTS


def iter_django_model_table_contracts() -> tuple[DjangoFastapiModelContract, ...]:
    """返回只读 Django 模型表名契约目录。"""
    return DJANGO_FASTAPI_MODEL_CONTRACTS


def iter_fastapi_alias_targets() -> tuple[tuple[DjangoFastapiModelContract, tuple[str, ...]], ...]:
    """返回每个模型契约声明的 FastAPI 字段别名目标。"""
    return tuple(
        (contract, tuple(sorted(set(contract.field_aliases.values()))))
        for contract in DJANGO_FASTAPI_MODEL_CONTRACTS
    )


def iter_django_fastapi_relation_contracts() -> tuple[DjangoFastapiRelationContract, ...]:
    """返回 Django 到 FastAPI 的只读多对多关联表契约目录。"""
    return DJANGO_FASTAPI_RELATION_CONTRACTS


def iter_django_relation_through_contracts() -> tuple[DjangoFastapiRelationContract, ...]:
    """返回只读 Django 多对多 through 表契约目录。"""
    return DJANGO_FASTAPI_RELATION_CONTRACTS


def assert_model_contract_catalog() -> None:
    """校验模型契约目录自身完整，避免无效契约进入验证门禁。"""
    django_models = {contract.django_model for contract in DJANGO_FASTAPI_MODEL_CONTRACTS}
    assert len(django_models) == len(DJANGO_FASTAPI_MODEL_CONTRACTS)
    assert "system.dicts" in django_models
    assert "system.dictitems" in django_models
    relation_keys = {
        (contract.django_model, contract.django_field)
        for contract in DJANGO_FASTAPI_RELATION_CONTRACTS
    }
    assert len(relation_keys) == len(DJANGO_FASTAPI_RELATION_CONTRACTS)
    assert_field_contract_catalog()
    assert_model_index_contract_catalog()
    for contract in DJANGO_FASTAPI_MODEL_CONTRACTS:
        assert contract.django_model.startswith("system.")
        assert contract.fastapi_model
        assert contract.django_table.startswith("system_")
        assert contract.fastapi_table.startswith("system_")
    for contract in DJANGO_FASTAPI_RELATION_CONTRACTS:
        assert contract.django_model.startswith("system.")
        assert contract.django_field
        assert contract.django_through_table.startswith("system_")
        assert contract.fastapi_model
        assert contract.fastapi_field
        assert contract.fastapi_through_table.startswith("system_")
