# -*- coding: utf-8 -*-
"""
OAuth 会话接口测试
"""

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework import status

from drf_admin.apps.oauth.test_helpers import (
    authenticated_client,
    create_oauth_user,
    create_role_with_permission,
)
from drf_admin.apps.system.models import Users


class OAuthInfoTestCase(TestCase):
    """用户信息接口测试"""

    def setUp(self):
        role = create_role_with_permission()
        self.user = create_oauth_user()
        self.user.roles.add(role)
        self.client = authenticated_client(self.user)

    def test_get_user_info(self):
        """测试获取用户信息"""
        response = self.client.get("/api/v1/oauth/info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_user_info_query_count(self):
        """测试用户信息接口查询次数不退化"""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/v1/oauth/info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_count = len(context.captured_queries)
        self.assertLessEqual(
            query_count,
            5,
            f"UserInfoView should use <=5 queries with prefetch, got {query_count}",
        )


class OAuthMenusTestCase(TestCase):
    """用户菜单接口测试"""

    def setUp(self):
        role = create_role_with_permission(
            permission_name="测试菜单",
            permission_code="test:menu",
            permission_type="MENU",
            route_name="TestMenu",
            route_path="/test",
        )
        self.user = create_oauth_user()
        self.user.roles.add(role)
        self.client = authenticated_client(self.user)

    def test_get_user_menus(self):
        """测试获取用户菜单"""
        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIsInstance(response.data["data"], list)

    def test_get_user_menus_with_disabled_user(self):
        """测试禁用用户不能获取菜单"""
        self.user.is_active = 0
        self.user.save(update_fields=["is_active"])

        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)
        self.assertIn("用户已被禁用", str(response.data["errors"]))

    def test_get_user_menus_with_deleted_user(self):
        """测试已删除用户不能获取菜单"""
        stale_user = self.user
        Users.objects.filter(id=stale_user.id).delete()
        self.client.force_authenticate(user=stale_user)

        response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)
        self.assertIn("用户已被禁用", str(response.data["errors"]))

    def test_routes_query_count(self):
        """测试菜单接口查询次数不退化"""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/v1/oauth/menus/routes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_count = len(context.captured_queries)
        self.assertLessEqual(
            query_count,
            4,
            f"RoutesAPIView should use <=4 queries with prefetch, got {query_count}",
        )


class OAuthLogoutTestCase(TestCase):
    """登出接口测试"""

    def setUp(self):
        self.user = create_oauth_user()
        self.client = authenticated_client(self.user)

    def test_logout(self):
        """测试登出"""
        response = self.client.post("/api/v1/oauth/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("message", response.data["data"])
        self.assertNotIn("code", response.data["data"])
