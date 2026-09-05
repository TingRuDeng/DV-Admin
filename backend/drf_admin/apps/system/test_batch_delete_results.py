"""批量删除逐条结果与重试契约测试。"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Notices, Permissions, Roles, Users
from drf_admin.apps.system.test_helpers import create_admin_user
from drf_admin.apps.system.views import notices as notices_views


class BatchDeleteResultTestCase(TestCase):
    """验证 Django 批量删除的部分成功响应。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)
        self.target = Users.objects.create_user(
            username="batch-result-target",
            password="admin123",
            name="可删除用户",
            is_active=1,
        )

    def test_user_batch_delete_returns_item_failures_without_blocking_other_items(self):
        """当前登录用户失败时，其他用户仍应成功删除并返回逐条结果。"""
        response = self.client.delete(
            "/api/v1/system/users/",
            {"ids": [self.user.id, self.target.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["status"], "partial_failed")
        self.assertEqual(result["totalCount"], 2)
        self.assertEqual(result["successCount"], 1)
        self.assertEqual(result["failedCount"], 1)
        self.assertEqual(result["processedCount"], 2)
        self.assertEqual(result["successItems"][0]["objectId"], str(self.target.id))
        self.assertEqual(result["failures"][0]["objectId"], str(self.user.id))
        self.assertEqual(result["failures"][0]["errorCode"], "PROTECTED_OBJECT")
        self.assertFalse(result["failures"][0]["retryable"])
        self.assertTrue(Users.objects.filter(id=self.user.id).exists())
        self.assertFalse(Users.objects.filter(id=self.target.id).exists())

    def test_user_retry_endpoint_rechecks_deleted_state(self):
        """重试接口应逐条重查状态，已成功删除的用户返回稳定失败码。"""
        response = self.client.delete(
            "/api/v1/system/users/",
            {"ids": [self.target.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        retry_response = self.client.post(
            "/api/v1/system/users/batch-delete/retry/",
            {"ids": [self.target.id]},
            format="json",
        )

        self.assertEqual(retry_response.status_code, status.HTTP_200_OK)
        failure = retry_response.json()["data"]["failures"][0]
        self.assertEqual(failure["errorCode"], "ALREADY_DELETED")
        self.assertFalse(failure["retryable"])

    def test_role_batch_delete_reports_protected_item_and_deletes_other_items(self):
        """系统角色失败不应阻塞同批普通角色。"""
        protected = Roles.objects.get(name="超级管理员")
        target = Roles.objects.create(name="批量可删除角色", code="batch-delete-role", status=1)

        response = self.client.delete(
            "/api/v1/system/roles/",
            {"ids": [protected.id, target.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["status"], "partial_failed")
        self.assertEqual(result["successItems"][0]["objectId"], str(target.id))
        self.assertEqual(result["failures"][0]["errorCode"], "PROTECTED_OBJECT")
        self.assertFalse(result["failures"][0]["retryable"])
        self.assertTrue(Roles.objects.filter(id=protected.id).exists())
        self.assertFalse(Roles.objects.filter(id=target.id).exists())

    def test_role_delete_stays_successful_when_cache_invalidation_raises(self):
        """数据库删除已提交时，缓存失效异常不能伪装成删除失败。"""
        target = Roles.objects.create(name="缓存异常角色", code="cache-error-role", status=1)
        assigned_user = Users.objects.create_user(
            username="cache-error-user",
            password="admin123",
            name="缓存异常用户",
            is_active=1,
        )
        assigned_user.roles.add(target)

        with patch(
            "drf_admin.apps.system.views.roles.clear_user_permission_cache",
            side_effect=RuntimeError("cache unavailable"),
        ):
            response = self.client.delete(
                "/api/v1/system/roles/",
                {"ids": [target.id]},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["successCount"], 1)
        self.assertEqual(result["failedCount"], 0)
        self.assertFalse(Roles.objects.filter(id=target.id).exists())

    def test_notice_json_batch_delete_and_retry_published_item(self):
        """通知 JSON body 返回逐条结果，撤回后可通过重试删除。"""
        pending = Notices.objects.create(
            title="批量待删除通知",
            content="内容",
            target_type=1,
            publish_status=0,
        )
        published = Notices.objects.create(
            title="批量已发布通知",
            content="内容",
            target_type=1,
            publish_status=1,
        )

        response = self.client.delete(
            "/api/v1/system/notices/",
            {"ids": [pending.id, published.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["status"], "partial_failed")
        self.assertEqual(result["successItems"][0]["objectId"], str(pending.id))
        self.assertEqual(result["failures"][0]["objectId"], str(published.id))
        self.assertEqual(result["failures"][0]["errorCode"], "PUBLISHED_OBJECT")
        self.assertTrue(result["failures"][0]["retryable"])
        self.assertFalse(Notices.objects.filter(id=pending.id).exists())

        Notices.objects.filter(id=published.id).update(publish_status=-1)
        retry_response = self.client.post(
            "/api/v1/system/notices/batch-delete/retry/",
            {"ids": [published.id]},
            format="json",
        )

        self.assertEqual(retry_response.status_code, status.HTTP_200_OK)
        retry_result = retry_response.json()["data"]
        self.assertEqual(retry_result["status"], "succeeded")
        self.assertFalse(Notices.objects.filter(id=published.id).exists())

    def test_notice_batch_delete_rechecks_scope_before_locked_delete(self):
        """预检后发布人变更到范围外时，最终锁定删除必须拒绝。"""
        visible_dept = Departments.objects.create(name="通知竞态可见部门", status=1, sort=1)
        hidden_dept = Departments.objects.create(name="通知竞态隐藏部门", status=1, sort=2)
        role = Roles.objects.create(
            name="通知竞态范围角色",
            code="notice-race-scope",
            status=1,
            data_scope=Roles.DATA_SCOPE_DEPT,
        )
        permission = Permissions.objects.create(
            name="通知竞态删除权限",
            type="BUTTON",
            perm="system:notices:delete",
        )
        role.permissions.add(permission)
        scoped_user = Users.objects.create_user(
            username="notice-race-scoped-user",
            password="admin123",
            name="通知竞态操作人",
            dept=visible_dept,
            is_active=1,
        )
        scoped_user.roles.add(role)
        hidden_publisher = Users.objects.create_user(
            username="notice-race-hidden-publisher",
            password="admin123",
            name="通知竞态隐藏发布人",
            dept=hidden_dept,
            is_active=1,
        )
        notice = Notices.objects.create(
            title="通知竞态对象",
            content="内容",
            publisher_id=scoped_user.id,
            publisher_name=scoped_user.username,
            publish_status=0,
        )
        self.client.force_authenticate(user=scoped_user)

        original_scope = notices_views.apply_notice_admin_data_scope
        scope_calls = 0

        def scope_with_race(queryset, user):
            nonlocal scope_calls
            scope_calls += 1
            if scope_calls == 3:
                Notices.objects.filter(id=notice.id).update(
                    publisher_id=hidden_publisher.id,
                )
            return original_scope(queryset, user)

        with patch.object(
            notices_views,
            "apply_notice_admin_data_scope",
            side_effect=scope_with_race,
        ):
            response = self.client.delete(
                "/api/v1/system/notices/",
                {"ids": [notice.id]},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failures"][0]["errorCode"], "NOT_FOUND")
        self.assertTrue(Notices.objects.filter(id=notice.id).exists())
        self.assertEqual(scope_calls, 3)

    def test_notice_comma_path_keeps_result_contract(self):
        """通知历史逗号路径保留兼容性并返回新结果结构。"""
        first = Notices.objects.create(title="兼容通知一", content="内容", target_type=1)
        second = Notices.objects.create(title="兼容通知二", content="内容", target_type=1)

        response = self.client.delete(
            f"/api/v1/system/notices/{first.id},{second.id}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()["data"]
        self.assertEqual(result["totalCount"], 2)
        self.assertEqual(result["successCount"], 2)
        self.assertEqual(
            [item["objectId"] for item in result["successItems"]],
            [str(first.id), str(second.id)],
        )

    def test_batch_delete_rejects_invalid_ids_with_bad_request(self):
        """三类接口对空列表、字符串、布尔值和非正整数统一返回 400。"""
        endpoints = (
            "/api/v1/system/users/",
            "/api/v1/system/roles/",
            "/api/v1/system/notices/",
        )
        for endpoint in endpoints:
            for ids in ([], [0], [-1], ["1"], [True]):
                with self.subTest(endpoint=endpoint, ids=ids):
                    response = self.client.delete(endpoint, {"ids": ids}, format="json")
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
