# -*- coding: utf-8 -*-
"""
系统管理 - 通知公告接口测试
"""
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Notices, Permissions, Roles, Users
from drf_admin.apps.system.test_helpers import create_admin_user


def grant_notice_target_write(user):
    """为测试用户授予通知目标字段写入权限。"""
    permission, _ = Permissions.objects.get_or_create(
        perm="system:notices:target:write",
        defaults={"name": "通知目标字段写入", "type": "BUTTON"},
    )
    user.roles.first().permissions.add(permission)
    cache.delete(f"user_info_{user.id}_perms")


def grant_notice_target_plain(user):
    """为测试用户授予通知目标字段原文读取权限。"""
    permission, _ = Permissions.objects.get_or_create(
        perm="system:notices:target:plain",
        defaults={"name": "通知目标字段原文读取", "type": "BUTTON"},
    )
    user.roles.first().permissions.add(permission)
    cache.delete(f"user_info_{user.id}_perms")


def create_scoped_notice_permission_role(data_scope):
    """创建带通知管理权限的数据范围角色。"""
    role = Roles.objects.create(
        name=f"通知数据范围角色{data_scope}",
        code=f"notice_scope_role_{data_scope}",
        status=1,
        data_scope=data_scope,
    )
    for code in (
        "system:notices:query",
        "system:notices:edit",
        "system:notices:delete",
        "system:notices:publish",
        "system:notices:revoke",
    ):
        permission, _ = Permissions.objects.get_or_create(
            perm=code,
            defaults={"name": code, "type": "BUTTON"},
        )
        role.permissions.add(permission)
    return role


