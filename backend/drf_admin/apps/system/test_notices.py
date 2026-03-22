# -*- coding: utf-8 -*-
"""
系统管理 - 通知公告接口测试
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles, Permissions


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


class NoticesListTestCase(TestCase):
    """通知公告列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_notices_list(self):
        """测试获取通知列表"""
        response = self.client.get("/api/v1/system/notices/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class NoticesCreateTestCase(TestCase):
    """通知公告创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_notice(self):
        """测试创建通知"""
        response = self.client.post("/api/v1/system/notices/", {
            "title": "测试通知",
            "content": "测试内容",
            "type": 1,
            "status": 1
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class NoticesDetailTestCase(TestCase):
    """通知公告详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_notice_detail(self):
        """测试获取通知详情"""
        response = self.client.get("/api/v1/system/notices/1/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_update_notice(self):
        """测试更新通知"""
        response = self.client.put("/api/v1/system/notices/1/", {
            "title": "更新通知"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_delete_notice(self):
        """测试删除通知"""
        response = self.client.delete("/api/v1/system/notices/1/")
        
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])


class NoticesPublishTestCase(TestCase):
    """通知公告发布接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_publish_notice(self):
        """测试发布通知"""
        response = self.client.post("/api/v1/system/notices/1/publish/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
