from __future__ import annotations

from pathlib import Path


FASTAPI_TEST_PATH = "fastapi/tests/test_import_django_model_contracts.py"
DJANGO_TEST_PATH = "backend/drf_admin/utils/test_model_contracts.py"

FASTAPI_REQUIRED_SNIPPETS = (
    "iter_django_fastapi_model_contracts",
    "iter_fastapi_alias_targets",
    "iter_django_fastapi_relation_contracts",
    "iter_fastapi_field_metadata_contracts",
    "iter_fastapi_field_constraint_contracts",
    "iter_fastapi_model_index_contracts",
    "iter_fastapi_unique_together_contracts",
    "test_import_mapping_matches_shared_model_contracts",
    "test_fastapi_model_tables_match_shared_contracts",
    "test_fastapi_model_alias_targets_match_shared_contracts",
    "test_fastapi_relation_through_tables_match_shared_contracts",
    "test_fastapi_field_metadata_matches_shared_contracts",
    "test_fastapi_field_constraints_match_shared_contracts",
    "test_fastapi_model_indexes_match_shared_contracts",
    "test_fastapi_model_unique_together_matches_shared_contracts",
)

DJANGO_REQUIRED_SNIPPETS = (
    "iter_django_model_table_contracts",
    "test_django_model_tables_match_shared_contracts",
)


def validate_tests(root: Path) -> list[str]:
    """校验 Django/FastAPI 模型契约测试引用共享契约目录。"""
    issues = validate_required_snippets(root, FASTAPI_TEST_PATH, FASTAPI_REQUIRED_SNIPPETS)
    issues.extend(validate_required_snippets(root, DJANGO_TEST_PATH, DJANGO_REQUIRED_SNIPPETS))
    return issues


def validate_required_snippets(root: Path, relative_path: str, snippets: tuple[str, ...]) -> list[str]:
    """校验指定测试文件包含所有必须的契约测试片段。"""
    text = read_text(root / relative_path)
    return [
        f"{relative_path}: 缺少模型契约测试片段 {snippet}"
        for snippet in snippets
        if snippet not in text
    ]


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
