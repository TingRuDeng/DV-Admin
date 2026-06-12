from __future__ import annotations

import ast
from pathlib import Path


DJANGO_MODEL_FILES = (
    "backend/drf_admin/apps/system/models.py",
    "backend/drf_admin/apps/system/models_notice.py",
)


def load_django_model_tables(root: Path) -> dict[str, str]:
    """静态读取 Django 模型 Meta.db_table 声明。"""
    tables: dict[str, str] = {}
    for rel in DJANGO_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        tables.update(extract_module_tables(module))
    return tables


def extract_module_tables(module: ast.Module) -> dict[str, str]:
    """提取单个 Django 模型模块内所有 class Meta.db_table。"""
    tables: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            table = extract_meta_db_table(node)
            if table:
                tables[f"system.{node.name.lower()}"] = table
    return tables


def extract_meta_db_table(model_node: ast.ClassDef) -> str:
    """从 Django 模型的内部 Meta 类提取 db_table 字面量。"""
    for child in model_node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            return extract_db_table_assignment(child)
    return ""


def extract_db_table_assignment(meta_node: ast.ClassDef) -> str:
    """读取 Meta.db_table = 'xxx' 形式的表名声明。"""
    for statement in meta_node.body:
        if isinstance(statement, ast.Assign) and is_db_table_target(statement.targets):
            if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
                return statement.value.value
    return ""


def is_db_table_target(targets: list[ast.expr]) -> bool:
    """判断赋值目标是否包含 db_table 字段。"""
    return any(isinstance(target, ast.Name) and target.id == "db_table" for target in targets)


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
