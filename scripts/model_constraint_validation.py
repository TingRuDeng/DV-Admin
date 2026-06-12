from __future__ import annotations

import sys
from pathlib import Path

from model_contract_ast import load_fastapi_field_metadata


def validate_fastapi_field_constraints(root: Path) -> list[str]:
    """校验 FastAPI 字段长度、唯一性和索引与共享契约一致。"""
    issues: list[str] = []
    metadata_by_model = load_fastapi_field_metadata(root)
    no_default = load_no_default(root)
    for contract in load_field_constraint_contracts(root):
        metadata = metadata_by_model.get(contract.fastapi_model, {}).get(contract.field_name)
        if metadata is None:
            issues.append(f"fastapi/app/db/models: {contract.fastapi_model} 缺少字段 {contract.field_name}")
            continue
        if contract.max_length is not no_default and metadata.max_length != contract.max_length:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} max_length 应为 "
                f"{contract.max_length!r}，实际为 {metadata.max_length!r}"
            )
        if contract.unique is not no_default and metadata.unique != contract.unique:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} unique 应为 "
                f"{contract.unique!r}，实际为 {metadata.unique!r}"
            )
        if contract.index is not no_default and metadata.index != contract.index:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model}.{contract.field_name} index 应为 "
                f"{contract.index!r}，实际为 {metadata.index!r}"
            )
    return issues


def load_field_constraint_contracts(root: Path):
    """从共享模型契约加载 FastAPI 字段约束契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_fastapi_field_constraint_contracts

    return iter_fastapi_field_constraint_contracts()


def load_no_default(root: Path):
    """加载默认值跳过哨兵，保持校验脚本不复制契约细节。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import NO_DEFAULT

    return NO_DEFAULT
