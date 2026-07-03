#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from model_constraint_validation import validate_fastapi_field_constraints
from model_django_validation import (
    validate_django_field_constraints,
    validate_django_field_metadata,
    validate_django_model_tables,
    validate_django_relation_through_tables,
)
from model_fastapi_validation import (
    validate_fastapi_alias_target_fields,
    validate_fastapi_field_metadata,
    validate_fastapi_model_tables,
    validate_fastapi_relation_through_tables,
)
from model_index_validation import validate_fastapi_model_indexes, validate_fastapi_unique_together
from model_legacy_schema_validation import validate_legacy_schema_markers
from model_test_validation import validate_tests


REQUIRED_FILES = (
    "scripts/model_contracts.py",
    "fastapi/app/db/import_django_data.py",
    "fastapi/app/db/django_import_config.py",
    "fastapi/tests/test_import_django_model_contracts.py",
    "docs/DATABASE_SCHEMA.md",
    "docs/TECH_DEBT.md",
)

REQUIRED_DOC_SNIPPETS = (
    "Django Fixture 导入约束",
    "scripts/model_contracts.py",
    "keepAlive/alwaysShow",
    "dict` → `dict_data",
    "字典主表内部字段已统一为 `dict_code/remark`",
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
    issues.extend(validate_django_model_tables(root))
    issues.extend(validate_django_field_metadata(root))
    issues.extend(validate_django_field_constraints(root))
    issues.extend(validate_django_relation_through_tables(root))
    issues.extend(validate_fastapi_model_tables(root))
    issues.extend(validate_fastapi_alias_target_fields(root))
    issues.extend(validate_fastapi_relation_through_tables(root))
    issues.extend(validate_fastapi_field_metadata(root))
    issues.extend(validate_fastapi_field_constraints(root))
    issues.extend(validate_fastapi_model_indexes(root))
    issues.extend(validate_fastapi_unique_together(root))
    issues.extend(validate_legacy_schema_markers(root))
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
    mapping_path = "fastapi/app/db/django_import_config.py"
    import_text = read_text(root / mapping_path)
    for contract in contracts:
        for snippet in (contract.django_model, contract.fastapi_model):
            if snippet not in import_text:
                issues.append(f"{mapping_path}: 缺少模型映射 {snippet}")
        for django_field, fastapi_field in contract.field_aliases.items():
            if django_field != fastapi_field and django_field not in import_text:
                issues.append(f"{mapping_path}: 缺少字段映射 {django_field}")
            if django_field != fastapi_field and fastapi_field not in import_text:
                issues.append(f"{mapping_path}: 缺少字段目标 {fastapi_field}")
    return issues


def validate_docs(root: Path) -> list[str]:
    """校验数据库文档记录了模型契约入口和关键映射。"""
    issues: list[str] = []
    text = read_text(root / "docs/DATABASE_SCHEMA.md")
    for snippet in REQUIRED_DOC_SNIPPETS:
        if snippet not in text:
            issues.append(f"docs/DATABASE_SCHEMA.md: 缺少模型契约说明 {snippet}")
    return issues


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
