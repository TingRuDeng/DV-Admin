# -*- coding: utf-8 -*-

from django.test import Client, TestCase

from drf_admin.utils.request_id import REQUEST_ID_HEADER


class HealthEndpointTests(TestCase):
    """验证 Django 健康检查端点可被发布门禁直接调用。"""

    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_request_id(self):
        response = self.client.get("/health", HTTP_X_REQUEST_ID="health-trace")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response[REQUEST_ID_HEADER], "health-trace")
        self.assertEqual(response.json()["status"], "ok")

    def test_liveness_endpoint_does_not_require_database(self):
        response = self.client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "alive")

    def test_readiness_endpoint_checks_database(self):
        response = self.client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["database"], "ok")
