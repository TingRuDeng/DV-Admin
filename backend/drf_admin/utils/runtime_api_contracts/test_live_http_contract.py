"""Django 真实监听端口的共享业务 HTTP smoke。"""

from __future__ import annotations

import base64
import os
import tempfile
import unittest

import requests
from django.test import LiveServerTestCase, override_settings
from scripts.real_backend_playwright import run_real_backend_playwright

from drf_admin.apps.system.models import NoticeReads, Notices
from drf_admin.utils.runtime_api_contracts.helpers import create_runtime_contract_user


class DjangoLiveHttpContractTestCase(LiveServerTestCase):
    """绕过进程内 APIClient，验证真实 WSGI HTTP 链路。"""

    @classmethod
    def setUpClass(cls):
        cls.media_root = tempfile.TemporaryDirectory()
        cls.settings_override = override_settings(MEDIA_ROOT=cls.media_root.name)
        cls.settings_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.settings_override.disable()
        cls.media_root.cleanup()

    def setUp(self):
        self.user = create_runtime_contract_user()
        self.notice = Notices.objects.create(
            title="Django 真实 HTTP 通知",
            content="Django 真实 HTTP 正文",
            target_type=1,
            publish_status=1,
            publisher_id=self.user.id,
            publisher_name=self.user.username,
        )

    def test_shared_profile_avatar_password_and_notice_flow_over_http(self):
        session = requests.Session()
        session.headers["Accept"] = "application/json"

        login = session.post(
            f"{self.live_server_url}/api/v1/oauth/login/",
            json={"username": self.user.username, "password": "testpass123"},
            timeout=10,
        )
        access_token = self.assert_success(login)["accessToken"]
        session.headers["Authorization"] = f"Bearer {access_token}"

        profile = session.get(
            f"{self.live_server_url}/api/v1/information/profile/",
            timeout=10,
        )
        self.assertEqual(self.assert_success(profile)["username"], self.user.username)

        update = session.put(
            f"{self.live_server_url}/api/v1/information/profile/",
            json={"name": "Django HTTP 已更新", "gender": 2},
            timeout=10,
        )
        self.assertEqual(self.assert_success(update)["name"], "Django HTTP 已更新")

        avatar = session.post(
            f"{self.live_server_url}/api/v1/information/change-avatar/",
            files={
                "file": (
                    "avatar.gif",
                    base64.b64decode("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="),
                    "image/gif",
                ),
            },
            timeout=10,
        )
        self.assertIn("/media/avatar/", self.assert_success(avatar)["url"])

        my_page = session.get(
            f"{self.live_server_url}/api/v1/system/notices/my-page/",
            params={"pageNum": 1, "pageSize": 10, "isRead": 0},
            timeout=10,
        )
        self.assertIn(
            self.notice.id,
            {item["id"] for item in self.assert_success(my_page)["list"]},
        )

        detail = session.get(
            f"{self.live_server_url}/api/v1/system/notices/{self.notice.id}/detail",
            timeout=10,
        )
        self.assertEqual(self.assert_success(detail)["id"], self.notice.id)
        self.assertTrue(
            NoticeReads.objects.filter(notice=self.notice, user_id=self.user.id).exists()
        )

        password = session.put(
            f"{self.live_server_url}/api/v1/information/password",
            json={
                "oldPassword": "testpass123",
                "newPassword": "httpPass456",
                "confirmPassword": "httpPass456",
            },
            timeout=10,
        )
        self.assert_success(password)

        relogin = requests.post(
            f"{self.live_server_url}/api/v1/oauth/login/",
            json={"username": self.user.username, "password": "httpPass456"},
            timeout=10,
        )
        self.assertIn("accessToken", self.assert_success(relogin))

    @unittest.skipUnless(
        os.environ.get("RUN_REAL_BACKEND_PLAYWRIGHT") == "1",
        "仅在双后端真实浏览器 smoke 门禁中运行",
    )
    def test_shared_frontend_flow_over_real_django_http(self):
        """让真实 Vue 页面通过 Vite 代理连接当前 Django LiveServer。"""
        run_real_backend_playwright(
            backend_name="Django",
            backend_url=self.live_server_url,
            username=self.user.username,
            password="testpass123",
            notice_title=self.notice.title,
            notice_content=self.notice.content,
        )

    def assert_success(self, response):
        """断言真实 HTTP 响应满足 Django 成功信封并返回 data。"""
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["code"], 20000, payload)
        return payload["data"]
