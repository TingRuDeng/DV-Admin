# -*- coding: utf-8 -*-
"""
系统管理 - 用户接口测试
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Permissions, Roles, Users
from drf_admin.apps.system.test_helpers import create_admin_user


def create_scoped_user_permission_role(data_scope, dept=None, permission_codes=()):
    """创建带用户查询权限的数据范围角色。"""
    role = Roles.objects.create(
        name=f"数据范围角色{data_scope}",
        code=f"scope_role_{data_scope}",
        status=1,
        data_scope=data_scope,
    )
    permission, _ = Permissions.objects.get_or_create(
        perm="system:users:query",
        defaults={"name": "system:users:query", "type": "BUTTON"},
    )
    role.permissions.add(permission)
    for code in permission_codes:
        permission, _ = Permissions.objects.get_or_create(
            perm=code,
            defaults={"name": code, "type": "BUTTON"},
        )
        role.permissions.add(permission)
    if dept is not None:
        role.data_depts.add(dept)
    return role


def create_dept_scoped_user_context(permission_codes=()):
    """创建部门范围操作人与范围内外用户。"""
    visible_dept = Departments.objects.create(name="范围内部门", status=1, sort=1)
    hidden_dept = Departments.objects.create(name="范围外部门", status=1, sort=2)
    role = create_scoped_user_permission_role(
        Roles.DATA_SCOPE_DEPT,
        permission_codes=permission_codes,
    )
    operator = Users.objects.create_user(
        username="scope_operator",
        password="admin123",
        name="范围操作人",
        dept=visible_dept,
        is_active=1,
    )
    operator.roles.add(role)
    visible_user = Users.objects.create_user(
        username="scope_visible_user",
        password="admin123",
        name="范围内用户",
        dept=visible_dept,
        is_active=1,
    )
    hidden_user = Users.objects.create_user(
        username="scope_hidden_user",
        password="admin123",
        name="范围外用户",
        dept=hidden_dept,
        is_active=1,
    )
    return {
        "operator": operator,
        "visible_dept": visible_dept,
        "hidden_dept": hidden_dept,
        "visible_user": visible_user,
        "hidden_user": hidden_user,
    }


class UsersListTestCase(TestCase):
    """用户列表接口测试"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_users_list(self):
        """测试获取用户列表"""
        response = self.client.get("/api/v1/system/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

        data = response.data["data"]
        self.assertIn("list", data, "分页响应应包含 list 字段")
        self.assertIn("total", data, "分页响应应包含 total 字段")

    def test_get_users_list_with_params(self):
        """测试带参数的用户列表"""
        response = self.client.get("/api/v1/system/users/", {"page": 1, "size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_options(self):
        """测试获取用户下拉框"""
        response = self.client.get("/api/v1/system/users/options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)

    def test_dept_data_scope_filters_users(self):
        """部门数据范围用户只能看到本部门用户。"""
        visible_dept = Departments.objects.create(name="可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="隐藏部门", status=1, sort=2)
        role = create_scoped_user_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="scoped_admin",
            password="admin123",
            name="范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        visible_user = Users.objects.create_user(
            username="visible_user",
            password="admin123",
            name="可见用户",
            dept=visible_dept,
            is_active=1,
        )
        hidden_user = Users.objects.create_user(
            username="hidden_user",
            password="admin123",
            name="隐藏用户",
            dept=hidden_dept,
            is_active=1,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.get("/api/v1/system/users/", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item["username"] for item in response.data["data"]["list"]}
        self.assertIn(visible_user.username, usernames)
        self.assertNotIn(hidden_user.username, usernames)

    def test_user_options_follow_data_scope(self):
        """用户下拉选项不得泄露范围外用户。"""
        context = create_dept_scoped_user_context()
        self.client.force_authenticate(user=context["operator"])

        response = self.client.get("/api/v1/system/users/options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        option_ids = {item["id"] for item in response.data["data"]}
        self.assertIn(context["visible_user"].id, option_ids)
        self.assertNotIn(context["hidden_user"].id, option_ids)

    def test_sensitive_user_fields_are_masked_without_plain_permission(self):
        """无字段原文权限时，用户手机号和邮箱应脱敏但字段仍保留。"""
        Users.objects.create_user(
            username="sensitive_user",
            password="admin123",
            name="敏感用户",
            mobile="13800138000",
            email="sensitive@example.com",
            is_active=1,
        )

        response = self.client.get(
            "/api/v1/system/users/",
            {"pageNum": 1, "pageSize": 20, "search": "sensitive_user"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["mobile"], "138****8000")
        self.assertEqual(item["email"], "s********@example.com")

    def test_sensitive_user_fields_keep_plain_with_permission(self):
        """拥有字段原文权限时，用户手机号和邮箱返回原文。"""
        role = self.user.roles.first()
        permission, _ = Permissions.objects.get_or_create(
            perm="system:users:field:plain",
            defaults={"name": "system:users:field:plain", "type": "BUTTON"},
        )
        role.permissions.add(permission)
        cache.delete(f"user_info_{self.user.id}_perms")
        Users.objects.create_user(
            username="plain_user",
            password="admin123",
            name="原文字段用户",
            mobile="13800138001",
            email="plain@example.com",
            is_active=1,
        )

        response = self.client.get(
            "/api/v1/system/users/",
            {"pageNum": 1, "pageSize": 20, "search": "plain_user"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["mobile"], "13800138001")
        self.assertEqual(item["email"], "plain@example.com")


class UsersCreateTestCase(TestCase):
    """用户创建接口测试"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        """测试创建用户"""
        response = self.client.post(
            "/api/v1/system/users/",
            {"username": "newuser", "password": "newpass123", "name": "新用户", "is_active": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_rejects_sensitive_fields_without_write_permission(self):
        """无字段写入权限时，创建用户不得写入手机号和邮箱。"""
        response = self.client.post(
            "/api/v1/system/users/",
            {
                "username": "sensitive_create",
                "password": "newpass123",
                "name": "敏感创建",
                "mobile": "13800138010",
                "email": "sensitive-create@example.com",
                "is_active": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("字段写入权限", str(response.data))

    def test_create_user_allows_sensitive_fields_with_write_permission(self):
        """拥有字段写入权限时，创建用户可以写入手机号和邮箱。"""
        role = self.user.roles.first()
        permission, _ = Permissions.objects.get_or_create(
            perm="system:users:field:write",
            defaults={"name": "system:users:field:write", "type": "BUTTON"},
        )
        role.permissions.add(permission)
        cache.delete(f"user_info_{self.user.id}_perms")

        response = self.client.post(
            "/api/v1/system/users/",
            {
                "username": "plain_create",
                "password": "newpass123",
                "name": "允许创建",
                "mobile": "13800138011",
                "email": "plain-create@example.com",
                "is_active": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Users.objects.get(username="plain_create")
        self.assertEqual(created.mobile, "13800138011")
        self.assertEqual(created.email, "plain-create@example.com")

    def test_create_user_rejects_department_outside_data_scope(self):
        """受限操作人不得把新用户放入范围外部门。"""
        context = create_dept_scoped_user_context(("system:users:add",))
        self.client.force_authenticate(user=context["operator"])

        response = self.client.post(
            "/api/v1/system/users/",
            {
                "username": "hidden_dept_create",
                "name": "范围外创建",
                "deptId": context["hidden_dept"].id,
                "isActive": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("目标部门超出", str(response.data))
        self.assertFalse(Users.objects.filter(username="hidden_dept_create").exists())


class UsersDetailTestCase(TestCase):
    """用户详情接口测试"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_user_detail(self):
        """测试获取用户详情"""
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], "admin")

    def test_get_user_not_found(self):
        """测试获取不存在的用户"""
        response = self.client.get("/api/v1/system/users/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self):
        """测试更新用户"""
        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/",
            {"username": "admin", "name": "更新后的名称"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_rejects_sensitive_fields_without_write_permission(self):
        """无字段写入权限时，更新用户不得写入手机号和邮箱。"""
        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/",
            {
                "username": "admin",
                "name": "更新后的名称",
                "mobile": "13800138012",
                "email": "sensitive-update@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("字段写入权限", str(response.data))

    def test_update_user_allows_sensitive_fields_with_write_permission(self):
        """拥有字段写入权限时，更新用户可以写入手机号和邮箱。"""
        role = self.user.roles.first()
        permission, _ = Permissions.objects.get_or_create(
            perm="system:users:field:write",
            defaults={"name": "system:users:field:write", "type": "BUTTON"},
        )
        role.permissions.add(permission)
        cache.delete(f"user_info_{self.user.id}_perms")

        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/",
            {
                "username": "admin",
                "name": "允许更新",
                "mobile": "13800138013",
                "email": "plain-update@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.mobile, "13800138013")
        self.assertEqual(self.user.email, "plain-update@example.com")

    def test_delete_user(self):
        """测试删除用户"""
        new_user = Users.objects.create_user(
            username="todelete", password="testpass123", name="待删除用户"
        )
        response = self.client.delete(f"/api/v1/system/users/{new_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_hidden_user_detail_update_and_delete_return_not_found(self):
        """范围外用户的详情和写操作统一按不存在处理。"""
        context = create_dept_scoped_user_context(
            ("system:users:edit", "system:users:delete"),
        )
        self.client.force_authenticate(user=context["operator"])
        hidden_user = context["hidden_user"]

        self.assertEqual(
            self.client.get(f"/api/v1/system/users/{hidden_user.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        update_response = self.client.put(
            f"/api/v1/system/users/{hidden_user.id}/",
            {"username": hidden_user.username, "name": "越权更新"},
            format="json",
        )
        delete_response = self.client.delete(f"/api/v1/system/users/{hidden_user.id}/")

        self.assertEqual(update_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        hidden_user.refresh_from_db()
        self.assertEqual(hidden_user.name, "范围外用户")

    def test_update_user_rejects_department_outside_data_scope(self):
        """受限操作人不得把范围内用户移动到范围外部门。"""
        context = create_dept_scoped_user_context(("system:users:edit",))
        self.client.force_authenticate(user=context["operator"])
        visible_user = context["visible_user"]

        response = self.client.put(
            f"/api/v1/system/users/{visible_user.id}/",
            {
                "username": visible_user.username,
                "name": visible_user.name,
                "deptId": context["hidden_dept"].id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("目标部门超出", str(response.data))
        visible_user.refresh_from_db()
        self.assertEqual(visible_user.dept_id, context["visible_dept"].id)

    def test_batch_delete_is_atomic_across_data_scope(self):
        """批量目标混入范围外用户时全部拒绝。"""
        context = create_dept_scoped_user_context(("system:users:delete",))
        self.client.force_authenticate(user=context["operator"])

        response = self.client.delete(
            "/api/v1/system/users/",
            {
                "ids": [
                    context["visible_user"].id,
                    context["hidden_user"].id,
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Users.objects.filter(id=context["visible_user"].id).exists())
        self.assertTrue(Users.objects.filter(id=context["hidden_user"].id).exists())


class UsersPasswordTestCase(TestCase):
    """用户密码接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_reset_password(self):
        """测试重置密码"""
        response = self.client.put(
            f"/api/v1/system/users/{self.user.id}/password/reset/",
            {"password": "Newpass123", "confirm_password": "Newpass123"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_uses_dedicated_permission(self):
        """密码重置应只要求专用权限，不应错误复用用户编辑权限。"""
        context = create_dept_scoped_user_context(("system:users:password:reset",))
        self.client.force_authenticate(user=context["operator"])

        response = self.client.put(
            f"/api/v1/system/users/{context['visible_user'].id}/password/reset/",
            {"password": "LifecyclePass123", "confirm_password": "LifecyclePass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        context["visible_user"].refresh_from_db()
        self.assertTrue(context["visible_user"].check_password("LifecyclePass123"))

    def test_reset_password_hidden_user_returns_not_found(self):
        """不得重置范围外用户密码。"""
        context = create_dept_scoped_user_context(("system:users:password:reset",))
        self.client.force_authenticate(user=context["operator"])

        response = self.client.put(
            f"/api/v1/system/users/{context['hidden_user'].id}/password/reset/",
            {"password": "Newpass123", "confirm_password": "Newpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UsersPermissionsTestCase(TestCase):
    """用户权限接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_user_permissions(self):
        """测试获取用户权限"""
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_pagination_results_not_rewritten(self):
        response = self.client.get(f"/api/v1/system/users/{self.user.id}/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertIn("results", response.data["data"])
        self.assertNotIn("list", response.data["data"])
        self.assertNotIn("total", response.data["data"])

    def test_hidden_user_permissions_return_not_found(self):
        """不得通过权限详情探测范围外用户。"""
        context = create_dept_scoped_user_context()
        self.client.force_authenticate(user=context["operator"])

        response = self.client.get(
            f"/api/v1/system/users/{context['hidden_user'].id}/permissions/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
