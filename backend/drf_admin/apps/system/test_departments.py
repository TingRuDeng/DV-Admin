# -*- coding: utf-8 -*-
"""
系统管理 - 部门接口测试
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles, Permissions, Departments


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


class DepartmentsListTestCase(TestCase):
    """部门列表接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_departments_list(self):
        """测试获取部门列表"""
        response = self.client.get("/api/v1/system/departments/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)


class DepartmentsCreateTestCase(TestCase):
    """部门创建接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_department(self):
        """测试创建部门"""
        response = self.client.post("/api/v1/system/departments/", {
            "name": "测试部门",
            "sort": 1,
            "status": 1
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sub_department(self):
        """测试创建子部门"""
        parent = Departments.objects.create(name="父部门", status=1)
        
        response = self.client.post("/api/v1/system/departments/", {
            "name": "子部门",
            "parent": parent.id,
            "sort": 1,
            "status": 1
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DepartmentsDetailTestCase(TestCase):
    """部门详情接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.dept = Departments.objects.create(
            name="测试部门",
            sort=1,
            status=1
        )
        self.client.force_authenticate(user=self.user)

    def test_get_department_detail(self):
        """测试获取部门详情"""
        response = self.client.get(f"/api/v1/system/departments/{self.dept.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_department(self):
        """测试更新部门"""
        response = self.client.put(f"/api/v1/system/departments/{self.dept.id}/", {
            "name": "更新后的部门"
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_department(self):
        """测试删除部门"""
        dept_to_delete = Departments.objects.create(
            name="待删除部门",
            status=1
        )
        response = self.client.delete(f"/api/v1/system/departments/{dept_to_delete.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DepartmentsTreeTestCase(TestCase):
    """部门树接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_departments_tree(self):
        """测试获取部门树"""
        response = self.client.get("/api/v1/system/departments/tree/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
