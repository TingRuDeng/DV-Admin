from __future__ import annotations

import sys
from pathlib import Path

from model_django_ast import load_django_model_tables


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


def load_django_model_table_contracts(root: Path):
    """从共享模型契约加载 Django 模型表名契约。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import iter_django_model_table_contracts

    return iter_django_model_table_contracts()
