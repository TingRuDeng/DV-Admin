#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

REQUIRED_FILES = (
    "scripts/api_contracts.py",
    "backend/drf_admin/utils/test_response_contract.py",
    "fastapi/tests/test_api_contracts.py",
    "frontend/src/utils/__tests__/api-contract.test.ts",
    "docs/API_ENDPOINTS.md",
    "fastapi/app/api/v1/README.md",
)

REQUIRED_CONTRACT_FUNCTIONS = (
    "normalize_api_envelope",
    "assert_success_envelope",
    "assert_error_envelope",
    "assert_page_payload",
)

REQUIRED_DOC_SNIPPETS = (
    "共享 API 契约验证",
    "scripts/validate_api_contracts.py",
    "Django 响应中间件统一输出",
    "FastAPI `ResponseModel` 默认输出",
)

REQUIRED_TEST_SNIPPETS = {
    "backend/drf_admin/utils/test_response_contract.py": ("assert_success_envelope", "assert_error_envelope"),
    "fastapi/tests/test_api_contracts.py": ("ResponseModel.success", "PageResult.create"),
    "frontend/src/utils/__tests__/api-contract.test.ts": ("Django", "FastAPI", "list", "total"),
}

REQUIRED_FILE_ROUTE_SNIPPETS = {
    "docs/API_ENDPOINTS.md": (
        "POST   /api/v1/files/",
        "DELETE /api/v1/files/?filePath=files/{user_id}/{filename}",
        "上传响应 `data.path`",
    ),
    "fastapi/app/api/v1/README.md": (
        "POST /api/v1/files/",
        "DELETE /api/v1/files/?filePath=files/{user_id}/{filename}",
    ),
}

FORBIDDEN_FILE_ROUTE_SNIPPETS = {
    "docs/API_ENDPOINTS.md": ("/api/v1/files/upload/",),
    "fastapi/app/api/v1/README.md": ("/api/v1/files/upload/",),
}


def validate(root: Path) -> list[str]:
    """校验 API 契约定义、测试覆盖和文档入口是否同步。"""
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"{rel}: 缺少 API 契约治理文件")
    if issues:
        return issues

    contract_text = read_text(root / "scripts/api_contracts.py")
    for function_name in REQUIRED_CONTRACT_FUNCTIONS:
        if f"def {function_name}(" not in contract_text:
            issues.append(f"scripts/api_contracts.py: 缺少契约函数 {function_name}")

    api_doc = read_text(root / "docs/API_ENDPOINTS.md")
    for snippet in REQUIRED_DOC_SNIPPETS:
        if snippet not in api_doc:
            issues.append(f"docs/API_ENDPOINTS.md: 缺少契约说明 {snippet}")

    for rel, snippets in REQUIRED_TEST_SNIPPETS.items():
        text = read_text(root / rel)
        for snippet in snippets:
            if snippet not in text:
                issues.append(f"{rel}: 缺少契约测试片段 {snippet}")
    for rel, snippets in REQUIRED_FILE_ROUTE_SNIPPETS.items():
        text = read_text(root / rel)
        for snippet in snippets:
            if snippet not in text:
                issues.append(f"{rel}: 缺少文件接口契约片段 {snippet}")
    for rel, snippets in FORBIDDEN_FILE_ROUTE_SNIPPETS.items():
        text = read_text(root / rel)
        for snippet in snippets:
            if snippet in text:
                issues.append(f"{rel}: 仍包含过期文件接口路径 {snippet}")
    return issues


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