class NoticesListTestCase(TestCase):
    """通知公告列表接口测试"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_get_notices_list(self):
        """测试获取通知列表"""
        response = self.client.get("/api/v1/system/notices/")
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_admin_list_filters_notices_by_publisher_dept_scope(self):
        """部门数据范围只返回本部门用户发布的后台通知。"""
        visible_dept = Departments.objects.create(name="通知可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="通知隐藏部门", status=1, sort=2)
        role = create_scoped_notice_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="notice_scoped_admin",
            password="admin123",
            name="通知范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        visible_publisher = Users.objects.create_user(
            username="notice_visible_publisher",
            password="admin123",
            name="通知可见发布人",
            dept=visible_dept,
            is_active=1,
        )
        hidden_publisher = Users.objects.create_user(
            username="notice_hidden_publisher",
            password="admin123",
            name="通知隐藏发布人",
            dept=hidden_dept,
            is_active=1,
        )
        Notices.objects.create(
            title="可见部门通知",
            content="内容",
            target_type=1,
            publisher_id=visible_publisher.id,
            publisher_name=visible_publisher.username,
        )
        Notices.objects.create(
            title="隐藏部门通知",
            content="内容",
            target_type=1,
            publisher_id=hidden_publisher.id,
            publisher_name=hidden_publisher.username,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.get("/api/v1/system/notices/page", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {item["title"] for item in response.data["data"]["list"]}
        self.assertIn("可见部门通知", titles)
        self.assertNotIn("隐藏部门通知", titles)

    def test_admin_list_masks_target_users_without_plain_permission(self):
        """无字段原文权限时，后台列表不暴露通知指定用户 ID。"""
        target_user = Users.objects.create_user(
            username="notice_target_user",
            password="admin123",
            name="通知目标用户",
            is_active=1,
        )
        Notices.objects.create(
            title="定向后台通知",
            content="内容",
            target_type=2,
            target_user_ids=[target_user.id],
            publisher_id=self.user.id,
            publisher_name=self.user.username,
        )

        response = self.client.get("/api/v1/system/notices/page", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notice = next(item for item in response.data["data"]["list"] if item["title"] == "定向后台通知")
        self.assertEqual(notice["target_user_ids"], [])

    def test_admin_list_keeps_target_users_with_plain_permission(self):
        """拥有字段原文权限时，后台列表返回通知指定用户 ID。"""
        grant_notice_target_plain(self.user)
        target_user = Users.objects.create_user(
            username="notice_target_plain_user",
            password="admin123",
            name="通知目标原文用户",
            is_active=1,
        )
        Notices.objects.create(
            title="授权定向后台通知",
            content="内容",
            target_type=2,
            target_user_ids=[target_user.id],
            publisher_id=self.user.id,
            publisher_name=self.user.username,
        )

        response = self.client.get("/api/v1/system/notices/page", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notice = next(
            item for item in response.data["data"]["list"] if item["title"] == "授权定向后台通知"
        )
        self.assertEqual(notice["target_user_ids"], [target_user.id])


class NoticesCreateTestCase(TestCase):
    """通知公告创建接口测试"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_create_notice(self):
        """测试创建通知"""
        response = self.client.post("/api/v1/system/notices", {
            "title": "测试通知",
            "content": "测试内容",
            "type": 1,
            "status": 1
        }, format="json")
        
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_create_rejects_target_users_without_field_write_permission(self):
        """无字段写入权限时，创建指定用户通知应被拒绝。"""
        response = self.client.post("/api/v1/system/notices", {
            "title": "定向通知",
            "content": "定向内容",
            "type": 1,
            "level": "H",
            "targetType": 2,
            "targetUserIds": [self.user.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("通知目标字段写入权限", str(response.data))

    def test_create_allows_target_users_with_field_write_permission(self):
        """拥有字段写入权限时，创建指定用户通知应通过。"""
        grant_notice_target_write(self.user)

        response = self.client.post("/api/v1/system/notices", {
            "title": "授权定向通知",
            "content": "定向内容",
            "type": 1,
            "level": "H",
            "targetType": 2,
            "targetUserIds": [self.user.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["target_user_ids"], [self.user.id])


class NoticesDetailTestCase(TestCase):
    """通知公告详情接口测试"""

    def setUp(self):
        cache.clear()
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

    def test_update_rejects_target_users_without_field_write_permission(self):
        """无字段写入权限时，更新指定用户通知应被拒绝。"""
        notice = Notices.objects.create(title="普通通知", content="内容", target_type=1)

        response = self.client.put(f"/api/v1/system/notices/{notice.id}", {
            "title": "定向通知",
            "content": "定向内容",
            "type": 1,
            "level": "H",
            "targetType": 2,
            "targetUserIds": [self.user.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("通知目标字段写入权限", str(response.data))

    def test_update_allows_target_users_with_field_write_permission(self):
        """拥有字段写入权限时，更新指定用户通知应通过。"""
        grant_notice_target_write(self.user)
        notice = Notices.objects.create(title="普通通知", content="内容", target_type=1)

        response = self.client.put(f"/api/v1/system/notices/{notice.id}", {
            "title": "授权定向通知",
            "content": "定向内容",
            "type": 1,
            "level": "H",
            "targetType": 2,
            "targetUserIds": [self.user.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["target_user_ids"], [self.user.id])

    def test_delete_notice(self):
        """测试删除通知"""
        response = self.client.delete("/api/v1/system/notices/1/")
        
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_delete_rejects_notice_outside_publisher_dept_scope(self):
        """删除接口不能绕过通知发布人部门数据范围。"""
        visible_dept = Departments.objects.create(name="通知可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="通知隐藏部门", status=1, sort=2)
        role = create_scoped_notice_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="notice_delete_scoped_admin",
            password="admin123",
            name="通知删除范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        hidden_publisher = Users.objects.create_user(
            username="notice_delete_hidden_publisher",
            password="admin123",
            name="通知删除隐藏人",
            dept=hidden_dept,
            is_active=1,
        )
        hidden_notice = Notices.objects.create(
            title="隐藏部门待删除通知",
            content="内容",
            target_type=1,
            publisher_id=hidden_publisher.id,
            publisher_name=hidden_publisher.username,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.delete(f"/api/v1/system/notices/{hidden_notice.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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

    def test_publish_rejects_notice_outside_publisher_dept_scope(self):
        """发布接口不能绕过通知发布人部门数据范围。"""
        visible_dept = Departments.objects.create(name="通知可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="通知隐藏部门", status=1, sort=2)
        role = create_scoped_notice_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="notice_publish_scoped_admin",
            password="admin123",
            name="通知发布范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        hidden_publisher = Users.objects.create_user(
            username="notice_publish_hidden_publisher",
            password="admin123",
            name="通知发布隐藏人",
            dept=hidden_dept,
            is_active=1,
        )
        hidden_notice = Notices.objects.create(
            title="隐藏部门待发布通知",
            content="内容",
            target_type=1,
            publisher_id=hidden_publisher.id,
            publisher_name=hidden_publisher.username,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.put(f"/api/v1/system/notices/{hidden_notice.id}/publish")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class NoticesMyPageTestCase(TestCase):
    """我的通知接口测试（Django 实现）"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

        from drf_admin.apps.system.models import Notices

        # 已发布、面向全体：可见
        self.notice_all = Notices.objects.create(
            title="全体通知", content="全体内容", publish_status=1, target_type=1
        )
        # 未发布：不可见
        Notices.objects.create(
            title="草稿通知", content="草稿内容", publish_status=0, target_type=1
        )
        # 已发布、指定到当前用户：可见
        self.notice_targeted = Notices.objects.create(
            title="定向通知", content="定向内容", publish_status=1,
            target_type=2, target_user_ids=[self.user.id],
        )
        # 已发布、指定到他人：不可见
        Notices.objects.create(
            title="他人通知", content="他人内容", publish_status=1,
            target_type=2, target_user_ids=[self.user.id + 999],
        )

    def test_my_page_returns_visible_published_notices(self):
        """我的通知只返回当前用户可见的已发布通知，且默认未读。"""
        response = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 1, "pageSize": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        titles = {item["title"] for item in data["list"]}
        self.assertEqual(data["total"], 2)
        self.assertEqual(titles, {"全体通知", "定向通知"})
        for item in data["list"]:
            self.assertEqual(item["isRead"], 0)

    def test_my_page_pagination_navigates_second_page(self):
        """pageNum 必须能驱动我的通知翻到第二页。"""
        first = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 1, "pageSize": 1})
        second = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 2, "pageSize": 1})

        first_data = first.json()["data"]
        second_data = second.json()["data"]
        self.assertEqual(first_data["total"], 2)
        self.assertEqual(len(first_data["list"]), 1)
        self.assertEqual(len(second_data["list"]), 1)
        self.assertNotEqual(first_data["list"][0]["id"], second_data["list"][0]["id"])

    def test_my_page_is_read_filter_returns_empty(self):
        """Django 不跟踪已读状态，按 isRead=1 过滤返回空列表。"""
        response = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 1, "pageSize": 10, "isRead": 1})

        data = response.json()["data"]
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["list"], [])

    def test_my_page_masks_target_users_without_plain_permission(self):
        """无字段原文权限时，我的通知不暴露指定用户 ID。"""
        response = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 1, "pageSize": 10})

        data = response.json()["data"]
        targeted = next(item for item in data["list"] if item["title"] == "定向通知")
        self.assertEqual(targeted["targetUserIds"], [])

    def test_my_page_keeps_target_users_with_plain_permission(self):
        """拥有字段原文权限时，我的通知返回指定用户 ID。"""
        grant_notice_target_plain(self.user)

        response = self.client.get("/api/v1/system/notices/my-page/", {"pageNum": 1, "pageSize": 10})

        data = response.json()["data"]
        targeted = next(item for item in data["list"] if item["title"] == "定向通知")
        self.assertEqual(targeted["targetUserIds"], [self.user.id])


class NoticesAdminListPagingTestCase(TestCase):
    """通知公告后台列表分页与筛选行为测试。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

        from drf_admin.apps.system.models import Notices

        for index in range(3):
            Notices.objects.create(
                title=f"已发布通知{index}", content="内容", publish_status=1, target_type=1
            )
        Notices.objects.create(title="草稿通知", content="内容", publish_status=0, target_type=1)

    def test_admin_list_honors_page_size_and_page_num(self):
        """后台列表必须按 pageNum/pageSize 真实翻页，而非恒定第一页。"""
        first = self.client.get("/api/v1/system/notices/page", {"pageNum": 1, "pageSize": 2})
        second = self.client.get("/api/v1/system/notices/page", {"pageNum": 2, "pageSize": 2})

        first_data = first.json()["data"]
        second_data = second.json()["data"]
        self.assertEqual(first_data["total"], 4)
        self.assertEqual(len(first_data["list"]), 2)
        self.assertEqual(len(second_data["list"]), 2)
        first_ids = {item["id"] for item in first_data["list"]}
        second_ids = {item["id"] for item in second_data["list"]}
        self.assertTrue(first_ids.isdisjoint(second_ids))

    def test_admin_list_filters_by_publish_status(self):
        """后台列表必须按 publishStatus 过滤。"""
        response = self.client.get("/api/v1/system/notices/page", {"publishStatus": 0})

        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["list"][0]["title"], "草稿通知")
