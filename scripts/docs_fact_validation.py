from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ForbiddenDocFact:
    """描述已经失效、不得回流到文档或契约脚本的事实表述。"""

    scope: str
    snippets: tuple[str, ...]
    reason: str


FORBIDDEN_DOC_FACTS = (
    ForbiddenDocFact(
        scope="操作日志双后端能力",
        snippets=(
            "Django 当前只有文件日志中间件",
            "Django `OperationLogMiddleware` 当前仅写入日志文件",
            "不提供可查询的 `OperationLog` 数据库模型或日志管理 API",
            "该能力尚未在 Django 实现中对齐",
            "FastAPI 独占日志模型",
            "FastAPI 独占事实",
        ),
        reason="操作日志已在 Django 与 FastAPI 双实现，旧独占描述会误导后续治理。",
    ),
)

DOC_FACT_SCAN_PATHS = (
    "docs/ARCHITECTURE.md",
    "docs/API_ENDPOINTS.md",
    "docs/DATABASE_SCHEMA.md",
    "docs/TECH_DEBT.md",
    "scripts/api_capability_contracts.py",
)


def validate_doc_facts(base: Path) -> list[str]:
    """校验跨文档事实未回流到已废弃结论。"""
    issues: list[str] = []
    for rel in DOC_FACT_SCAN_PATHS:
        path = base / rel
        if not path.exists():
            continue
        text = read_text(path)
        for fact in FORBIDDEN_DOC_FACTS:
            for snippet in fact.snippets:
                if snippet in text:
                    issues.append(f"{rel}: 仍包含过期事实 {snippet}（{fact.reason}）")
    return issues


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
