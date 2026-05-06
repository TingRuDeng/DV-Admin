#!/usr/bin/env python3
"""Validate repository documentation structure and link health."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_DOCS = [
    ROOT / "AGENTS.md",
    ROOT / "docs/README.md",
    ROOT / "docs/ARCHITECTURE.md",
    ROOT / "docs/API_ENDPOINTS.md",
    ROOT / "docs/DATABASE_SCHEMA.md",
    ROOT / "docs/KNOWN_PITFALLS.md",
    ROOT / "docs/TECH_DEBT.md",
    ROOT / "docs/DOC_SYNC_CHECKLIST.md",
]

AI_CONTEXT_DOC = ROOT / "docs/AI_CONTEXT.md"

REQUIRED_HEADINGS = [
    "## 目的",
    "## 适合读者",
    "## 一分钟摘要",
    "## 权威边界",
    "## 如何验证",
]

AI_CONTEXT_REQUIRED_HEADINGS = [
    "# AI Context",
    "## 权威文档地图",
    "## 任务读取路径",
    "## 关键证据入口",
    "## 高风险误读点",
    "## Optional",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"待补充"),
    re.compile(r"\{\{[^}]+\}\}"),
]

MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _strip_line_suffix(target: str) -> str:
    # Support links like /abs/path/file.md:12 used in local docs.
    match = re.match(r"^(.*):(\d+)$", target)
    if match:
        return match.group(1)
    return target


def _is_external_link(target: str) -> bool:
    target_lower = target.lower()
    return (
        target_lower.startswith("http://")
        or target_lower.startswith("https://")
        or target_lower.startswith("mailto:")
        or target_lower.startswith("tel:")
        or target_lower.startswith("data:")
        or target_lower.startswith("#")
    )


def check_required_sections(path: Path, text: str, errors: list[str]) -> None:
    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE):
            errors.append(f"{path.relative_to(ROOT)} missing heading: {heading}")
    if "ai_summary:" not in text:
        errors.append(f"{path.relative_to(ROOT)} missing ai_summary block")


def check_placeholders(path: Path, text: str, errors: list[str]) -> None:
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{path.relative_to(ROOT)} contains placeholder pattern: {pattern.pattern}"
            )


def check_ai_context(path: Path, text: str, errors: list[str]) -> None:
    indices: list[int] = []
    for heading in AI_CONTEXT_REQUIRED_HEADINGS:
        idx = text.find(heading)
        if idx < 0:
            errors.append(f"{path.relative_to(ROOT)} missing heading: {heading}")
            return
        indices.append(idx)
    if indices != sorted(indices):
        errors.append(
            f"{path.relative_to(ROOT)} heading order invalid: {', '.join(AI_CONTEXT_REQUIRED_HEADINGS)}"
        )

    # Require one blockquote line between title and first section heading.
    first_h2_idx = text.find("## 权威文档地图")
    preface = text[:first_h2_idx]
    has_blockquote = any(line.strip().startswith(">") for line in preface.splitlines()[1:])
    if not has_blockquote:
        errors.append(f"{path.relative_to(ROOT)} missing blockquote preface after title")


def check_local_links(path: Path, text: str, errors: list[str]) -> None:
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = target.split("#", 1)[0].strip()
        if not target or _is_external_link(target):
            continue

        target = _strip_line_suffix(target)
        if target.startswith("file://"):
            errors.append(f"{path.relative_to(ROOT)} should not use file:// link: {raw_target}")
            continue

        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (path.parent / target_path).resolve()

        if not target_path.exists():
            errors.append(
                f"{path.relative_to(ROOT)} has broken local link: {raw_target} -> {target_path}"
            )


def main() -> int:
    errors: list[str] = []

    for doc in AUTHORITY_DOCS:
        if not doc.exists():
            errors.append(f"missing authority doc: {doc.relative_to(ROOT)}")
            continue
        text = _read_text(doc)
        check_required_sections(doc, text, errors)
        check_placeholders(doc, text, errors)

    if not AI_CONTEXT_DOC.exists():
        errors.append("missing AI context index: docs/AI_CONTEXT.md")
    else:
        ai_text = _read_text(AI_CONTEXT_DOC)
        check_ai_context(AI_CONTEXT_DOC, ai_text, errors)

    link_docs = {ROOT / "AGENTS.md", AI_CONTEXT_DOC}
    link_docs.update(ROOT.glob("docs/**/*.md"))
    for doc in sorted(link_docs):
        if doc.exists():
            check_local_links(doc, _read_text(doc), errors)

    if errors:
        print("Documentation validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Documentation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
