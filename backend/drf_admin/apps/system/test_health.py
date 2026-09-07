# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import Client, TestCase, override_settings

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

    def test_existing_but_broken_database_connection_is_not_ready(self):
        with patch("drf_admin.apps.system.views.health.connection.cursor", side_effect=ConnectionError("lost")):
            self.assertEqual(self.client.get("/health/ready").status_code, 503)
            self.assertEqual(self.client.get("/health/live").status_code, 200)

    @override_settings(ENVIRONMENT="prod", REDIS_HOST="redis", REDIS_PORT=6379)
    def test_production_readiness_requires_redis(self):
        with patch("django_redis.get_redis_connection", side_effect=ConnectionError("unavailable")):
            response = self.client.get("/health/ready")
            live = self.client.get("/health/live")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["redis"], "error")
        self.assertEqual(live.status_code, 200)

    @override_settings(ENVIRONMENT="production", REDIS_HOST="", REDIS_PORT=None)
    def test_production_missing_redis_is_not_ready(self):
        self.assertEqual(self.client.get("/health/ready").status_code, 503)

    @override_settings(ENVIRONMENT="pro", REDIS_HOST="redis", REDIS_PORT=6379)
    def test_production_settings_file_environment_checks_redis(self):
        with patch("django_redis.get_redis_connection", side_effect=ConnectionError("lost")):
            self.assertEqual(self.client.get("/health/ready").status_code, 503)
