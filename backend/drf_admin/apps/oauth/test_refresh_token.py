# -*- coding: utf-8 -*-
"""
OAuth 刷新 Token 接口测试
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.oauth.test_helpers import create_oauth_user


class OAuthRefreshTokenAPITestCase(TestCase):
    """刷新 Token 接口测试，保持 FastAPI 兼容格式"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_oauth_user()
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
