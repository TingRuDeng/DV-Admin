# -*- coding: utf-8 -*-
"""
OAuth 刷新 Token 接口测试
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.oauth.test_helpers import create_oauth_user


class OAuthRefreshTokenAPITestCase(TestCase):
    """刷新 Token 接口测试，保持 FastAPI 兼容格式"""

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.client = APIClient()
        self.user = create_oauth_user()
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data["data"].get("accessToken")
        self.refresh_token = response.data["data"].get("refreshToken")
        self.assertTrue(self.refresh_token)

    def test_refresh_token_with_query_param(self):
        """测试使用 query parameter 刷新 Token"""
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
        self.assertEqual(response.data["code"], 40002)

    def test_refresh_token_is_rotated_and_cannot_be_replayed(self):
        """刷新成功后旧 refresh token 必须立即失效。"""
        response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refreshToken": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rotated_refresh_token = response.data["data"]["refreshToken"]
        self.assertNotEqual(rotated_refresh_token, self.refresh_token)

        replay_response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refreshToken": self.refresh_token},
            format="json",
        )
        self.assertEqual(replay_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(replay_response.data["code"], 40002)

        rotated_response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refreshToken": rotated_refresh_token},
            format="json",
        )
        self.assertEqual(rotated_response.status_code, status.HTTP_200_OK)

    def test_password_change_invalidates_existing_access_token(self):
        """密码变更后旧 access token 必须立即失效。"""
        self.user.set_password("Newpass123")
        self.user.save(update_fields=["password"])

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = client.get("/api/v1/oauth/info/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_invalidates_existing_refresh_token(self):
        """密码变更后旧 refresh token 不得继续轮换。"""
        self.user.set_password("Newpass123")
        self.user.save(update_fields=["password"])

        response = self.client.post(
            "/api/v1/oauth/refresh-token/",
            {"refreshToken": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], 40002)
