# -*- coding: utf-8 -*-
"""审计日志对象关联与结构化请求上下文契约测试。"""

import hashlib
import json
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from drf_admin.apps.system.models import OperationLog
from drf_admin.apps.system.test_helpers import create_admin_user, grant_log_permissions
from drf_admin.utils.audit import (
    MAX_REQUEST_CONTEXT_BYTES,
    build_request_context,
    limit_request_context,
    serialize_query_params,
    set_audit_context,
    set_audit_object,
)


class OperationLogObjectContextTestCase(TestCase):
    """对象字段、筛选和显式关联行为。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        grant_log_permissions(self.user, plain=True)
        self.client.force_authenticate(user=self.user)

    def test_log_output_contains_object_fields_and_request_context(self):
        """日志详情对外输出 objectType/objectId/requestContext。"""
        log = OperationLog.objects.create(
            username="admin",
            operation="更新用户",
            method="PUT",
            path="/api/v1/system/users/7/",
            object_type="system.users",
            object_id="7",
            request_context={
                "pathParams": {"userId": "7"},
                "changedFields": ["name"],
                "truncated": False,
            },
        )

        response = self.client.get(f"/api/v1/system/logs/{log.id}")

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["objectType"], "system.users")
        self.assertEqual(data["objectId"], "7")
        self.assertEqual(data["requestContext"]["pathParams"]["userId"], "7")

    def test_page_filters_by_object_type_and_id(self):
        """日志分页支持对象类型和对象 ID 精确筛选。"""
        OperationLog.objects.create(
            username="admin",
            operation="目标日志",
            method="PUT",
            path="/api/v1/system/users/7/",
            object_type="system.users",
            object_id="7",
        )
        OperationLog.objects.create(
            username="admin",
            operation="其他对象",
            method="PUT",
            path="/api/v1/system/roles/7/",
            object_type="system.roles",
            object_id="7",
        )

        response = self.client.get(
            "/api/v1/system/logs/page",
            {"objectType": "system.users", "objectId": "7"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["list"][0]["operation"], "目标日志")

    def test_create_write_request_associates_created_object(self):
        """通用 Django CRUD 写入后，审计日志关联新建对象。"""
        response = self.client.post(
            "/api/v1/system/dicts/",
            {"name": "对象关联字典", "dictCode": "audit_object_dict", "status": 1},
            format="json",
            HTTP_X_REQUEST_ID="django-object-context",
        )

        self.assertIn(response.status_code, (200, 201))
        log = OperationLog.objects.filter(
            request_id="django-object-context",
            method="POST",
        ).latest("created_at")
        self.assertEqual(log.object_type, "system.dicts")
        self.assertTrue(log.object_id)
        self.assertEqual(log.request_context.get("objectId"), log.object_id)


class OperationLogRequestContextTestCase(TestCase):
    """结构化请求上下文的脱敏、大小和文件元数据约束。"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_query_params_serializer_masks_sensitive_values_and_keeps_duplicates(self):
        query_params = QueryDict(
            "token=django-secret&search=one&search=two&empty="
        )

        serialized = json.loads(serialize_query_params(query_params))

        self.assertEqual(serialized["token"], "******")
        self.assertEqual(serialized["search"], ["one", "two"])
        self.assertEqual(serialized["empty"], "")
        self.assertNotIn("django-secret", json.dumps(serialized))

    def test_context_recursively_masks_body_and_excludes_sensitive_headers(self):
        request = self.factory.post(
            "/api/v1/system/users/7/?tag=one&tag=two",
            data=json.dumps(
                {
                    "profile": {
                        "name": "Alice",
                        "password": "must-not-leak",
                        "tokens": [{"accessToken": "also-secret"}],
                    }
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer must-not-leak",
            HTTP_COOKIE="session=must-not-leak",
            HTTP_X_REQUEST_ID="request-context-1",
            HTTP_ACCEPT="application/json",
        )
        request.resolver_match = SimpleNamespace(kwargs={"user_id": "7"})

        context = build_request_context(request)

        self.assertEqual(context["pathParams"], {"userId": "7"})
        self.assertEqual(context["query"]["tag"], ["one", "two"])
        self.assertEqual(context["body"]["profile"]["name"], "Alice")
        self.assertNotEqual(context["body"]["profile"]["password"], "must-not-leak")
        self.assertEqual(context["body"]["profile"]["tokens"], "******")
        self.assertNotIn("authorization", context["selectedHeaders"])
        self.assertNotIn("cookie", context["selectedHeaders"])
        self.assertEqual(context["selectedHeaders"]["accept"], "application/json")
        self.assertEqual(len(context["bodyHash"]), 64)

    def test_context_masks_sensitive_values_inside_selected_headers(self):
        """白名单 Header 的值也不能把 Referer/XFF 中的凭据原样落库。"""
        request = self.factory.post(
            "/api/v1/system/users/7/",
            data=b"{}",
            content_type="application/json",
            HTTP_REFERER=(
                "https://host.example/path?token=referer-secret&next=/home"
                "&code=oauth-secret#state=state-secret"
            ),
            HTTP_X_FORWARDED_FOR="10.0.0.1, token=forwarded-secret",
        )

        context = build_request_context(request)

        self.assertEqual(
            context["selectedHeaders"]["referer"],
            "https://host.example/path?token=******&next=******&code=******#state=******",
        )
        self.assertEqual(
            context["selectedHeaders"]["x-forwarded-for"],
            "10.0.0.1, ******",
        )
        self.assertNotIn("referer-secret", json.dumps(context))
        self.assertNotIn("oauth-secret", json.dumps(context))
        self.assertNotIn("state-secret", json.dumps(context))
        self.assertNotIn("forwarded-secret", json.dumps(context))

    def test_context_limits_serialized_size_and_marks_truncated(self):
        request = self.factory.post(
            "/api/v1/system/users/7/",
            data=json.dumps({"notes": "x" * (MAX_REQUEST_CONTEXT_BYTES * 2)}),
            content_type="application/json",
        )

        context = build_request_context(request)

        encoded = json.dumps(context, ensure_ascii=False, separators=(",", ":")).encode()
        self.assertLessEqual(len(encoded), MAX_REQUEST_CONTEXT_BYTES)
        self.assertTrue(context["truncated"])

    def test_canonical_request_fields_cannot_be_overridden_by_extra_context(self):
        """请求采集字段和显式对象字段必须优先于业务附加上下文。"""
        body = json.dumps({"name": "actual"}).encode()
        request = self.factory.post(
            "/api/v1/system/users/7/?tag=actual",
            data=body,
            content_type="application/json",
        )
        request.resolver_match = SimpleNamespace(kwargs={"user_id": "7"})
        set_audit_object(request, "system.users", 7, changed_fields=["name"])
        set_audit_context(
            request,
            object_type="spoofed.type",
            object_id="999",
            path_params={"userId": "999"},
            query={"tag": "spoofed"},
            body={"name": "spoofed"},
            body_hash="spoofed-hash",
            changed_fields=["spoofedField"],
            custom_marker="kept",
        )

        context = build_request_context(request)

        self.assertEqual(context["objectType"], "system.users")
        self.assertEqual(context["objectId"], "7")
        self.assertEqual(context["pathParams"], {"userId": "7"})
        self.assertEqual(context["query"], {"tag": "actual"})
        self.assertEqual(context["body"], {"name": "actual"})
        self.assertEqual(context["changedFields"], ["name"])
        self.assertEqual(context["bodyHash"], hashlib.sha256(body).hexdigest())
        self.assertEqual(context["customMarker"], "kept")

    def test_extreme_context_truncation_preserves_audit_identity_and_batch_summary(self):
        """顶层附加字段很多时仍保留对象身份和批量结果摘要。"""
        context = {f"extra{i}": "x" * 1000 for i in range(1000)}
        context.update(
            {
                "objectType": "system.users",
                "objectId": "7",
                "bodyHash": "a" * 64,
                "batchCount": 10,
                "processedCount": 10,
                "successCount": 7,
                "failedCount": 3,
                "failureCodes": ["DELETE_FAILED", "PROTECTED_OBJECT"],
            }
        )

        limited = limit_request_context(context)

        self.assertLessEqual(
            len(json.dumps(limited, ensure_ascii=False, separators=(",", ":")).encode()),
            MAX_REQUEST_CONTEXT_BYTES,
        )
        self.assertTrue(limited["truncated"])
        self.assertEqual(limited["objectType"], "system.users")
        self.assertEqual(limited["objectId"], "7")
        self.assertEqual(limited["bodyHash"], "a" * 64)
        self.assertEqual(limited["batchCount"], 10)
        self.assertEqual(limited["processedCount"], 10)
        self.assertEqual(limited["successCount"], 7)
        self.assertEqual(limited["failedCount"], 3)
        self.assertEqual(limited["failureCodes"], ["DELETE_FAILED", "PROTECTED_OBJECT"])

    def test_file_metadata_contains_hash_without_file_content(self):
        upload = SimpleUploadedFile(
            "credentials.txt",
            b"private-file-content",
            content_type="text/plain",
        )
        request = self.factory.post(
            "/api/v1/system/users/import",
            data={"file": upload},
        )

        context = build_request_context(request)

        self.assertEqual(len(context["fileMeta"]), 1)
        metadata = context["fileMeta"][0]
        self.assertEqual(metadata["fieldName"], "file")
        self.assertEqual(metadata["fileName"], "credentials.txt")
        self.assertEqual(metadata["size"], len(b"private-file-content"))
        self.assertEqual(len(metadata["sha256"]), 64)
        self.assertNotIn("private-file-content", json.dumps(context))

    def test_set_audit_object_keeps_explicit_context_on_request(self):
        request = self.factory.post("/api/v1/system/users/7/", data={})

        set_audit_object(
            request,
            "system.users",
            7,
            changed_fields=["name", "mobile"],
        )

        self.assertEqual(request.audit_object, {"type": "system.users", "id": "7"})
        self.assertEqual(request.audit_context["changedFields"], ["name", "mobile"])
