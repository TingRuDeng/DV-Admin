from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple


DJANGO_MODEL_FILES = (
    "backend/drf_admin/apps/system/models.py",
    "backend/drf_admin/apps/system/models_notice.py",
)


class DjangoFieldMetadata(NamedTuple):
    """Django 字段静态元数据。"""

    field_type: str
    null: bool
    default: object


def load_django_model_tables(root: Path) -> dict[str, str]:
    """静态读取 Django 模型 Meta.db_table 声明。"""
    tables: dict[str, str] = {}
    for rel in DJANGO_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        tables.update(extract_module_tables(module))
    return tables


def load_django_field_metadata(root: Path) -> dict[str, dict[str, DjangoFieldMetadata]]:
    """静态读取 Django 模型字段类型、null 和 default。"""
    metadata: dict[str, dict[str, DjangoFieldMetadata]] = {}
    for rel in DJANGO_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        metadata.update(extract_module_field_metadata(module))
    return metadata


def extract_module_tables(module: ast.Module) -> dict[str, str]:
    """提取单个 Django 模型模块内所有 class Meta.db_table。"""
    tables: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            table = extract_meta_db_table(node)
            if table:
                tables[f"system.{node.name.lower()}"] = table
    return tables


def extract_module_field_metadata(module: ast.Module) -> dict[str, dict[str, DjangoFieldMetadata]]:
    """提取单个 Django 模型模块内的字段元数据。"""
    metadata_by_model: dict[str, dict[str, DjangoFieldMetadata]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            model_metadata = extract_class_field_metadata(node)
            if model_metadata:
                metadata_by_model[f"system.{node.name.lower()}"] = model_metadata
    return metadata_by_model


def extract_class_field_metadata(model_node: ast.ClassDef) -> dict[str, DjangoFieldMetadata]:
    """提取类体中 models.*Field 声明的静态元数据。"""
    field_metadata: dict[str, DjangoFieldMetadata] = {}
    for statement in model_node.body:
        field_name, call = extract_field_call(statement)
        if field_name and call:
            field_metadata[field_name] = build_field_metadata(call)
    return field_metadata


def extract_field_call(statement: ast.stmt) -> tuple[str, ast.Call | None]:
    """提取 Django 字段名和 models.*Field 调用。"""
    if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
        field_name = next(iter(extract_name_targets(statement.targets)), "")
        return field_name, statement.value if is_django_field_call(statement.value) else None
    return "", None


def extract_name_targets(targets: list[ast.expr]) -> set[str]:
    """提取赋值语句中的简单名称目标。"""
    return {target.id for target in targets if isinstance(target, ast.Name)}


def is_django_field_call(call: ast.Call) -> bool:
    """判断调用是否为 models.*Field。"""
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr.endswith("Field")
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "models"
    )


def build_field_metadata(call: ast.Call) -> DjangoFieldMetadata:
    """从 Django 字段调用提取字段类型、null 和 default。"""
    return DjangoFieldMetadata(
        field_type=call.func.attr,
        null=extract_bool_keyword(call, "null", default=False),
        default=extract_keyword_value(call, "default"),
    )


def extract_bool_keyword(call: ast.Call, name: str, default: bool) -> bool:
    """提取布尔关键字，缺省时返回指定默认值。"""
    value = extract_keyword_value(call, name)
    if isinstance(value, bool):
        return value
    return default


def extract_keyword_value(call: ast.Call, name: str) -> object:
    """提取关键字字面量；未声明时返回 None。"""
    for keyword in call.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return None


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
