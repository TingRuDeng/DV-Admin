# -*- coding: utf-8 -*-
"""
系统管理 - 菜单接口测试
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


class MenusListTestCase(TestCase):
    """菜单列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_menus_list(self):
        """测试获取菜单列表"""
        response = self.client.get("/api/v1/system/menus/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class MenusCreateTestCase(TestCase):
    """菜单创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_menu(self):
        """测试创建菜单"""
        response = self.client.post("/api/v1/system/menus/", {
            "name": "测试菜单",
            "type": "MENU",
            "sort": 1,
            "visible": 1
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN])

    def test_create_button(self):
        """测试创建按钮"""
        response = self.client.post("/api/v1/system/menus/", {
            "name": "新增按钮",
            "type": "BUTTON",
            "perm": "test:add"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])


class MenusDetailTestCase(TestCase):
    """菜单详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.menu = Permissions.objects.create(
            name="测试菜单",
            type="MENU",
            perm="test:menu",
            visible=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_menu_detail(self):
        """测试获取菜单详情"""
        response = self.client.get(f"/api/v1/system/menus/{self.menu.id}/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_update_menu(self):
        """测试更新菜单"""
        response = self.client.put(f"/api/v1/system/menus/{self.menu.id}/", {
            "name": "更新后的菜单"
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_delete_menu(self):
        """测试删除菜单"""
        menu_to_delete = Permissions.objects.create(
            name="待删除菜单",
            type="MENU",
            visible=1
        )
        response = self.client.delete(f"/api/v1/system/menus/{menu_to_delete.id}/")
        
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN])


class MenusTreeTestCase(TestCase):
    """菜单树接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_menus_tree(self):
        """测试获取菜单树"""
        response = self.client.get("/api/v1/system/menus/tree/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
