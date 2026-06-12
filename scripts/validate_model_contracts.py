#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


REQUIRED_FILES = (
    "scripts/model_contracts.py",
    "fastapi/app/db/import_django_data.py",
    "fastapi/tests/test_import_django_model_contracts.py",
    "docs/DATABASE_SCHEMA.md",
    "docs/TECH_DEBT.md",
)

REQUIRED_DOC_SNIPPETS = (
    "Django Fixture 导入约束",
    "scripts/model_contracts.py",
    "keepAlive/alwaysShow",
    "dict_code` → `code",
    "remark` → `desc",
)
FASTAPI_MODEL_FILES = (
    "fastapi/app/db/models/system.py",
    "fastapi/app/db/models/oauth.py",
)


def validate(root: Path) -> list[str]:
    """校验 Django 到 FastAPI 模型契约、导入映射和文档说明是否同步。"""
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"{rel}: 缺少模型契约治理文件")
    if issues:
        return issues

    issues.extend(validate_contract_catalog(root))
    issues.extend(validate_import_mapping(root))
    issues.extend(validate_fastapi_model_tables(root))
    issues.extend(validate_docs(root))
    issues.extend(validate_tests(root))
    return issues


def validate_contract_catalog(root: Path) -> list[str]:
    """加载共享模型契约目录，确保目录自身有效。"""
    try:
        load_contracts(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/model_contracts.py: 模型契约目录无效：{exc}"]
    return []


def validate_import_mapping(root: Path) -> list[str]:
    """校验导入脚本包含契约声明的模型和字段映射。"""
    issues: list[str] = []
    contracts = load_contracts(root)
    import_text = read_text(root / "fastapi/app/db/import_django_data.py")
    for contract in contracts:
        for snippet in (contract.django_model, contract.fastapi_model):
            if snippet not in import_text:
                issues.append(f"fastapi/app/db/import_django_data.py: 缺少模型映射 {snippet}")
        for django_field, fastapi_field in contract.field_aliases.items():
            if django_field != fastapi_field and django_field not in import_text:
                issues.append(f"fastapi/app/db/import_django_data.py: 缺少字段映射 {django_field}")
            if django_field != fastapi_field and fastapi_field not in import_text:
                issues.append(f"fastapi/app/db/import_django_data.py: 缺少字段目标 {fastapi_field}")
    return issues


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


def validate_docs(root: Path) -> list[str]:
    """校验数据库文档记录了模型契约入口和关键映射。"""
    issues: list[str] = []
    text = read_text(root / "docs/DATABASE_SCHEMA.md")
    for snippet in REQUIRED_DOC_SNIPPETS:
        if snippet not in text:
            issues.append(f"docs/DATABASE_SCHEMA.md: 缺少模型契约说明 {snippet}")
    return issues


def validate_tests(root: Path) -> list[str]:
    """校验 FastAPI 导入测试引用共享模型契约目录。"""
    text = read_text(root / "fastapi/tests/test_import_django_model_contracts.py")
    required = (
        "iter_django_fastapi_model_contracts",
        "test_import_mapping_matches_shared_model_contracts",
        "test_fastapi_model_tables_match_shared_contracts",
    )
    return [
        f"fastapi/tests/test_import_django_model_contracts.py: 缺少模型契约测试片段 {snippet}"
        for snippet in required
        if snippet not in text
    ]


def load_contracts(root: Path):
    """从仓库根目录加载模型契约，避免脚本工作目录影响 import。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.model_contracts import (
        assert_model_contract_catalog,
        iter_django_fastapi_model_contracts,
    )

    assert_model_contract_catalog()
    return iter_django_fastapi_model_contracts()


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")


def parse_root(args: Sequence[str]) -> Path:
    """解析可选仓库根目录，默认使用当前工作目录。"""
    if args:
        return Path(args[0]).resolve()
    return Path.cwd().resolve()


def main(argv: Sequence[str] | None = None) -> int:
    """命令行入口，发现问题时逐条输出并返回非零状态。"""
    root = parse_root(sys.argv[1:] if argv is None else argv)
    issues = validate(root)
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
