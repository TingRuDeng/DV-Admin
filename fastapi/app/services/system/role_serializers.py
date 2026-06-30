"""角色服务输出转换 helper。"""

from typing import Any

from app.db.models.system import Permissions, Roles
from app.schemas.system import RoleOut, RoleUpdate, RoleWithPermissions

ROLE_MENU_TYPES = {"CATALOG", "MENU"}


def build_role_out(role: Roles, permission_ids: list[int] | None = None) -> RoleOut:
    """将角色模型转换为角色列表输出结构。"""
    return RoleOut(
        id=role.id,
        name=role.name,
        code=role.code,
        status=role.status,
        sort=role.sort,
        is_default=role.is_default,
        desc=role.desc,
        permissions=permission_ids or [],
        create_time=role.created_at,
        update_time=role.updated_at,
    )


def build_role_with_permissions(
    role: Roles,
    permission_ids: list[int],
) -> RoleWithPermissions:
    """将角色模型和权限 ID 转换为角色详情输出结构。"""
    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        code=role.code,
        status=role.status,
        sort=role.sort,
        is_default=role.is_default,
        desc=role.desc,
        permissions=permission_ids,
        create_time=role.created_at,
        update_time=role.updated_at,
    )


def build_role_update_fields(role_data: RoleUpdate) -> dict[str, Any]:
    """提取需要落库的角色更新字段，跳过未传入字段。"""
    update_fields: dict[str, Any] = {}
    for field_name in ("name", "code", "status", "sort", "is_default", "desc"):
        value = getattr(role_data, field_name)
        if value is not None:
            update_fields[field_name] = value
    return update_fields


def build_role_menu_items(permissions: list[Permissions]) -> list[dict[str, Any]]:
    """将角色权限转换为角色菜单列表，只保留目录和菜单。"""
    return [
        {
            "id": permission.id,
            "name": permission.name,
            "type": permission.type,
        }
        for permission in permissions
        if permission.type in ROLE_MENU_TYPES
    ]
