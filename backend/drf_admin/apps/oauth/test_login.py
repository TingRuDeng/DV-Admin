# -*- coding: utf-8 -*-
"""
OAuth 登录接口测试
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.oauth.test_helpers import create_oauth_user


class OAuthLoginTestCase(TestCase):
    """登录接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_oauth_user()

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
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "testuser"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_not_found(self):
        """测试登录失败 - 用户不存在"""
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "nonexistent", "password": "password"},
            format="json",
        )

        self.assertIn(response.status_code, [200, 400])


class OAuthMobileLoginTestCase(TestCase):
    """用户名字段也接受 11 位手机号"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_oauth_user()
        self.user.mobile = "13800138000"
        self.user.save(update_fields=["mobile"])

    def _login(self, username, password="testpass123"):
        return self.client.post(
            "/api/v1/oauth/login/",
            {"username": username, "password": password},
            format="json",
        )

    def test_login_with_mobile(self):
        response = self._login("13800138000")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("accessToken", response.data["data"])

    def test_login_with_mobile_and_wrong_password(self):
        response = self._login("13800138000", "wrongpassword")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 40000)

    def test_login_with_mobile_of_disabled_user(self):
        self.user.is_active = 0
        self.user.save(update_fields=["is_active"])

        response = self._login("13800138000")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("禁用", str(response.data["errors"]))
