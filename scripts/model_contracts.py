from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


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
        fastapi_table="system_dict_data",
        field_aliases=merged_aliases(
            COMMON_DJANGO_FIELD_ALIASES,
            {
                "dict_code": "code",
                "remark": "desc",
            },
        ),
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


def iter_django_fastapi_model_contracts() -> tuple[DjangoFastapiModelContract, ...]:
    """返回 Django 到 FastAPI 的只读模型契约目录。"""
    return DJANGO_FASTAPI_MODEL_CONTRACTS


def iter_fastapi_alias_targets() -> tuple[tuple[DjangoFastapiModelContract, tuple[str, ...]], ...]:
    """返回每个模型契约声明的 FastAPI 字段别名目标。"""
    return tuple(
        (contract, tuple(sorted(set(contract.field_aliases.values()))))
        for contract in DJANGO_FASTAPI_MODEL_CONTRACTS
    )


def assert_model_contract_catalog() -> None:
    """校验模型契约目录自身完整，避免无效契约进入验证门禁。"""
    django_models = {contract.django_model for contract in DJANGO_FASTAPI_MODEL_CONTRACTS}
    assert len(django_models) == len(DJANGO_FASTAPI_MODEL_CONTRACTS)
    assert "system.dicts" in django_models
    assert "system.dictitems" in django_models
    for contract in DJANGO_FASTAPI_MODEL_CONTRACTS:
        assert contract.django_model.startswith("system.")
        assert contract.fastapi_model
        assert contract.django_table.startswith("system_")
        assert contract.fastapi_table.startswith("system_")
