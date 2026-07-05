# -*- coding: utf-8 -*-
"""
系统管理 - 用户接口测试
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Permissions, Roles, Users
from drf_admin.apps.system.test_helpers import create_admin_user


def create_scoped_user_permission_role(data_scope, dept=None):
    """创建带用户查询权限的数据范围角色。"""
    role = Roles.objects.create(
        name=f"数据范围角色{data_scope}",
        code=f"scope_role_{data_scope}",
        status=1,
        data_scope=data_scope,
    )
    permission, _ = Permissions.objects.get_or_create(
        perm="system:users:query",
        defaults={"name": "system:users:query", "type": "BUTTON"},
    )
    role.permissions.add(permission)
    if dept is not None:
        role.data_depts.add(dept)
    return role


class UsersListTestCase(TestCase):
    """用户列表接口测试"""

    def setUp(self):
        cache.clear()
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

    def test_dept_data_scope_filters_users(self):
        """部门数据范围用户只能看到本部门用户。"""
        visible_dept = Departments.objects.create(name="可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="隐藏部门", status=1, sort=2)
        role = create_scoped_user_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="scoped_admin",
            password="admin123",
            name="范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        visible_user = Users.objects.create_user(
            username="visible_user",
            password="admin123",
            name="可见用户",
            dept=visible_dept,
            is_active=1,
        )
        hidden_user = Users.objects.create_user(
            username="hidden_user",
            password="admin123",
            name="隐藏用户",
            dept=hidden_dept,
            is_active=1,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.get("/api/v1/system/users/", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item["username"] for item in response.data["data"]["list"]}
        self.assertIn(visible_user.username, usernames)
        self.assertNotIn(hidden_user.username, usernames)

    def test_sensitive_user_fields_are_masked_without_plain_permission(self):
        """无字段原文权限时，用户手机号和邮箱应脱敏但字段仍保留。"""
        Users.objects.create_user(
            username="sensitive_user",
            password="admin123",
            name="敏感用户",
            mobile="13800138000",
            email="sensitive@example.com",
            is_active=1,
        )

        response = self.client.get(
            "/api/v1/system/users/",
            {"pageNum": 1, "pageSize": 20, "search": "sensitive_user"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["mobile"], "138****8000")
        self.assertEqual(item["email"], "s********@example.com")

    def test_sensitive_user_fields_keep_plain_with_permission(self):
        """拥有字段原文权限时，用户手机号和邮箱返回原文。"""
        role = self.user.roles.first()
        permission, _ = Permissions.objects.get_or_create(
            perm="system:users:field:plain",
            defaults={"name": "system:users:field:plain", "type": "BUTTON"},
        )
        role.permissions.add(permission)
        cache.delete(f"user_info_{self.user.id}_perms")
        Users.objects.create_user(
            username="plain_user",
            password="admin123",
            name="原文字段用户",
            mobile="13800138001",
            email="plain@example.com",
            is_active=1,
        )

        response = self.client.get(
            "/api/v1/system/users/",
            {"pageNum": 1, "pageSize": 20, "search": "plain_user"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["mobile"], "13800138001")
        self.assertEqual(item["email"], "plain@example.com")


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
        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/password/reset/",
            {"password": "Newpass123", "confirm_password": "Newpass123"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


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
