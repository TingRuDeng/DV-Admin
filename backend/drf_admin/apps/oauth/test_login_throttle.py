"""Django login cooldown contract, using its real Redis cache connection."""

from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from redis import Redis
from redis.exceptions import ConnectionError
from scripts.redis_test_server import RedisTestServer

from drf_admin.apps.oauth import login_throttle
from drf_admin.apps.oauth.login_throttle_policy import rate_limit_keys
from drf_admin.apps.system.models import Users
from drf_admin.settings_helpers import build_caches


class LoginThrottleTests(TestCase):
    def test_success_clears_only_account_failures(self):
        user = Users.objects.create_user(username="limit-account", password="old-password")
        client = Client()
        for _ in range(4):
            response = client.post("/api/v1/oauth/login/", {
                "username": user.username, "password": "wrong",
            }, content_type="application/json")
            self.assertEqual(response.status_code, 400)
        response = client.post("/api/v1/oauth/login/", {
            "username": user.username, "password": "old-password",
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        failures, cooldown, ip_key = rate_limit_keys(user.username, "127.0.0.1")
        redis = login_throttle.get_login_redis()
        self.assertFalse(redis.exists(failures, cooldown))
        self.assertEqual(redis.zcard(ip_key), 5)

    def test_five_failures_cool_account_with_retry_after(self):
        with RedisTestServer() as server, override_settings(
            REDIS_HOST="127.0.0.1", REDIS_PORT=server.port,
            CACHES=build_caches("127.0.0.1", server.port, ""),
        ), Redis.from_url(server.url, decode_responses=True) as redis, patch(
            "drf_admin.apps.oauth.login_throttle.get_login_redis", return_value=redis,
        ):
            client = Client()
            responses = [client.post("/api/v1/oauth/login/", {
                "username": "missing-user", "password": "invalid",
            }, content_type="application/json") for _ in range(6)]
        self.assertEqual(responses[4].status_code, 429)
        self.assertEqual(responses[5].status_code, 429)
        self.assertLessEqual(int(responses[5]["Retry-After"]), 300)
        self.assertEqual(responses[5].json()["code"], 429)

    def test_login_store_outage_returns_503(self):
        with patch("drf_admin.apps.oauth.login_throttle.get_login_redis", side_effect=ConnectionError("unavailable")):
            response = Client().post("/api/v1/oauth/login/", {
                "username": "account", "password": "old",
            }, content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["code"], 503)

    @override_settings(REDIS_HOST="redis", REDIS_PORT=6379)
    def test_blacklist_dependency_outage_does_not_mask_503(self):
        with patch("drf_admin.utils.middleware.get_redis_connection", side_effect=ConnectionError("unavailable")):
            response = Client().post("/api/v1/oauth/login/", {
                "username": "account", "password": "old",
            }, content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["code"], 503)
