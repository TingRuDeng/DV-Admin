# -*- coding: utf-8 -*-
"""
OAuth 测试建数辅助函数
"""

from rest_framework.test import APIClient

from drf_admin.apps.system.models import Permissions, Roles, Users


def create_oauth_user(username="testuser", password="testpass123", name="测试用户"):
    """创建 OAuth 接口测试用户，统一默认凭据。"""
    return Users.objects.create_user(
        username=username,
        password=password,
        name=name,
        is_active=1,
    )


def create_role_with_permission(
    *,
    role_name="测试角色",
    role_code="test",
    permission_name="测试权限",
    permission_code="test:perm",
    permission_type="BUTTON",
    **permission_defaults,
):
    """创建带单个权限的角色，供用户信息和菜单测试复用。"""
    role = Roles.objects.create(name=role_name, code=role_code, status=1, sort=1)
    permission = Permissions.objects.create(
        name=permission_name,
        perm=permission_code,
        type=permission_type,
        **permission_defaults,
    )
    role.permissions.add(permission)
    return role


def authenticated_client(user):
    """返回已认证的 APIClient，避免每个会话类重复认证样板代码。"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client
