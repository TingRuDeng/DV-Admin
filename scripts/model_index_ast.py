from __future__ import annotations

import ast
from pathlib import Path

from model_contract_ast import FASTAPI_MODEL_FILES, read_text


def load_fastapi_model_indexes(root: Path) -> dict[str, tuple[tuple[str, ...], ...]]:
    """静态读取 FastAPI 模型 Meta.indexes 声明。"""
    indexes: dict[str, tuple[tuple[str, ...], ...]] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        indexes.update(extract_module_indexes(module))
    return indexes


def extract_module_indexes(module: ast.Module) -> dict[str, tuple[tuple[str, ...], ...]]:
    """提取单个 FastAPI 模型模块内所有 class Meta.indexes。"""
    indexes_by_model: dict[str, tuple[tuple[str, ...], ...]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            indexes = extract_meta_indexes(node)
            if indexes:
                indexes_by_model[node.name] = indexes
    return indexes_by_model


def extract_meta_indexes(model_node: ast.ClassDef) -> tuple[tuple[str, ...], ...]:
    """从 Tortoise 模型的内部 Meta 类提取 indexes 字面量。"""
    for child in model_node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            return extract_indexes_assignment(child)
    return ()


def extract_indexes_assignment(meta_node: ast.ClassDef) -> tuple[tuple[str, ...], ...]:
    """读取 Meta.indexes = ((...), ...) 形式的索引声明。"""
    for statement in meta_node.body:
        if isinstance(statement, ast.Assign) and is_indexes_target(statement.targets):
            return extract_indexes_tuple(statement.value)
    return ()


def is_indexes_target(targets: list[ast.expr]) -> bool:
    """判断赋值目标是否包含 indexes 字段。"""
    return any(isinstance(target, ast.Name) and target.id == "indexes" for target in targets)


def extract_indexes_tuple(value: ast.expr) -> tuple[tuple[str, ...], ...]:
    """提取索引字段组，只接受字符串字面量元组。"""
    if not isinstance(value, ast.Tuple):
        return ()
    return tuple(
        index_fields
        for item in value.elts
        if (index_fields := extract_index_fields(item))
    )


def extract_index_fields(value: ast.expr) -> tuple[str, ...]:
    """提取单个索引字段组。"""
    if not isinstance(value, ast.Tuple):
        return ()
    fields: list[str] = []
    for item in value.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            return ()
        fields.append(item.value)
    return tuple(fields)
