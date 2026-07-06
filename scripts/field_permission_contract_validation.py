from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any


def validate_field_permission_contracts(root: Path) -> list[str]:
    """校验字段权限码在运行时代码、Django seed 和 FastAPI fixture 中完整登记。"""
    try:
        contracts = load_field_permission_contracts(root)
    except (AssertionError, ImportError) as exc:
        return [f"scripts/field_permission_contracts.py: 字段权限码目录无效：{exc}"]

    issues: list[str] = []
    issues.extend(validate_runtime_sources(root, contracts))
    issues.extend(validate_django_seed(root, contracts))
    issues.extend(validate_fastapi_fixture(root, contracts))
    return issues


def validate_runtime_sources(root: Path, contracts) -> list[str]:
    """校验双后端字段权限运行时代码都声明了契约权限码。"""
    issues: list[str] = []
    for contract in contracts:
        for backend, rel in (("Django", contract.django_source), ("FastAPI", contract.fastapi_source)):
            source_path = root / rel
            if not source_path.exists():
                issues.append(f"{contract.key}: {backend} 字段权限来源文件不存在 {rel}")
                continue
            if contract.perm not in source_path.read_text(encoding="utf-8"):
                issues.append(f"{contract.key}: {rel} 缺少字段权限码 {contract.perm}")
    return issues


def validate_django_seed(root: Path, contracts) -> list[str]:
    """校验 Django 初始权限树收录了所有字段权限码。"""
    rows = json.loads((root / "backend/init_data.json").read_text(encoding="utf-8"))
    permissions = {
        row["fields"].get("perm"): row
        for row in rows
        if row.get("model") == "system.permissions" and row.get("fields", {}).get("perm")
    }
    admin_role = find_role(rows, "admin")
    ordinary_role = find_role(rows, "普通用户")

    issues: list[str] = []
    for contract in contracts:
        permission = permissions.get(contract.perm)
        if permission is None:
            issues.append(f"backend/init_data.json: 缺少字段权限码 {contract.perm}")
            continue
        fields = permission["fields"]
        if fields.get("name") != contract.name:
            issues.append(f"backend/init_data.json: {contract.perm} 名称应为 {contract.name}")
        if fields.get("type") != "BUTTON":
            issues.append(f"backend/init_data.json: {contract.perm} 类型应为 BUTTON")
        if fields.get("parent") != contract.parent_pk:
            issues.append(f"backend/init_data.json: {contract.perm} 父级应为 {contract.parent_pk}")
        if permission["pk"] not in admin_role.get("fields", {}).get("permissions", []):
            issues.append(f"backend/init_data.json: admin 角色缺少字段权限 {contract.perm}")
        if permission["pk"] in ordinary_role.get("fields", {}).get("permissions", []):
            issues.append(f"backend/init_data.json: 普通用户角色不应默认拥有字段权限 {contract.perm}")
    return issues


def validate_fastapi_fixture(root: Path, contracts) -> list[str]:
    """校验 FastAPI 测试权限 fixture 收录了所有字段权限码。"""
    fixture_path = root / "fastapi/tests/fixtures/permissions.py"
    namespace = runpy.run_path(str(fixture_path))
    button_specs = namespace.get("BUTTON_SPECS", ())
    by_perm: dict[str, tuple[Any, ...]] = {spec[3]: spec for spec in button_specs}

    issues: list[str] = []
    for contract in contracts:
        spec = by_perm.get(contract.perm)
        if spec is None:
            issues.append(f"fastapi/tests/fixtures/permissions.py: 缺少字段权限码 {contract.perm}")
            continue
        if spec[0] != contract.key:
            issues.append(f"fastapi/tests/fixtures/permissions.py: {contract.perm} key 应为 {contract.key}")
        if spec[1] != contract.name:
            issues.append(f"fastapi/tests/fixtures/permissions.py: {contract.perm} 名称应为 {contract.name}")
    return issues


def find_role(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    """按名称查找 Django 初始角色。"""
    for row in rows:
        if row.get("model") == "system.roles" and row.get("fields", {}).get("name") == name:
            return row
    return {}


def load_field_permission_contracts(root: Path):
    """从仓库根目录加载字段权限码契约目录。"""
    import sys

    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.field_permission_contracts import (
        assert_field_permission_contract_catalog,
        iter_field_permission_contracts,
    )

    assert_field_permission_contract_catalog()
    return iter_field_permission_contracts()
