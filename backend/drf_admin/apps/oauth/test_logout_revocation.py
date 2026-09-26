# -*- coding: utf-8 -*-
"""
退出登录必须让当前会话的 Refresh Token 失效
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.oauth.test_helpers import create_oauth_user


class LogoutRevokesRefreshTokenTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.client = APIClient()
        self.user = create_oauth_user()
        self.access_token, self.refresh_token = self._login()

    def _login(self, username="testuser", password="testpass123"):
        response = self.client.post(
            "/api/v1/oauth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["data"]["accessToken"], response.data["data"]["refreshToken"]

    def _logout(self, access_token, body=None):
        return self.client.post(
            "/api/v1/oauth/logout/",
            body,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

    def _refresh(self, refresh_token):
        return self.client.post(
            "/api/v1/oauth/refresh-token/", {"refreshToken": refresh_token}, format="json"
        )

    def test_logout_with_refresh_token_blocks_later_refresh(self):
        response = self._logout(self.access_token, {"refreshToken": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._refresh(self.refresh_token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], 40002)

    def test_logout_without_body_still_succeeds(self):
        response = self._logout(self.access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_logout_ignores_malformed_refresh_token(self):
        response = self._logout(self.access_token, {"refreshToken": "not-a-jwt"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_cannot_revoke_another_users_refresh_token(self):
        create_oauth_user(username="otheruser", password="otherpass123")
        _other_access, other_refresh = self._login("otheruser", "otherpass123")

        response = self._logout(self.access_token, {"refreshToken": other_refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._refresh(other_refresh)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
