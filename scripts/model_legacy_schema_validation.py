from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LegacySchemaMarker:
    """历史 FastAPI 结构哨兵，防止旧表名或旧关联字段回流。"""

    relative_path: str
    snippet: str
    reason: str


LEGACY_SCHEMA_MARKERS: tuple[LegacySchemaMarker, ...] = (
    LegacySchemaMarker(
        "fastapi/app/db/models/system_dict.py",
        'table = "system_dict_data"',
        "字典主表已统一为 Django 表名 system_dicts",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/system_permission.py",
        'through="system_roles_permissions"',
        "角色权限关联表已统一为 Django 表名 system_roles_to_system_permissions",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/system_permission.py",
        'backward_key="role_id"',
        "角色权限关联字段已统一为 roles_id",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/system_permission.py",
        'forward_key="permission_id"',
        "角色权限关联字段已统一为 permissions_id",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/oauth.py",
        'through="system_users_roles"',
        "用户角色关联表已统一为 Django 表名 system_users_to_system_roles",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/oauth.py",
        'backward_key="user_id"',
        "用户角色关联字段已统一为 users_id",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/oauth.py",
        'forward_key="role_id"',
        "用户角色关联字段已统一为 roles_id",
    ),
    LegacySchemaMarker(
        "fastapi/app/db/models/system_dict.py",
        "is_default =",
        "字典项 FastAPI-only 字段 is_default 已移除",
    ),
)


def validate_legacy_schema_markers(root: Path) -> list[str]:
    """校验 FastAPI 模型没有重新引入需要显式迁移的历史旧结构。"""
    issues: list[str] = []
    for marker in LEGACY_SCHEMA_MARKERS:
        path = root / marker.relative_path
        if marker.snippet in path.read_text(encoding="utf-8"):
            issues.append(f"{marker.relative_path}: 发现历史旧结构 {marker.snippet!r}，{marker.reason}")
    return issues
