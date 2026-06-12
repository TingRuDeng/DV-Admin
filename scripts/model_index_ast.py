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


def load_fastapi_unique_together(root: Path) -> dict[str, tuple[str, ...]]:
    """静态读取 FastAPI 模型 Meta.unique_together 声明。"""
    unique_together: dict[str, tuple[str, ...]] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        unique_together.update(extract_module_unique_together(module))
    return unique_together


def extract_module_indexes(module: ast.Module) -> dict[str, tuple[tuple[str, ...], ...]]:
    """提取单个 FastAPI 模型模块内所有 class Meta.indexes。"""
    indexes_by_model: dict[str, tuple[tuple[str, ...], ...]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            indexes = extract_meta_indexes(node)
            if indexes:
                indexes_by_model[node.name] = indexes
    return indexes_by_model


def extract_module_unique_together(module: ast.Module) -> dict[str, tuple[str, ...]]:
    """提取单个 FastAPI 模型模块内所有 class Meta.unique_together。"""
    unique_by_model: dict[str, tuple[str, ...]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            fields = extract_meta_unique_together(node)
            if fields:
                unique_by_model[node.name] = fields
    return unique_by_model


def extract_meta_indexes(model_node: ast.ClassDef) -> tuple[tuple[str, ...], ...]:
    """从 Tortoise 模型的内部 Meta 类提取 indexes 字面量。"""
    for child in model_node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            return extract_indexes_assignment(child)
    return ()


def extract_meta_unique_together(model_node: ast.ClassDef) -> tuple[str, ...]:
    """从 Tortoise 模型的内部 Meta 类提取 unique_together 字面量。"""
    for child in model_node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            return extract_unique_together_assignment(child)
    return ()


def extract_indexes_assignment(meta_node: ast.ClassDef) -> tuple[tuple[str, ...], ...]:
    """读取 Meta.indexes = ((...), ...) 形式的索引声明。"""
    for statement in meta_node.body:
        if isinstance(statement, ast.Assign) and is_indexes_target(statement.targets):
            return extract_indexes_tuple(statement.value)
    return ()


def extract_unique_together_assignment(meta_node: ast.ClassDef) -> tuple[str, ...]:
    """读取 Meta.unique_together = (...) 形式的唯一组合声明。"""
    for statement in meta_node.body:
        if isinstance(statement, ast.Assign) and is_unique_together_target(statement.targets):
            return extract_index_fields(statement.value)
    return ()


def is_indexes_target(targets: list[ast.expr]) -> bool:
    """判断赋值目标是否包含 indexes 字段。"""
    return any(isinstance(target, ast.Name) and target.id == "indexes" for target in targets)


def is_unique_together_target(targets: list[ast.expr]) -> bool:
    """判断赋值目标是否包含 unique_together 字段。"""
    return any(isinstance(target, ast.Name) and target.id == "unique_together" for target in targets)


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
