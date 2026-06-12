from __future__ import annotations

import sys
from pathlib import Path

from model_django_ast import load_django_field_metadata, load_django_model_tables


def validate_django_model_tables(root: Path) -> list[str]:
    """校验 Django 模型文件中的表名声明与共享模型契约一致。"""
    issues: list[str] = []
    tables = load_django_model_tables(root)
    for contract in load_django_model_table_contracts(root):
        actual_table = tables.get(contract.django_model)
        if actual_table is None:
            issues.append(f"backend/drf_admin/apps/system: 缺少模型 {contract.django_model}")
            continue
        if actual_table != contract.django_table:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model} 表名应为 "
                f"{contract.django_table}，实际为 {actual_table}"
            )
    return issues


def validate_django_field_metadata(root: Path) -> list[str]:
    """校验 Django 字段元数据与共享模型契约一致。"""
    issues: list[str] = []
    metadata_by_model = load_django_field_metadata(root)
    no_default = load_no_default(root)
    for contract in load_django_field_metadata_contracts(root):
        metadata = metadata_by_model.get(contract.django_model, {}).get(contract.field_name)
        if metadata is None:
            issues.append(f"backend/drf_admin/apps/system: {contract.django_model} 缺少字段 {contract.field_name}")
            continue
        if metadata.field_type != contract.field_type:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} 类型应为 "
                f"{contract.field_type}，实际为 {metadata.field_type}"
            )
        if metadata.null != contract.null:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} null 应为 "
                f"{contract.null}，实际为 {metadata.null}"
            )
        if contract.default is not no_default and metadata.default != contract.default:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} default 应为 "
                f"{contract.default!r}，实际为 {metadata.default!r}"
            )
    return issues


def validate_django_field_constraints(root: Path) -> list[str]:
    """校验 Django 字段约束与共享模型契约一致。"""
    issues: list[str] = []
    metadata_by_model = load_django_field_metadata(root)
    no_default = load_no_default(root)
    for contract in load_django_field_constraint_contracts(root):
        metadata = metadata_by_model.get(contract.django_model, {}).get(contract.field_name)
        if metadata is None:
            issues.append(f"backend/drf_admin/apps/system: {contract.django_model} 缺少字段 {contract.field_name}")
            continue
        if contract.max_length is not no_default and metadata.max_length != contract.max_length:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} max_length 应为 "
                f"{contract.max_length}，实际为 {metadata.max_length}"
            )
        if contract.unique is not no_default and metadata.unique != contract.unique:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} unique 应为 "
                f"{contract.unique}，实际为 {metadata.unique}"
            )
        if contract.index is not no_default and metadata.index != contract.index:
            issues.append(
                f"backend/drf_admin/apps/system: {contract.django_model}.{contract.field_name} index 应为 "
                f"{contract.index}，实际为 {metadata.index}"
            )
    return issues


def load_django_model_table_contracts(root: Path):
    """从共享模型契约加载 Django 模型表名契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_model_table_contracts

    return iter_django_model_table_contracts()


def load_django_field_metadata_contracts(root: Path):
    """从共享模型契约加载 Django 字段元数据契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_field_metadata_contracts

    return iter_django_field_metadata_contracts()


def load_django_field_constraint_contracts(root: Path):
    """从共享模型契约加载 Django 字段约束契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_field_constraint_contracts

    return iter_django_field_constraint_contracts()


def load_no_default(root: Path):
    """加载默认值跳过哨兵，保持校验脚本不复制契约细节。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import NO_DEFAULT

    return NO_DEFAULT
