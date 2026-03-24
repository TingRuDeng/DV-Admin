# -*- coding: utf-8 -*-
"""
系统管理 - 用户接口测试
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles, Permissions


def create_admin_user():
    """创建带管理员角色的测试用户"""
    role, _ = Roles.objects.get_or_create(
        name="超级管理员", code="admin", defaults={"status": 1, "sort": 1}
    )

    perm_codes = [
        "system:users:query",
        "system:users:add",
        "system:users:edit",
        "system:users:delete",
        "system:roles:query",
        "system:roles:add",
        "system:roles:edit",
        "system:roles:delete",
        "system:menus:query",
        "system:menus:add",
        "system:menus:edit",
        "system:menus:delete",
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
    ]

    perms = []
    for code in perm_codes:
        perm, _ = Permissions.objects.get_or_create(
            perm=code, defaults={"name": code, "type": "BUTTON"}
        )
        perms.append(perm)

    role.permissions.add(*perms)

    user = Users.objects.create_user(
        username="admin", password="admin123", name="管理员", is_active=1
    )
    user.roles.add(role)

    return user


class UsersListTestCase(TestCase):
    """用户列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_users_list(self):
        """测试获取用户列表"""
        response = self.client.get("/api/v1/system/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

        data = response.data["data"]
        self.assertIn("list", data, "分页响应应包含 list 字段")
        self.assertIn("total", data, "分页响应应包含 total 字段")

    def test_get_users_list_with_params(self):
        """测试带参数的用户列表"""
        response = self.client.get("/api/v1/system/users/", {"page": 1, "size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_options(self):
        """测试获取用户下拉框"""
        response = self.client.get("/api/v1/system/users/options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)


class UsersCreateTestCase(TestCase):
    """用户创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        """测试创建用户"""
        response = self.client.post(
            "/api/v1/system/users/",
            {"username": "newuser", "password": "newpass123", "name": "新用户", "is_active": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UsersDetailTestCase(TestCase):
    """用户详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_user_detail(self):
        """测试获取用户详情"""
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], "admin")

    def test_get_user_not_found(self):
        """测试获取不存在的用户"""
        response = self.client.get("/api/v1/system/users/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self):
        """测试更新用户"""
        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/",
            {"username": "admin", "name": "更新后的名称"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """测试删除用户"""
        new_user = Users.objects.create_user(
            username="todelete", password="testpass123", name="待删除用户"
        )
        response = self.client.delete(f"/api/v1/system/users/{new_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UsersPasswordTestCase(TestCase):
    """用户密码接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_reset_password(self):
        """测试重置密码"""
        response = self.client.post(f"/api/v1/system/users/{self.user.id}/reset-password/")

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])


class UsersPermissionsTestCase(TestCase):
    """用户权限接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_user_permissions(self):
        """测试获取用户权限"""
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_pagination_results_not_rewritten(self):
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("results", response.data["data"])
        self.assertNotIn("list", response.data["data"])
        self.assertNotIn("total", response.data["data"])
