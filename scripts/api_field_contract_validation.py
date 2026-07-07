from __future__ import annotations

import re
import sys
from pathlib import Path

from scripts.api_field_source_introspection import resolve_dotted_source, source_has_symbol


def validate_field_contracts(root: Path) -> list[str]:
    """校验字段契约目录、来源证据、读端点覆盖和收敛目标。"""
    issues: list[str] = []
    try:
        contracts, endpoint_contracts, converge_items = load_field_contract_data(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/api_field_contracts.py: 字段契约目录无效：{exc}"]

    for contract in contracts:
        issues.extend(validate_backend_sources(root, contract))

    endpoint_keys = {contract.key for contract in endpoint_contracts}
    covered_endpoint_keys = {endpoint_key for endpoint_key, _field_contract_key in load_endpoint_field_contracts(root)}
    for endpoint_key, field_contract_key in load_endpoint_field_contracts(root):
        if endpoint_key not in endpoint_keys:
            issues.append(f"scripts/api_field_contracts.py: 端点字段契约引用了不存在的端点 {endpoint_key}")
        if not field_contract_key:
            issues.append(f"scripts/api_field_contracts.py: 端点 {endpoint_key} 未绑定字段契约")
    exempt_endpoint_keys = load_field_contract_exempt_endpoints(root)
    for endpoint_key in iter_field_contract_required_endpoint_keys(endpoint_contracts):
        if endpoint_key in exempt_endpoint_keys:
            continue
        if endpoint_key not in covered_endpoint_keys:
            issues.append(f"scripts/api_field_contracts.py: 端点 {endpoint_key} 缺少字段契约覆盖关系")

    issues.extend(validate_converge_debt_doc(root, converge_items))
    return issues


def validate_backend_sources(root: Path, contract) -> list[str]:
    """校验单个字段契约的 Django/FastAPI 来源类存在。"""
    issues: list[str] = []
    for backend, dotted_path in (("Django", contract.django_source), ("FastAPI", contract.fastapi_source)):
        source_path, symbol_chain = resolve_dotted_source(root, dotted_path)
        if not source_path.exists():
            issues.append(f"{contract.key}: {backend} 字段来源文件不存在 {source_path.relative_to(root)}")
            continue
        if not source_has_symbol(read_text(source_path), symbol_chain):
            symbol_name = ".".join(symbol_chain)
            issues.append(f"{contract.key}: {source_path.relative_to(root)} 缺少字段来源符号 {symbol_name}")
    return issues


def validate_frontend_field_contracts(root: Path) -> list[str]:
    """校验前端 API 类型字段声明仍覆盖已登记字段契约。"""
    issues: list[str] = []
    try:
        contracts = load_frontend_field_contracts(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/api_frontend_field_contracts.py: 前端字段契约目录无效：{exc}"]

    for contract in contracts:
        source_path = root / contract.frontend_source
        if not source_path.exists():
            issues.append(f"{contract.key}: 前端字段来源文件不存在 {contract.frontend_source}")
            continue
        source_text = read_text(source_path)
        for field in contract.required_fields:
            if not has_typescript_field_declaration(source_text, field):
                issues.append(f"{contract.key}: {contract.frontend_source} 缺少字段声明 {field}")

    endpoint_contracts = load_critical_endpoint_contracts(root)
    endpoint_field_contracts = dict(load_endpoint_field_contracts(root))
    tracked_backend_contracts = {contract.tracked_backend_contract for contract in contracts}
    frontend_exempt_endpoints = load_frontend_field_contract_exempt_endpoints(root)
    for endpoint_key in iter_frontend_field_contract_required_endpoint_keys(endpoint_contracts):
        if endpoint_key in frontend_exempt_endpoints:
            continue
        field_contract_key = endpoint_field_contracts.get(endpoint_key)
        if not field_contract_key:
            issues.append(f"scripts/api_frontend_field_contracts.py: 端点 {endpoint_key} 缺少前端字段契约或显式豁免")
            continue
        if field_contract_key not in tracked_backend_contracts:
            issues.append(
                "scripts/api_frontend_field_contracts.py: "
                f"端点 {endpoint_key} 绑定的字段契约 {field_contract_key} 缺少前端类型覆盖"
            )
    return issues


def iter_field_contract_required_endpoint_keys(endpoint_contracts) -> tuple[str, ...]:
    """返回必须绑定字段契约的前端对象响应端点。"""
    return tuple(
        contract.key
        for contract in endpoint_contracts
        if contract.method in {"GET", "POST", "PUT", "PATCH"}
        and contract.response_fields
        and any(evidence.file.startswith("frontend/src/api/") for evidence in contract.evidence)
    )


def iter_frontend_field_contract_required_endpoint_keys(endpoint_contracts) -> tuple[str, ...]:
    """返回必须纳入前端字段契约或豁免的端点。"""
    return tuple(
        contract.key
        for contract in endpoint_contracts
        if contract.method in {"GET", "POST", "PUT", "PATCH"}
        and contract.response_fields
        and any(evidence.file.startswith("frontend/src/api/") for evidence in contract.evidence)
    )


def validate_converge_debt_doc(root: Path, converge_items: tuple[tuple[str, str], ...]) -> list[str]:
    """校验待收敛字段已进入技术债文档，避免 converge 只停留在代码注释。"""
    tech_debt = read_text(root / "docs/TECH_DEBT.md")
    issues: list[str] = []
    for contract_key, field in converge_items:
        snippet = f"`{contract_key}.{field}`"
        if snippet not in tech_debt:
            issues.append(f"docs/TECH_DEBT.md: 缺少字段收敛债务 {snippet}")
    return issues


def load_field_contract_data(root: Path):
    """加载字段契约、端点契约和收敛项。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts
    from scripts.api_field_contracts import (
        assert_api_field_contract_catalog,
        iter_api_field_contracts,
        iter_api_field_converge_items,
    )

    assert_api_field_contract_catalog()
    return iter_api_field_contracts(), iter_critical_endpoint_contracts(), iter_api_field_converge_items()


def load_endpoint_field_contracts(root: Path) -> tuple[tuple[str, str], ...]:
    """加载端点到字段契约的覆盖关系。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_field_contracts import iter_endpoint_field_contracts

    return iter_endpoint_field_contracts()


def load_field_contract_exempt_endpoints(root: Path) -> frozenset[str]:
    """加载不适用双后端字段契约的端点。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_field_contracts import iter_field_contract_exempt_endpoints

    return iter_field_contract_exempt_endpoints()


def load_critical_endpoint_contracts(root: Path):
    """加载关键端点契约目录。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts

    return iter_critical_endpoint_contracts()


def load_frontend_field_contracts(root: Path):
    """从仓库根目录加载前端 API 字段契约目录。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_frontend_field_contracts import (
        assert_api_frontend_field_contract_catalog,
        iter_api_frontend_field_contracts,
    )

    assert_api_frontend_field_contract_catalog()
    return iter_api_frontend_field_contracts()


def load_frontend_field_contract_exempt_endpoints(root: Path) -> frozenset[str]:
    """加载不适用普通前端对象字段契约的端点。"""
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.api_frontend_field_contracts import iter_frontend_field_contract_exempt_endpoints

    return iter_frontend_field_contract_exempt_endpoints()


def has_typescript_field_declaration(source_text: str, field: str) -> bool:
    """判断 TypeScript 接口中是否存在指定字段声明。"""
    pattern = rf"(^|\n)\s*{re.escape(field)}\??\s*:"
    return re.search(pattern, source_text) is not None


def read_text(path: Path) -> str:
    """按仓库约定读取 UTF-8 文本。"""
    return path.read_text(encoding="utf-8")
