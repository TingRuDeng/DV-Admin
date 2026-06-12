from __future__ import annotations

import sys
from pathlib import Path

from model_contract_ast import (
    load_fastapi_field_metadata,
    load_fastapi_model_fields,
    load_fastapi_model_tables,
    load_fastapi_relation_through_tables,
)


def validate_fastapi_model_tables(root: Path) -> list[str]:
    """校验 FastAPI 模型文件中的表名声明与共享模型契约一致。"""
    issues: list[str] = []
    contracts = load_contracts(root)
    tables = load_fastapi_model_tables(root)
    for contract in contracts:
        actual_table = tables.get(contract.fastapi_model)
        if actual_table is None:
            issues.append(f"fastapi/app/db/models: 缺少模型 {contract.fastapi_model}")
            continue
        if actual_table != contract.fastapi_table:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model} 表名应为 {contract.fastapi_table}，实际为 {actual_table}"
            )
    return issues


def validate_fastapi_alias_target_fields(root: Path) -> list[str]:
    """校验字段别名目标真实存在于对应 FastAPI 模型。"""
    issues: list[str] = []
    model_fields = load_fastapi_model_fields(root)
    base_fields = model_fields.get("BaseModel", set())
    for contract, target_fields in load_alias_targets(root):
        actual_fields = base_fields | model_fields.get(contract.fastapi_model, set())
        for field_name in target_fields:
            if field_name not in actual_fields:
                issues.append(f"fastapi/app/db/models: {contract.fastapi_model} 缺少字段 {field_name}")
    return issues


def validate_fastapi_relation_through_tables(root: Path) -> list[str]:
    """校验 FastAPI 多对多关联字段的 through 表与共享契约一致。"""
    issues: list[str] = []
    through_tables = load_fastapi_relation_through_tables(root)
    for contract in load_relation_contracts(root):
        model_relations = through_tables.get(contract.fastapi_model, {})
        actual_table = model_relations.get(contract.fastapi_field)
        if actual_table is None:
            issues.append(f"fastapi/app/db/models: {contract.fastapi_model} 缺少关联字段 {contract.fastapi_field}")
            continue
        if actual_table != contract.fastapi_through_table:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.fastapi_field} through 表应为 "
                f"{contract.fastapi_through_table}，实际为 {actual_table}"
            )
    return issues


def validate_fastapi_field_metadata(root: Path) -> list[str]:
    """校验 FastAPI 字段元数据与共享契约一致。"""
    issues: list[str] = []
    metadata_by_model = load_fastapi_field_metadata(root)
    no_default = load_no_default(root)
    for contract in load_field_metadata_contracts(root):
        metadata = metadata_by_model.get(contract.fastapi_model, {}).get(contract.field_name)
        if metadata is None:
            issues.append(f"fastapi/app/db/models: {contract.fastapi_model} 缺少字段 {contract.field_name}")
            continue
        if metadata.field_type != contract.field_type:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} 类型应为 "
                f"{contract.field_type}，实际为 {metadata.field_type}"
            )
        if metadata.null != contract.null:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} null 应为 "
                f"{contract.null}，实际为 {metadata.null}"
            )
        if contract.default is not no_default and metadata.default != contract.default:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} default 应为 "
                f"{contract.default!r}，实际为 {metadata.default!r}"
            )
    return issues


def load_contracts(root: Path):
    """从仓库根目录加载模型契约，避免脚本工作目录影响 import。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_fastapi_model_contracts

    return iter_django_fastapi_model_contracts()


def load_alias_targets(root: Path):
    """从共享模型契约加载 FastAPI 字段别名目标。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_fastapi_alias_targets

    return iter_fastapi_alias_targets()


def load_relation_contracts(root: Path):
    """从共享模型契约加载 Django/FastAPI 多对多关联表契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_fastapi_relation_contracts

    return iter_django_fastapi_relation_contracts()


def load_field_metadata_contracts(root: Path):
    """从共享模型契约加载 FastAPI 字段元数据契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_fastapi_field_metadata_contracts

    return iter_fastapi_field_metadata_contracts()


def load_no_default(root: Path):
    """加载默认值跳过哨兵，保持校验脚本不复制契约细节。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import NO_DEFAULT

    return NO_DEFAULT
