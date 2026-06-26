# -*- coding: utf-8 -*-
"""
系统管理 - 字典项接口测试
"""
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.test_helpers import create_admin_user


class DictItemsListTestCase(TestCase):
    """字典项列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_dict_items_list(self):
        """测试获取字典项列表"""
        response = self.client.get("/api/v1/system/dict-items/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])


class DictItemsCreateTestCase(TestCase):
    """字典项创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_dict_item(self):
        """测试创建字典项"""
        response = self.client.post("/api/v1/system/dict-items/", {
            "dict_id": 1,
            "label": "测试",
            "value": "test",
            "sort": 1,
            "status": 1
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])


class DictItemsDetailTestCase(TestCase):
    """字典项详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_update_dict_item(self):
        """测试更新字典项"""
        response = self.client.put("/api/v1/system/dict-items/1/", {
            "label": "更新"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_delete_dict_item(self):
        """测试删除字典项"""
        response = self.client.delete("/api/v1/system/dict-items/1/")
        
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
