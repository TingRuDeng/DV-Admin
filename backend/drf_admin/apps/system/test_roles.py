# -*- coding: utf-8 -*-
"""
系统管理 - 角色接口测试
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


class RolesListTestCase(TestCase):
    """角色列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_roles_list(self):
        """测试获取角色列表"""
        response = self.client.get("/api/v1/system/roles/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_get_roles_options(self):
        """测试获取角色下拉框"""
        response = self.client.get("/api/v1/system/roles/options/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)


class RolesCreateTestCase(TestCase):
    """角色创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_role(self):
        """测试创建角色"""
        response = self.client.post("/api/v1/system/roles/", {
            "name": "测试角色",
            "code": "test_role",
            "sort": 1,
            "status": 1
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RolesDetailTestCase(TestCase):
    """角色详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.role = Roles.objects.create(
            name="测试角色",
            code="test_role",
            sort=1,
            status=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_role_detail(self):
        """测试获取角色详情"""
        response = self.client.get(f"/api/v1/system/roles/{self.role.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_role(self):
        """测试更新角色"""
        response = self.client.put(f"/api/v1/system/roles/{self.role.id}/", {
            "name": "更新后的角色"
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_role(self):
        """测试删除角色"""
        role_to_delete = Roles.objects.create(
            name="待删除角色",
            code="to_delete",
            status=1
        )
        response = self.client.delete(f"/api/v1/system/roles/{role_to_delete.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RolesMenuTestCase(TestCase):
    """角色菜单接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.role = Roles.objects.create(
            name="测试角色",
            code="test_role",
            status=1
        )
        self.menu = Permissions.objects.create(
            name="测试菜单",
            type="MENU",
            perm="test:menu"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_role_menu_ids(self):
        """测试获取角色菜单ID列表"""
        response = self.client.get(f"/api/v1/system/roles/{self.role.id}/menuIds/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
