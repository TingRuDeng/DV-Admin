from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple


FASTAPI_MODEL_FILES = (
    "fastapi/app/db/models/base.py",
    "fastapi/app/db/models/system.py",
    "fastapi/app/db/models/oauth.py",
)


class FastapiFieldMetadata(NamedTuple):
    """FastAPI 字段静态元数据。"""

    field_type: str
    null: bool
    default: object


def load_fastapi_model_tables(root: Path) -> dict[str, str]:
    """静态读取 FastAPI 模型 Meta.table，避免校验脚本依赖运行时数据库。"""
    tables: dict[str, str] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        tables.update(extract_module_tables(module))
    return tables


def extract_module_tables(module: ast.Module) -> dict[str, str]:
    """提取单个 FastAPI 模型模块内所有 class Meta.table。"""
    tables: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            table = extract_meta_table(node)
            if table:
                tables[node.name] = table
    return tables


def extract_meta_table(model_node: ast.ClassDef) -> str:
    """从 Tortoise 模型的内部 Meta 类提取 table 字面量。"""
    for child in model_node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            return extract_table_assignment(child)
    return ""


def extract_table_assignment(meta_node: ast.ClassDef) -> str:
    """读取 Meta.table = 'xxx' 形式的表名声明。"""
    for statement in meta_node.body:
        if isinstance(statement, ast.Assign) and is_table_target(statement.targets):
            if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
                return statement.value.value
    return ""


def is_table_target(targets: list[ast.expr]) -> bool:
    """判断赋值目标是否包含 table 字段。"""
    return any(isinstance(target, ast.Name) and target.id == "table" for target in targets)


def load_fastapi_model_fields(root: Path) -> dict[str, set[str]]:
    """静态读取 FastAPI 模型字段声明，覆盖普通字段和类型注解字段。"""
    model_fields: dict[str, set[str]] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        model_fields.update(extract_module_fields(module))
    return model_fields


def extract_module_fields(module: ast.Module) -> dict[str, set[str]]:
    """提取单个 FastAPI 模型模块内的类字段名。"""
    fields_by_model: dict[str, set[str]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            fields_by_model[node.name] = extract_class_fields(node)
    return fields_by_model


def extract_class_fields(model_node: ast.ClassDef) -> set[str]:
    """提取类体中的字段赋值和字段注解名称。"""
    field_names: set[str] = set()
    for statement in model_node.body:
        if isinstance(statement, ast.Assign):
            field_names.update(extract_name_targets(statement.targets))
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            field_names.add(statement.target.id)
    return field_names


def extract_name_targets(targets: list[ast.expr]) -> set[str]:
    """提取赋值语句中的简单名称目标。"""
    return {target.id for target in targets if isinstance(target, ast.Name)}


def load_fastapi_field_metadata(root: Path) -> dict[str, dict[str, FastapiFieldMetadata]]:
    """静态读取 FastAPI 模型字段类型、null 和 default。"""
    metadata: dict[str, dict[str, FastapiFieldMetadata]] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        metadata.update(extract_module_field_metadata(module))
    return metadata


def extract_module_field_metadata(module: ast.Module) -> dict[str, dict[str, FastapiFieldMetadata]]:
    """提取单个 FastAPI 模型模块内的字段元数据。"""
    metadata_by_model: dict[str, dict[str, FastapiFieldMetadata]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            model_metadata = extract_class_field_metadata(node)
            if model_metadata:
                metadata_by_model[node.name] = model_metadata
    return metadata_by_model


def extract_class_field_metadata(model_node: ast.ClassDef) -> dict[str, FastapiFieldMetadata]:
    """提取类体中 fields.*Field 声明的静态元数据。"""
    field_metadata: dict[str, FastapiFieldMetadata] = {}
    for statement in model_node.body:
        field_name, call = extract_field_call(statement)
        if field_name and call:
            field_metadata[field_name] = build_field_metadata(call)
    return field_metadata


def extract_field_call(statement: ast.stmt) -> tuple[str, ast.Call | None]:
    """提取字段名和 fields.*Field 调用。"""
    if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
        targets = extract_name_targets(statement.targets)
        field_name = next(iter(targets), "")
        return field_name, statement.value if is_fastapi_field_call(statement.value) else None
    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        if isinstance(statement.value, ast.Call) and is_fastapi_field_call(statement.value):
            return statement.target.id, statement.value
    return "", None


def is_fastapi_field_call(call: ast.Call) -> bool:
    """判断调用是否为 fields.*Field。"""
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr.endswith("Field")
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "fields"
    )


def build_field_metadata(call: ast.Call) -> FastapiFieldMetadata:
    """从字段调用提取字段类型、null 和 default。"""
    return FastapiFieldMetadata(
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


def load_fastapi_relation_through_tables(root: Path) -> dict[str, dict[str, str]]:
    """静态读取 FastAPI 模型多对多字段 through 表声明。"""
    relations: dict[str, dict[str, str]] = {}
    for rel in FASTAPI_MODEL_FILES:
        module = ast.parse(read_text(root / rel))
        relations.update(extract_module_relation_through_tables(module))
    return relations


def extract_module_relation_through_tables(module: ast.Module) -> dict[str, dict[str, str]]:
    """提取单个 FastAPI 模型模块内的多对多 through 表声明。"""
    relations_by_model: dict[str, dict[str, str]] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            through_tables = extract_class_relation_through_tables(node)
            if through_tables:
                relations_by_model[node.name] = through_tables
    return relations_by_model


def extract_class_relation_through_tables(model_node: ast.ClassDef) -> dict[str, str]:
    """提取类体中 fields.ManyToManyField 的 through 参数。"""
    through_tables: dict[str, str] = {}
    for statement in model_node.body:
        field_name = extract_annotation_target_name(statement)
        if field_name:
            through_table = extract_many_to_many_through(statement)
            if through_table:
                through_tables[field_name] = through_table
    return through_tables


def extract_annotation_target_name(statement: ast.stmt) -> str:
    """提取字段注解语句左侧名称。"""
    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        return statement.target.id
    return ""


def extract_many_to_many_through(statement: ast.stmt) -> str:
    """读取 fields.ManyToManyField(..., through='xxx') 的 through 字面量。"""
    if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.value, ast.Call):
        return ""
    call = statement.value
    if not is_many_to_many_call(call):
        return ""
    for keyword in call.keywords:
        if keyword.arg == "through" and isinstance(keyword.value, ast.Constant):
            if isinstance(keyword.value.value, str):
                return keyword.value.value
    return ""


def is_many_to_many_call(call: ast.Call) -> bool:
    """判断调用是否为 fields.ManyToManyField。"""
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "ManyToManyField"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "fields"
    )


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
