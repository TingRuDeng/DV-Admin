# -*- coding: utf-8 -*-
"""
系统管理测试辅助函数
"""

from drf_admin.apps.system.models import Permissions, Roles, Users

ADMIN_PERMISSION_CODES = (
    "system:users:query",
    "system:users:add",
    "system:users:edit",
    "system:users:delete",
    "system:roles:query",
    "system:roles:add",
    "system:roles:edit",
    "system:roles:delete",
    "system:permissions:query",
    "system:permissions:add",
    "system:permissions:edit",
    "system:permissions:delete",
    "system:departments:query",
    "system:departments:add",
    "system:departments:edit",
    "system:departments:delete",
    "system:dicts:query",
    "system:dicts:add",
    "system:dicts:edit",
    "system:dicts:delete",
    "system:notices:query",
    "system:notices:add",
    "system:notices:edit",
    "system:notices:delete",
)


def create_admin_user():
    """创建带完整 system 按钮权限的管理员测试用户。"""
    role, _ = Roles.objects.get_or_create(
        name="超级管理员",
        code="admin",
        defaults={"status": 1, "sort": 1},
    )

    permissions = []
    for code in ADMIN_PERMISSION_CODES:
        permission, _ = Permissions.objects.get_or_create(
            perm=code,
            defaults={"name": code, "type": "BUTTON"},
        )
        permissions.append(permission)

    role.permissions.add(*permissions)
    user = Users.objects.create_user(
        username="admin",
        password="admin123",
        name="管理员",
        is_active=1,
    )
    user.roles.add(role)
    return user
