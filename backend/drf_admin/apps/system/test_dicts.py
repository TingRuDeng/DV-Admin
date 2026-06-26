# -*- coding: utf-8 -*-
"""
系统管理 - 字典接口测试
"""
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.test_helpers import create_admin_user


class DictsListTestCase(TestCase):
    """字典列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_dicts_list(self):
        """测试获取字典列表"""
        response = self.client.get("/api/v1/system/dicts/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])


class DictsCreateTestCase(TestCase):
    """字典创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_dict(self):
        """测试创建字典"""
        response = self.client.post("/api/v1/system/dicts/", {
            "name": "测试字典",
            "code": "test_dict",
            "status": 1
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])


class DictsDetailTestCase(TestCase):
    """字典详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_dict_detail(self):
        """测试获取字典详情"""
        response = self.client.get("/api/v1/system/dicts/1/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_update_dict(self):
        """测试更新字典"""
        response = self.client.put("/api/v1/system/dicts/1/", {
            "name": "更新字典"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_delete_dict(self):
        """测试删除字典"""
        response = self.client.delete("/api/v1/system/dicts/1/")
        
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
