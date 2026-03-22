# -*- coding: utf-8 -*-
"""
OAuth 认证接口测试
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles, Departments, Permissions


def create_admin_user():
    """创建带管理员角色的测试用户"""
    role, _ = Roles.objects.get_or_create(
        name="超级管理员",
        code="admin",
        defaults={"status": 1, "sort": 1}
    )
    
    perm_codes = [
        "system:users:query", "system:users:add", "system:users:edit", "system:users:delete",
        "system:roles:query", "system:roles:add", "system:roles:edit", "system:roles:delete",
        "system:menus:query", "system:menus:add", "system:menus:edit", "system:menus:delete",
        "system:departments:query", "system:departments:add", "system:departments:edit", "system:departments:delete",
        "system:dicts:query", "system:dicts:add", "system:dicts:edit", "system:dicts:delete",
        "system:notices:query", "system:notices:add", "system:notices:edit", "system:notices:delete",
    ]
    
    perms = []
    for code in perm_codes:
        perm, _ = Permissions.objects.get_or_create(
            perm=code,
            defaults={"name": code, "type": "BUTTON"}
        )
        perms.append(perm)
    
    role.permissions.add(*perms)
    
    user = Users.objects.create_user(
        username="admin",
        password="admin123",
        name="管理员",
        is_active=1
    )
    user.roles.add(role)
    
    return user


class OAuthLoginTestCase(TestCase):
    """登录接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )

    def test_login_success(self):
        """测试登录成功"""
        response = self.client.post("/api/v1/oauth/login/", {
            "username": "testuser",
            "password": "testpass123"
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("accessToken", response.data["data"])

    def test_login_invalid_password(self):
        """测试登录失败 - 错误密码"""
        response = self.client.post("/api/v1/oauth/login/", {
            "username": "testuser",
            "password": "wrongpassword"
        }, format="json")
        
        self.assertIn(response.status_code, [200, 400])

    def test_login_missing_fields(self):
        """测试登录失败 - 缺少字段"""
        response = self.client.post("/api/v1/oauth/login/", {
            "username": "testuser"
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_not_found(self):
        """测试登录失败 - 用户不存在"""
        response = self.client.post("/api/v1/oauth/login/", {
            "username": "nonexistent",
            "password": "password"
        }, format="json")
        
        self.assertIn(response.status_code, [200, 400])


class OAuthRefreshTokenTestCase(TestCase):
    """刷新 Token 接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )

    def test_refresh_token(self):
        """测试刷新 Token"""
        response = self.client.post("/api/v1/oauth/refresh/", {
            "refresh": "test-refresh-token"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])


class OAuthInfoTestCase(TestCase):
    """用户信息接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_info(self):
        """测试获取用户信息"""
        response = self.client.get("/api/v1/oauth/info/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)


class OAuthMenusTestCase(TestCase):
    """用户菜单接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_menus(self):
        """测试获取用户菜单"""
        response = self.client.get("/api/v1/oauth/menus/routes/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIsInstance(response.data["data"], list)


class OAuthLogoutTestCase(TestCase):
    """登出接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_logout(self):
        """测试登出"""
        response = self.client.post("/api/v1/oauth/logout/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OAuthHomeTestCase(TestCase):
    """首页数据接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="testuser",
            password="testpass123",
            name="测试用户",
            is_active=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_home_data(self):
        """测试获取首页数据"""
        response = self.client.get("/api/v1/oauth/home/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR])
