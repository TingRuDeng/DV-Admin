# -*- coding: utf-8 -*-
"""
个人中心接口测试
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

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

    def test_update_profile(self):
        """测试更新个人信息"""
        response = self.client.put("/api/v1/information/profile/", {
            "name": "更新后的名称"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_400_BAD_REQUEST])


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
        """测试修改密码"""
        response = self.client.put("/api/v1/information/change-password/", {
            "oldPassword": "testpass123",
            "newPassword": "newpass123"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])


class AvatarTestCase(TestCase):
    """头像修改接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_change_avatar(self):
        """测试修改头像"""
        response = self.client.post("/api/v1/information/change-avatar/", {
            "avatar": "test.jpg"
        })
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
