from __future__ import annotations

import sys
from pathlib import Path

from model_index_ast import load_fastapi_model_indexes


def validate_fastapi_model_indexes(root: Path) -> list[str]:
    """校验 FastAPI 模型 Meta.indexes 与共享契约一致。"""
    issues: list[str] = []
    indexes_by_model = load_fastapi_model_indexes(root)
    for contract in load_model_index_contracts(root):
        actual_indexes = indexes_by_model.get(contract.fastapi_model)
        if actual_indexes is None:
            issues.append(f"fastapi/app/db/models: {contract.fastapi_model} 缺少 Meta.indexes")
            continue
        if actual_indexes != contract.indexes:
            issues.append(
                f"fastapi/app/db/models: {contract.fastapi_model} indexes 应为 "
                f"{contract.indexes!r}，实际为 {actual_indexes!r}"
            )
    return issues


def load_model_index_contracts(root: Path):
    """从共享模型契约加载 FastAPI 模型索引契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_fastapi_model_index_contracts

    return iter_fastapi_model_index_contracts()
