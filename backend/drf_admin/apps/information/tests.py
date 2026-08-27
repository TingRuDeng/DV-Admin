# -*- coding: utf-8 -*-
"""
个人中心接口测试
"""
import base64
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Users


class ProfileTestCase(TestCase):
    """个人信息接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """测试获取个人信息"""
        response = self.client.get("/api/v1/information/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertEqual(data["username"], self.user.username)
        self.assertIn("gender", data)
        self.assertIn("deptName", data)
        self.assertIn("roleNames", data)

    def test_update_profile(self):
        """共享 profile 路径必须真实更新 Django 用户资料。"""
        response = self.client.put("/api/v1/information/profile/", {
            "name": "更新后的名称",
            "email": "updated@example.com",
            "gender": 2,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "更新后的名称")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.gender, 2)


class PasswordTestCase(TestCase):
    """密码修改接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password(self):
        """共享 password 路径与字段必须真实修改密码。"""
        response = self.client.put("/api/v1/information/password", {
            "oldPassword": "testpass123",
            "newPassword": "newpass123",
            "confirmPassword": "newpass123",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_legacy_change_password_path_and_fields_remain_compatible(self):
        """旧 Django 路径与字段保留兼容，避免已部署客户端立即失效。"""
        response = self.client.put("/api/v1/information/change-password/", {
            "currentPassword": "testpass123",
            "password": "legacy123",
            "confirmPassword": "legacy123",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("legacy123"))


class AvatarTestCase(TestCase):
    """头像修改接口测试"""

    def setUp(self):
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()

    def test_change_avatar(self):
        """共享 file 字段必须上传头像并返回可展示 URL。"""
        image = SimpleUploadedFile(
            "avatar.gif",
            base64.b64decode("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="),
            content_type="image/gif",
        )

        response = self.client.post(
            "/api/v1/information/change-avatar/",
            {"file": image},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertTrue(data["avatar"].startswith("avatar/"))
        self.assertIn("/media/avatar/", data["url"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.image.name, data["avatar"])
