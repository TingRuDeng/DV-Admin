#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

REQUIRED_SYSTEM_MIGRATIONS = (
    "backend/drf_admin/apps/system/migrations/__init__.py",
    "backend/drf_admin/apps/system/migrations/0001_initial.py",
    "backend/drf_admin/apps/system/migrations/0002_alter_dictitems_options_remove_dictitems_sort_and_more.py",
    "backend/drf_admin/apps/system/migrations/0003_notices.py",
)

REQUIRED_GITIGNORE_SNIPPETS = (
    "!backend/drf_admin/apps/**/migrations/",
    "!backend/drf_admin/apps/**/migrations/__init__.py",
    "!backend/drf_admin/apps/**/migrations/[0-9][0-9][0-9][0-9]_*.py",
)


def validate(root: Path) -> list[str]:
    """校验 Django 迁移链必须被仓库显式跟踪。"""
    issues: list[str] = []
    tracked_files = load_tracked_files(root)
    issues.extend(validate_required_migrations(root, tracked_files))
    issues.extend(validate_gitignore(root))
    return issues


def validate_required_migrations(root: Path, tracked_files: set[str]) -> list[str]:
    """检查关键迁移文件既存在于工作区，也纳入 Git 索引。"""
    issues: list[str] = []
    for rel in REQUIRED_SYSTEM_MIGRATIONS:
        path = root / rel
        if not path.exists():
            issues.append(f"{rel}: 缺少 Django system 迁移文件")
            continue
        if rel not in tracked_files:
            issues.append(f"{rel}: Django system 迁移文件未被 Git 跟踪")
    return issues


def validate_gitignore(root: Path) -> list[str]:
    """检查仓库 ignore 规则显式允许 Django 迁移覆盖用户全局 ignore。"""
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return [".gitignore: 缺少仓库 ignore 文件"]

    gitignore_text = gitignore_path.read_text(encoding="utf-8")
    return [
        f".gitignore: 缺少 Django 迁移 unignore 规则 {snippet}"
        for snippet in REQUIRED_GITIGNORE_SNIPPETS
        if snippet not in gitignore_text
    ]


def load_tracked_files(root: Path) -> set[str]:
    """读取 Git 已跟踪文件列表，避免被本地全局 ignore 状态误导。"""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())


def parse_root(args: Sequence[str]) -> Path:
    """解析可选仓库根目录，默认使用当前工作目录。"""
    if args:
        return Path(args[0]).resolve()
    return Path.cwd().resolve()


def main(argv: Sequence[str] | None = None) -> int:
    """命令行入口，逐条输出迁移链治理问题。"""
    root = parse_root(sys.argv[1:] if argv is None else argv)
    issues = validate(root)
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
