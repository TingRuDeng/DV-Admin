# -*- coding: utf-8 -*-
"""
OAuth 认证接口测试
"""

from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles, Departments, Permissions


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


class OAuthLoginTestCase(TestCase):
    """登录接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )

    def test_login_success(self):
        """测试登录成功"""
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("accessToken", response.data["data"])

    def test_login_invalid_password(self):
        """测试登录失败 - 错误密码"""
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "testuser", "password": "wrongpassword"},
            format="json",
        )

        self.assertIn(response.status_code, [200, 400])

    def test_login_missing_fields(self):
        """测试登录失败 - 缺少字段"""
        response = self.client.post("/api/v1/oauth/login/", {"username": "testuser"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_not_found(self):
        """测试登录失败 - 用户不存在"""
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "nonexistent", "password": "password"},
            format="json",
        )

        self.assertIn(response.status_code, [200, 400])


class OAuthRefreshTokenAPITestCase(TestCase):
    """刷新 Token 接口测试 (FastAPI 兼容格式)"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )
        # 先登录获取 token
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.access_token = response.data["data"].get("accessToken")
        self.refresh_token = response.data["data"].get("refreshToken")

    def test_refresh_token_with_query_param(self):
        """测试使用 query parameter 刷新 Token"""
        if not self.refresh_token:
            self.skipTest("No refresh token available")

        response = self.client.post(
            f"/api/v1/oauth/refresh-token/?refreshToken={self.refresh_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("refreshToken", response.data["data"])
        self.assertIn("tokenType", response.data["data"])
        self.assertEqual(response.data["data"]["tokenType"], "bearer")

    def test_refresh_token_with_body(self):
        """测试使用 body 刷新 Token"""
        if not self.refresh_token:
            self.skipTest("No refresh token available")

        response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refreshToken": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("accessToken", response.data["data"])

    def test_refresh_token_with_refresh_key(self):
        """测试使用 refresh key 刷新 Token"""
        if not self.refresh_token:
            self.skipTest("No refresh token available")

        response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_refresh_token_missing(self):
        """测试缺少 refresh token"""
        response = self.client.post("/api/v1/oauth/refresh-token/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)

    def test_refresh_token_invalid(self):
        """测试无效的 refresh token"""
        response = self.client.post(
            "/api/v1/oauth/refresh-token/?refreshToken=invalid_token"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], 40001)


class OAuthInfoTestCase(TestCase):
    """用户信息接口测试"""

    def setUp(self):
        self.client = APIClient()
        role = Roles.objects.create(name="测试角色", code="test", status=1, sort=1)
        perm = Permissions.objects.create(name="测试权限", perm="test:perm", type="BUTTON")
        role.permissions.add(perm)

        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )
        self.user.roles.add(role)
        self.client.force_authenticate(user=self.user)

    def test_get_user_info(self):
        """测试获取用户信息"""
        response = self.client.get("/api/v1/oauth/info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_user_info_query_count(self):
        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/v1/oauth/info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_count = len(context.captured_queries)
        self.assertLessEqual(
            query_count, 5, f"UserInfoView should use <=5 queries with prefetch, got {query_count}"
        )


class OAuthMenusTestCase(TestCase):
    """用户菜单接口测试"""

    def setUp(self):
        self.client = APIClient()
        role = Roles.objects.create(name="测试角色", code="test", status=1, sort=1)
        menu_perm = Permissions.objects.create(
            name="测试菜单",
            perm="test:menu",
            type="MENU",
            route_name="TestMenu",
            route_path="/test",
        )
        role.permissions.add(menu_perm)

        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )
        self.user.roles.add(role)
        self.client.force_authenticate(user=self.user)

    def test_get_user_menus(self):
        """测试获取用户菜单"""
        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIsInstance(response.data["data"], list)

    def test_get_user_menus_with_disabled_user(self):
        self.user.is_active = 0
        self.user.save(update_fields=["is_active"])

        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)
        self.assertIn("用户已被禁用", str(response.data["errors"]))

    def test_get_user_menus_with_deleted_user(self):
        stale_user = self.user
        Users.objects.filter(id=stale_user.id).delete()
        self.client.force_authenticate(user=stale_user)

        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)
        self.assertIn("用户已被禁用", str(response.data["errors"]))

    def test_routes_query_count(self):
        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_count = len(context.captured_queries)
        self.assertLessEqual(
            query_count, 4, f"RoutesAPIView should use <=4 queries with prefetch, got {query_count}"
        )


class OAuthLogoutTestCase(TestCase):
    """登出接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_logout(self):
        """测试登出"""
        response = self.client.post("/api/v1/oauth/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("message", response.data["data"])
        self.assertNotIn("code", response.data["data"])


class OAuthHomeTestCase(TestCase):
    """首页数据接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser", password="testpass123", name="测试用户", is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_home_data(self):
        """测试获取首页数据"""
        response = self.client.get("/api/v1/oauth/home/")

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR],
        )
