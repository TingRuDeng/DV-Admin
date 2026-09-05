# -*- coding: utf-8 -*-
"""Django 自定义写入口的审计对象关联契约测试。"""

from __future__ import annotations

import base64
import tempfile
import uuid

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Notices, OperationLog, Permissions, Roles, Users
from drf_admin.apps.system.test_helpers import create_admin_user


def grant_permission(user: Users, code: str) -> None:
    """为测试用户补充一个按钮权限。"""
    role = user.roles.first()
    permission, _ = Permissions.objects.get_or_create(
        perm=code,
        defaults={"name": code, "type": "BUTTON"},
    )
    role.permissions.add(permission)
    cache.delete(f"user_info_{user.id}_perms")


class CustomAuditEntryTestCase(TestCase):
    """验证 Django 非标准 CRUD 写入口的对象关联。"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def request_id(self) -> str:
        return f"django-custom-{uuid.uuid4().hex}"

    def get_log(self, request_id: str) -> OperationLog:
        return OperationLog.objects.get(request_id=request_id)

    def assert_object_log(self, request_id: str, object_type: str, object_id: object = "") -> OperationLog:
        log = self.get_log(request_id)
        self.assertEqual(log.object_type, object_type)
        self.assertEqual(log.object_id, str(object_id))
        self.assertEqual(log.request_context.get("objectType"), object_type)
        self.assertEqual(log.request_context.get("objectId"), str(object_id))
        return log

    def test_reset_password_links_target_user(self):
        target = Users.objects.create_user(
            username="audit-reset-target",
            password="oldpass123",
            name="重置目标",
            is_active=1,
        )
        request_id = self.request_id()

        response = self.client.put(
            f"/api/v1/system/users/{target.id}/password/reset/",
            {"password": "Newpass1", "confirmPassword": "Newpass1"},
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.users", target.id)
        self.assertEqual(log.request_context["changedFields"], ["password"])

    def test_user_export_links_users_collection(self):
        grant_permission(self.user, "system:users:export")
        request_id = self.request_id()

        response = self.client.post(
            "/api/v1/system/users/export/",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.users")
        self.assertEqual(log.request_context["changedFields"], ["export"])

    def test_invalid_user_import_still_links_users_collection(self):
        grant_permission(self.user, "system:users:import")
        request_id = self.request_id()

        response = self.client.post(
            "/api/v1/system/users/import",
            {},
            format="multipart",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 400)
        log = self.assert_object_log(request_id, "system.users")
        self.assertEqual(log.status, 0)
        self.assertEqual(log.request_context["changedFields"], ["file", "deptId"])

    def test_role_menu_assignment_links_role(self):
        role = Roles.objects.create(name="审计授权角色", code="audit-role", status=1)
        menu = Permissions.objects.create(name="审计菜单", type="MENU", perm="audit:menu")
        request_id = self.request_id()

        response = self.client.put(
            f"/api/v1/system/roles/{role.id}/menus/",
            {"menuIds": [menu.id]},
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.roles", role.id)
        self.assertEqual(log.request_context["changedFields"], ["menuIds"])

    def test_notice_update_by_id_links_notice(self):
        notice = Notices.objects.create(title="审计通知", content="旧内容", target_type=1)
        request_id = self.request_id()

        response = self.client.put(
            f"/api/v1/system/notices/{notice.id}",
            {
                "title": "新标题",
                "content": "新内容",
                "type": 0,
                "level": "L",
                "targetType": 1,
                "targetUserIds": [],
            },
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_object_log(request_id, "system.notices", notice.id)

    def test_notice_batch_delete_records_path_ids(self):
        first = Notices.objects.create(title="批量一", content="内容", target_type=1)
        second = Notices.objects.create(title="批量二", content="内容", target_type=1)
        request_id = self.request_id()

        response = self.client.delete(
            f"/api/v1/system/notices/{first.id},{second.id}",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.notices")
        self.assertEqual(log.request_context["batchCount"], 2)
        self.assertEqual(log.request_context["batchIds"], [str(first.id), str(second.id)])

    def test_role_batch_retry_records_ids(self):
        """逐条重试也应保留高优先级批次 ID 摘要。"""
        protected = Roles.objects.get(name="超级管理员")
        request_id = self.request_id()

        response = self.client.post(
            "/api/v1/system/roles/batch-delete/retry/",
            {"ids": [protected.id]},
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.roles")
        self.assertEqual(log.request_context["batchCount"], 1)
        self.assertEqual(log.request_context["batchIds"], [str(protected.id)])

    def test_notice_publish_links_notice(self):
        grant_permission(self.user, "system:notices:publish")
        notice = Notices.objects.create(title="待发布", content="内容", target_type=1)
        request_id = self.request_id()

        response = self.client.put(
            f"/api/v1/system/notices/{notice.id}/publish",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_object_log(request_id, "system.notices", notice.id)

    def test_profile_update_links_current_user(self):
        request_id = self.request_id()

        response = self.client.put(
            "/api/v1/information/profile/",
            {"name": "审计资料更新"},
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.users", self.user.id)
        self.assertEqual(log.request_context["changedFields"], ["name"])

    def test_password_change_links_current_user(self):
        request_id = self.request_id()

        response = self.client.put(
            "/api/v1/information/password",
            {
                "oldPassword": "admin123",
                "newPassword": "Newpass1",
                "confirmPassword": "Newpass1",
            },
            format="json",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.users", self.user.id)
        self.assertEqual(log.request_context["changedFields"], ["oldPassword", "newPassword", "confirmPassword"])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_avatar_upload_links_current_user(self):
        request_id = self.request_id()
        image = SimpleUploadedFile(
            "audit-avatar.gif",
            base64.b64decode("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="),
            content_type="image/gif",
        )

        response = self.client.post(
            "/api/v1/information/change-avatar/",
            {"file": image},
            format="multipart",
            HTTP_X_REQUEST_ID=request_id,
        )

        self.assertEqual(response.status_code, 200)
        log = self.assert_object_log(request_id, "system.users", self.user.id)
        self.assertIn("file", log.request_context["changedFields"])
