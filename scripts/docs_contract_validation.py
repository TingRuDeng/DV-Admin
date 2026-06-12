from __future__ import annotations

from pathlib import Path

CONTRACT_REQUIRED_FILES = (
    "scripts/api_contracts.py",
    "scripts/validate_api_contracts.py",
    "scripts/model_contracts.py",
    "scripts/validate_model_contracts.py",
)
API_CONTRACT_DOC_SNIPPETS = ("共享 API 契约验证", "scripts/validate_api_contracts.py")
MODEL_CONTRACT_DOC_SNIPPETS = ("Django Fixture 导入约束", "scripts/model_contracts.py")
DJANGO_MIGRATION_REQUIRED_FILES = ("scripts/validate_django_migrations.py",)
DJANGO_MIGRATION_DOC_SNIPPETS = ("Django 迁移链校验", "scripts/validate_django_migrations.py")
PNPM_ACTION_SETUP_REQUIRED = "pnpm/action-setup@v6"
PNPM_ACTION_SETUP_FORBIDDEN = "pnpm/action-setup@v4"


def validate_contract_entrypoints(base: Path) -> list[str]:
    """校验契约校验入口、文档片段和 CI workflow 已同步。"""
    issues: list[str] = []
    issues.extend(validate_required_contract_files(base))
    issues.extend(validate_api_contract_doc(base))
    issues.extend(validate_model_contract_doc(base))
    issues.extend(validate_quality_workflow(base))
    return issues


def validate_required_contract_files(base: Path) -> list[str]:
    """校验仓库存在所有契约校验入口文件。"""
    issues: list[str] = []
    for rel in CONTRACT_REQUIRED_FILES + DJANGO_MIGRATION_REQUIRED_FILES:
        if not (base / rel).exists():
            issues.append(f"{rel}: 缺少契约校验入口")
    return issues


def validate_api_contract_doc(base: Path) -> list[str]:
    """校验 API 文档记录共享 API 契约入口。"""
    api_doc = base / "docs/API_ENDPOINTS.md"
    if not api_doc.exists():
        return []
    text = read_text(api_doc)
    return [
        f"docs/API_ENDPOINTS.md: 缺少 API 契约说明 {snippet}"
        for snippet in API_CONTRACT_DOC_SNIPPETS
        if snippet not in text
    ]


def validate_model_contract_doc(base: Path) -> list[str]:
    """校验数据库文档记录模型和迁移契约入口。"""
    schema_doc = base / "docs/DATABASE_SCHEMA.md"
    if not schema_doc.exists():
        return []
    text = read_text(schema_doc)
    return [
        f"docs/DATABASE_SCHEMA.md: 缺少模型契约说明 {snippet}"
        for snippet in MODEL_CONTRACT_DOC_SNIPPETS + DJANGO_MIGRATION_DOC_SNIPPETS
        if snippet not in text
    ]


def validate_quality_workflow(base: Path) -> list[str]:
    """校验质量门禁 workflow 运行必要契约检查并使用当前 pnpm action。"""
    workflow = base / ".github/workflows/quality-gates.yml"
    if not workflow.exists():
        return []
    workflow_text = read_text(workflow)
    issues: list[str] = []
    if "scripts/validate_api_contracts.py" not in workflow_text:
        issues.append(".github/workflows/quality-gates.yml: 未运行 API 契约校验")
    if "scripts/validate_model_contracts.py" not in workflow_text:
        issues.append(".github/workflows/quality-gates.yml: 未运行模型契约校验")
    if "scripts/validate_django_migrations.py" not in workflow_text:
        issues.append(".github/workflows/quality-gates.yml: 未运行 Django 迁移链校验")
    if PNPM_ACTION_SETUP_REQUIRED not in workflow_text:
        issues.append(".github/workflows/quality-gates.yml: 未使用 pnpm/action-setup@v6")
    if PNPM_ACTION_SETUP_FORBIDDEN in workflow_text:
        issues.append(".github/workflows/quality-gates.yml: 仍使用 pnpm/action-setup@v4")
    return issues


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
