# -*- coding: utf-8 -*-
"""
系统管理 - 操作日志接口与落库中间件测试
"""
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, OperationLog, Permissions, Roles, Users
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


def create_scoped_log_permission_role(data_scope):
    """创建带操作日志查询权限的数据范围角色。"""
    role = Roles.objects.create(
        name=f"日志数据范围角色{data_scope}",
        code=f"log_scope_role_{data_scope}",
        status=1,
        data_scope=data_scope,
    )
    permission, _ = Permissions.objects.get_or_create(
        perm="system:logs:query",
        defaults={"name": "system:logs:query", "type": "BUTTON"},
    )
    role.permissions.add(permission)
    return role


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

    def test_page_rejects_invalid_status(self):
        """无效 status 参数应返回 400，而不是抛出服务端异常。"""
        response = self.client.get("/api/v1/system/logs/page", {"status": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_page_rejects_invalid_pagination(self):
        """无效分页参数应返回 400，避免把外部输入转换错误暴露为 500。"""
        response = self.client.get("/api/v1/system/logs/page", {"pageNum": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dept_data_scope_filters_logs_by_actor_dept(self):
        """部门数据范围只返回本部门用户产生的操作日志。"""
        OperationLog.objects.all().delete()
        visible_dept = Departments.objects.create(name="日志可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="日志隐藏部门", status=1, sort=2)
        role = create_scoped_log_permission_role(Roles.DATA_SCOPE_DEPT)
        scoped_user = Users.objects.create_user(
            username="log_scoped_admin",
            password="admin123",
            name="日志范围管理员",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        visible_user = Users.objects.create_user(
            username="log_visible_user",
            password="admin123",
            name="日志可见用户",
            dept=visible_dept,
            is_active=1,
        )
        hidden_user = Users.objects.create_user(
            username="log_hidden_user",
            password="admin123",
            name="日志隐藏用户",
            dept=hidden_dept,
            is_active=1,
        )
        OperationLog.objects.create(
            user_id=visible_user.id,
            username=visible_user.username,
            operation="可见操作",
            method="POST",
            path="/api/visible",
            status=1,
        )
        OperationLog.objects.create(
            user_id=hidden_user.id,
            username=hidden_user.username,
            operation="隐藏操作",
            method="POST",
            path="/api/hidden",
            status=1,
        )
        self.client.force_authenticate(user=scoped_user)

        response = self.client.get("/api/v1/system/logs/page", {"pageNum": 1, "pageSize": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operations = {item["operation"] for item in response.data["data"]["list"]}
        self.assertIn("可见操作", operations)
        self.assertNotIn("隐藏操作", operations)

    def test_sensitive_log_fields_are_masked_without_plain_permission(self):
        """无字段原文权限时，日志请求体、响应体和 IP 应脱敏。"""
        OperationLog.objects.all().delete()
        OperationLog.objects.create(
            username="admin",
            operation="敏感日志",
            method="POST",
            path="/api/sensitive",
            request_body='{"password":"secret","mobile":"13800138000"}',
            response_body='{"token":"secret-token","ok":true}',
            ip="192.168.1.20",
            status=1,
        )

        response = self.client.get("/api/v1/system/logs/page", {"operation": "敏感日志"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["request_body"], "[已脱敏]")
        self.assertEqual(item["response_body"], "[已脱敏]")
        self.assertEqual(item["ip"], "192.168.1.*")

    def test_sensitive_log_fields_keep_plain_with_permission(self):
        """拥有字段原文权限时，日志敏感字段返回原文。"""
        role = self.user.roles.first()
        permission, _ = Permissions.objects.get_or_create(
            perm="system:logs:field:plain",
            defaults={"name": "system:logs:field:plain", "type": "BUTTON"},
        )
        role.permissions.add(permission)
        cache.delete(f"user_info_{self.user.id}_perms")
        OperationLog.objects.all().delete()
        OperationLog.objects.create(
            username="admin",
            operation="原文字段日志",
            method="POST",
            path="/api/plain",
            request_body='{"password":"secret"}',
            response_body='{"token":"secret-token"}',
            ip="10.0.0.8",
            status=1,
        )

        response = self.client.get("/api/v1/system/logs/page", {"operation": "原文字段日志"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["data"]["list"][0]
        self.assertEqual(item["request_body"], '{"password":"secret"}')
        self.assertEqual(item["response_body"], '{"token":"secret-token"}')
        self.assertEqual(item["ip"], "10.0.0.8")

    def test_visit_stats_shape(self):
        """访问统计返回汇总字段。"""
        data = self.client.get("/api/v1/system/logs/visit-stats").json()["data"]
        self.assertEqual(data["totalCount"], 4)
        self.assertEqual(data["successCount"], 3)
        self.assertEqual(data["failCount"], 1)
        self.assertIn("topUsers", data)

    def test_visit_stats_top_users_and_paths_cover_all_logs(self):
        """Top 统计应覆盖全量日志，不能只统计最近 1000 条。"""
        OperationLog.objects.all().delete()
        OperationLog.objects.bulk_create(
            [
                OperationLog(
                    username="历史高频用户",
                    operation="历史操作",
                    method="GET",
                    path="/api/history/hot",
                    status=1,
                    execution_time=20,
                )
                for _ in range(20)
            ]
        )
        OperationLog.objects.bulk_create(
            [
                OperationLog(
                    username=f"recent_user_{index}",
                    operation="近期操作",
                    method="GET",
                    path=f"/api/recent/{index}",
                    status=1,
                    execution_time=10,
                )
                for index in range(1000)
            ]
        )

        data = self.client.get("/api/v1/system/logs/visit-stats").json()["data"]

        self.assertEqual(data["totalCount"], 1020)
        self.assertEqual(data["avgExecutionTime"], 10)
        self.assertEqual(data["topUsers"][0], {"username": "历史高频用户", "count": 20})
        self.assertEqual(data["topPaths"][0], {"path": "/api/history/hot", "count": 20})

    def test_visit_trend_shape(self):
        """访问趋势返回按日聚合列表。"""
        data = self.client.get("/api/v1/system/logs/visit-trend").json()["data"]
        self.assertIsInstance(data, list)
        self.assertTrue(all("date" in row and "count" in row for row in data))

    def test_visit_trend_rejects_invalid_date(self):
        """访问趋势日期参数非法时应返回 400。"""
        response = self.client.get("/api/v1/system/logs/visit-trend", {"startDate": "not-a-date"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_logs_by_ids(self):
        """按 ID 批量删除日志（删除操作本身也会被审计，故按目标 ID 校验）。"""
        ids_to_delete = [log.id for log in OperationLog.objects.all()[:2]]
        self.client.delete(f"/api/v1/system/logs/{','.join(str(i) for i in ids_to_delete)}")
        self.assertFalse(OperationLog.objects.filter(id__in=ids_to_delete).exists())

    def test_delete_rejects_invalid_ids(self):
        """批量删除 ID 非法时应返回 400，不能抛出未处理 ValueError。"""
        response = self.client.delete("/api/v1/system/logs/1,invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
