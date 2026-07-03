#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from scripts.api_contract_validation_rules import (
    FORBIDDEN_FILE_ROUTE_SNIPPETS,
    MAX_RUNTIME_CONTRACT_TEST_LINES,
    REQUIRED_CONTRACT_FUNCTIONS,
    REQUIRED_DOC_SNIPPETS,
    REQUIRED_FILE_ROUTE_SNIPPETS,
    REQUIRED_FILES,
    REQUIRED_TEST_SNIPPETS,
    RUNTIME_CONTRACT_TEST_PATTERNS,
)
from scripts.api_field_contract_validation import validate_field_contracts, validate_frontend_field_contracts
from scripts.api_route_coverage_validation import validate_route_coverage


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

    issues.extend(validate_endpoint_contract_evidence(root))
    issues.extend(validate_field_contracts(root))
    issues.extend(validate_frontend_field_contracts(root))
    issues.extend(validate_api_capability_contracts(root))
    issues.extend(validate_error_code_contract(root))
    issues.extend(validate_route_coverage(root))
    issues.extend(validate_runtime_contract_test_size(root))
    return issues


def validate_runtime_contract_test_size(root: Path) -> list[str]:
    """校验运行时契约测试文件保持小文件，避免后续契约扩面再次堆成大文件。"""
    issues: list[str] = []
    for rel in iter_runtime_contract_test_files(root):
        line_count = len(read_text(root / rel).splitlines())
        if line_count > MAX_RUNTIME_CONTRACT_TEST_LINES:
            issues.append(
                f"{rel}: 运行时契约测试文件 {line_count} 行，超过 {MAX_RUNTIME_CONTRACT_TEST_LINES} 行上限"
            )
    return issues


def iter_runtime_contract_test_files(root: Path) -> list[str]:
    """返回现有运行时契约测试文件，兼容拆分前后的文件布局。"""
    files: list[str] = []
    for pattern in RUNTIME_CONTRACT_TEST_PATTERNS:
        files.extend(sorted(path.relative_to(root).as_posix() for path in root.glob(pattern)))
    return files


def validate_endpoint_contract_evidence(root: Path) -> list[str]:
    """校验关键端点契约目录及其代码/文档证据。"""
    issues: list[str] = []
    try:
        contracts = load_endpoint_contracts(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/api_endpoint_contracts.py: 端点契约目录无效：{exc}"]

    for contract in contracts:
        for evidence in contract.evidence:
            evidence_path = root / evidence.file
            if not evidence_path.exists():
                issues.append(f"{contract.key}: 缺少证据文件 {evidence.file}")
                continue
            evidence_text = read_text(evidence_path)
            for snippet in evidence.snippets:
                if snippet not in evidence_text:
                    issues.append(f"{contract.key}: {evidence.file} 缺少证据片段 {snippet}")
    return issues


def validate_api_capability_contracts(root: Path) -> list[str]:
    """校验单后端 API 能力边界契约及其正反向证据。"""
    issues: list[str] = []
    try:
        contracts = load_api_capability_contracts(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/api_capability_contracts.py: 能力边界契约目录无效：{exc}"]

    for contract in contracts:
        fastapi_path = root / contract.fastapi_source
        if not fastapi_path.exists():
            issues.append(f"{contract.key}: FastAPI 能力来源文件不存在 {contract.fastapi_source}")
            continue
        fastapi_text = read_text(fastapi_path)
        for snippet in contract.fastapi_snippets:
            if snippet not in fastapi_text:
                issues.append(f"{contract.key}: {contract.fastapi_source} 缺少 FastAPI 能力证据 {snippet}")

        django_path = root / contract.django_absent_source
        if not django_path.exists():
            issues.append(f"{contract.key}: Django 缺席证据文件不存在 {contract.django_absent_source}")
            continue
        django_text = read_text(django_path)
        for snippet in contract.django_forbidden_snippets:
            if snippet in django_text:
                issues.append(f"{contract.key}: {contract.django_absent_source} 出现独占能力禁止片段 {snippet}")
    return issues


def load_api_capability_contracts(root: Path):
    """从仓库根目录加载 API 能力边界契约目录。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_capability_contracts import (
        assert_api_capability_contract_catalog,
        iter_api_capability_contracts,
    )

    assert_api_capability_contract_catalog()
    return iter_api_capability_contracts()


def resolve_dotted_source(root: Path, dotted_path: str) -> tuple[Path, str]:
    """把后端 dotted path 映射到仓库内源码文件路径。"""
    module_name, class_name = dotted_path.rsplit(".", 1)
    if module_name.startswith("drf_admin."):
        return root / "backend" / Path(*module_name.split(".")).with_suffix(".py"), class_name
    if module_name.startswith("app."):
        return root / "fastapi" / Path(*module_name.split(".")).with_suffix(".py"), class_name
    return root / Path(*module_name.split(".")).with_suffix(".py"), class_name


def load_endpoint_contracts(root: Path):
    """从仓库根目录加载端点契约目录，避免脚本工作目录影响 import。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_contracts import assert_endpoint_contract_catalog, iter_critical_endpoint_contracts

    assert_endpoint_contract_catalog()
    return iter_critical_endpoint_contracts()


def validate_error_code_contract(root: Path) -> list[str]:
    """校验共享错误码目录与前端枚举是否保持同步。"""
    issues: list[str] = []
    try:
        codes = load_error_codes(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/api_error_codes.py: 错误码契约目录无效：{exc}"]

    enum_text = read_text(root / "frontend/src/enums/api/code-enum.ts")
    for code in codes:
        enum_entry = f"{code.key} = {code.value}"
        if enum_entry not in enum_text:
            issues.append(f"frontend/src/enums/api/code-enum.ts: 缺少错误码枚举 {enum_entry}")
    return issues


def load_error_codes(root: Path):
    """从仓库根目录加载共享错误码目录。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_error_codes import assert_api_error_code_catalog, iter_api_error_codes

    assert_api_error_code_catalog()
    return iter_api_error_codes()


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
