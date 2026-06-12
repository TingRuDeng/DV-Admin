from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FastapiModelIndexContract:
    """FastAPI 模型索引契约，锁定 Meta.indexes 声明。"""

    fastapi_model: str
    indexes: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class FastapiUniqueTogetherContract:
    """FastAPI 模型唯一组合契约，锁定 Meta.unique_together 声明。"""

    fastapi_model: str
    fields: tuple[str, ...]


FASTAPI_MODEL_INDEX_CONTRACTS: tuple[FastapiModelIndexContract, ...] = (
    FastapiModelIndexContract(
        fastapi_model="Permissions",
        indexes=(
            ("type",),
            ("route_name",),
            ("visible",),
            ("parent_id", "sort"),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="Roles",
        indexes=(
            ("code",),
            ("status",),
            ("is_default",),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="Departments",
        indexes=(
            ("status",),
            ("parent_id", "sort"),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="Notices",
        indexes=(
            ("publish_status",),
            ("publisher_id",),
            ("publish_status", "publish_time"),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="DictData",
        indexes=(
            ("code",),
            ("status",),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="DictItems",
        indexes=(
            ("status",),
            ("dict_data_id", "sort"),
            ("dict_data_id", "status"),
        ),
    ),
    FastapiModelIndexContract(
        fastapi_model="Users",
        indexes=(
            ("username",),
            ("mobile",),
            ("email",),
            ("is_active",),
            ("dept_id", "is_active"),
        ),
    ),
)

FASTAPI_UNIQUE_TOGETHER_CONTRACTS: tuple[FastapiUniqueTogetherContract, ...] = (
    FastapiUniqueTogetherContract(
        fastapi_model="NoticeReads",
        fields=("notice", "user_id"),
    ),
)


def iter_fastapi_model_index_contracts() -> tuple[FastapiModelIndexContract, ...]:
    """返回只读 FastAPI 模型索引契约目录。"""
    return FASTAPI_MODEL_INDEX_CONTRACTS


def iter_fastapi_unique_together_contracts() -> tuple[FastapiUniqueTogetherContract, ...]:
    """返回只读 FastAPI 模型唯一组合契约目录。"""
    return FASTAPI_UNIQUE_TOGETHER_CONTRACTS


def assert_model_index_contract_catalog() -> None:
    """校验模型索引契约目录自身完整。"""
    model_names = {
        contract.fastapi_model
        for contract in FASTAPI_MODEL_INDEX_CONTRACTS
    }
    assert len(model_names) == len(FASTAPI_MODEL_INDEX_CONTRACTS)
    unique_model_names = {
        contract.fastapi_model
        for contract in FASTAPI_UNIQUE_TOGETHER_CONTRACTS
    }
    assert len(unique_model_names) == len(FASTAPI_UNIQUE_TOGETHER_CONTRACTS)
    for contract in FASTAPI_MODEL_INDEX_CONTRACTS:
        assert contract.fastapi_model
        assert contract.indexes
        for index_fields in contract.indexes:
            assert index_fields
            assert all(field_name for field_name in index_fields)
    for contract in FASTAPI_UNIQUE_TOGETHER_CONTRACTS:
        assert contract.fastapi_model
        assert contract.fields
        assert all(field_name for field_name in contract.fields)
