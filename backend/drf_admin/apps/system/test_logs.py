# -*- coding: utf-8 -*-
"""
系统管理 - 操作日志接口与落库中间件测试
"""
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import OperationLog, Permissions, Roles
from drf_admin.apps.system.test_helpers import create_admin_user


def grant_log_permissions(user):
    """给测试用户授予操作日志权限码。"""
    role = user.roles.first()
    if role is None:
        role, _ = Roles.objects.get_or_create(name="日志角色", code="log", defaults={"status": 1})
        user.roles.add(role)
    for code in ("system:logs:query", "system:logs:delete"):
        permission, _ = Permissions.objects.get_or_create(
            perm=code, defaults={"name": code, "type": "BUTTON"}
        )
        role.permissions.add(permission)
    # RBAC 权限有进程级缓存，授权后需清除，避免跨用例脏读
    cache.delete(f"user_info_{user.id}_perms")


class OperationLogPersistenceTestCase(TestCase):
    """写操作落库行为测试。"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_post_request_is_persisted(self):
        """POST 写操作必须落库一条操作日志，并记录用户与方法。"""
        before = OperationLog.objects.count()
        self.client.post(
            "/api/v1/system/dicts/",
            {"name": "测试字典", "dictCode": "test_log_dict", "status": 1},
            format="json",
        )
        logs = OperationLog.objects.filter(method="POST", path__contains="/system/dicts")
        self.assertTrue(logs.exists())
        self.assertGreater(OperationLog.objects.count(), before)
        log = logs.first()
        self.assertEqual(log.username, self.user.username)

    def test_get_request_is_not_persisted(self):
        """GET 读请求不落库，避免审计表被轮询淹没。"""
        self.client.get("/api/v1/system/dicts/")
        self.assertFalse(OperationLog.objects.filter(method="GET").exists())


class OperationLogPageTestCase(TestCase):
    """操作日志查询端点测试。"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        grant_log_permissions(self.user)
        self.client.force_authenticate(user=self.user)
        for index in range(3):
            OperationLog.objects.create(
                username="admin", operation=f"创建用户{index}", method="POST",
                path=f"/api/v1/system/users/{index}", status=1, execution_time=10,
            )
        OperationLog.objects.create(
            username="admin", operation="删除角色", method="DELETE",
            path="/api/v1/system/roles/1", status=0, execution_time=20,
        )

    def test_page_returns_list_total_and_camel_fields(self):
        """分页结构为 list/total，且字段含 createdAt（对齐前端 LogPageVO）。"""
        response = self.client.get("/api/v1/system/logs/page", {"pageNum": 1, "pageSize": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertEqual(data["total"], 4)
        self.assertIn("createdAt", data["list"][0])
        self.assertIn("executionTime", data["list"][0])

    def test_page_filters_by_operation_keyword(self):
        """按 operation 关键字过滤。"""
        response = self.client.get("/api/v1/system/logs/page", {"operation": "删除"})
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["list"][0]["operation"], "删除角色")

    def test_page_pagination_navigates_second_page(self):
        """pageNum 驱动真实翻页。"""
        first = self.client.get("/api/v1/system/logs/page", {"pageNum": 1, "pageSize": 2}).json()["data"]
        second = self.client.get("/api/v1/system/logs/page", {"pageNum": 2, "pageSize": 2}).json()["data"]
        self.assertEqual(first["total"], 4)
        self.assertEqual(len(first["list"]), 2)
        self.assertEqual(len(second["list"]), 2)
        first_ids = {row["id"] for row in first["list"]}
        second_ids = {row["id"] for row in second["list"]}
        self.assertTrue(first_ids.isdisjoint(second_ids))

    def test_visit_stats_shape(self):
        """访问统计返回汇总字段。"""
        data = self.client.get("/api/v1/system/logs/visit-stats").json()["data"]
        self.assertEqual(data["totalCount"], 4)
        self.assertEqual(data["successCount"], 3)
        self.assertEqual(data["failCount"], 1)
        self.assertIn("topUsers", data)

    def test_visit_trend_shape(self):
        """访问趋势返回按日聚合列表。"""
        data = self.client.get("/api/v1/system/logs/visit-trend").json()["data"]
        self.assertIsInstance(data, list)
        self.assertTrue(all("date" in row and "count" in row for row in data))

    def test_delete_logs_by_ids(self):
        """按 ID 批量删除日志（删除操作本身也会被审计，故按目标 ID 校验）。"""
        ids_to_delete = [log.id for log in OperationLog.objects.all()[:2]]
        self.client.delete(f"/api/v1/system/logs/{','.join(str(i) for i in ids_to_delete)}")
        self.assertFalse(OperationLog.objects.filter(id__in=ids_to_delete).exists())


class OperationLogPermissionTestCase(TestCase):
    """操作日志权限校验测试。"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()  # 未授予 system:logs:query
        self.client.force_authenticate(user=self.user)

    def test_page_requires_logs_query_permission(self):
        """缺少 system:logs:query 时拒绝访问。"""
        response = self.client.get("/api/v1/system/logs/page")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
