# -*- coding: utf-8 -*-
"""
单点登录接口测试：授权流程、ID Token 校验、限速与审计脱敏
"""

import base64
import json
import time
from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from redis.exceptions import ConnectionError as RedisConnectionError
from rest_framework.test import APIClient

from drf_admin.apps.oauth import login_throttle
from drf_admin.apps.oauth import oidc_policy as policy
from drf_admin.apps.oauth.login_throttle_policy import IP_ATTEMPT_LIMIT, rate_limit_keys
from drf_admin.apps.oauth.models import OidcIdentity
from drf_admin.apps.oauth.services import oidc as oidc_service
from drf_admin.apps.oauth.test_oidc_helpers import (
    AUTHORIZE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    ISSUER,
    KEY_1,
    KEY_2,
    LOGIN_URL,
    REDIRECT_URI,
    SUBJECT,
    OidcFlowTestCase,
    hs256_token,
    unsigned_token,
)
from drf_admin.apps.oauth.views.oidc import OidcAuthorizeView, OidcLoginView
from drf_admin.apps.system.models import OperationLog, Users
from drf_admin.settings_helpers import validate_oidc_startup


class OidcViewBoundaryTests(SimpleTestCase):
    def test_views_are_public(self):
        """测试环境默认 AllowAny，只能直接断言视图属性来锁定公开边界。"""
        for view in (OidcAuthorizeView, OidcLoginView):
            self.assertEqual(view.authentication_classes, [])
            self.assertEqual(view.permission_classes, [])


class OidcStartupValidationTests(SimpleTestCase):
    def test_production_fails_fast_on_invalid_config(self):
        for issuer, redirect_uri in (
            ("", "https://admin.example.com/cb"),
            ("http://idp.example.com", "https://admin.example.com/cb"),
            ("https://idp.example.com", "http://admin.example.com/cb"),
        ):
            with self.subTest(issuer=issuer, redirect_uri=redirect_uri):
                with self.assertRaises(ImproperlyConfigured):
                    validate_oidc_startup(True, issuer, CLIENT_ID, redirect_uri, "pro")

    def test_non_production_or_disabled_does_not_raise(self):
        validate_oidc_startup(True, "", "", "", "dev")
        validate_oidc_startup(False, "", "", "", "pro")
        validate_oidc_startup(
            True, "https://idp.example.com", CLIENT_ID, "https://admin.example.com/cb", "pro"
        )


class OidcDisabledTests(OidcFlowTestCase):
    @override_settings(OIDC_ENABLED=False)
    def test_both_endpoints_report_disabled(self):
        self.assert_oidc_error(self.client.post(AUTHORIZE_URL), policy.MESSAGE_DISABLED)
        self.assert_oidc_error(self.client.post(LOGIN_URL, {}, format="json"), policy.MESSAGE_DISABLED)
        self.assertEqual(self.idp.discovery_fetches, 0)

    @override_settings(OIDC_ISSUER="")
    def test_invalid_config_outside_production_fails_requests_and_warns_once(self):
        with self.assertLogs("info", level="WARNING") as captured:
            for _ in range(2):
                self.assert_oidc_error(self.client.post(AUTHORIZE_URL), policy.MESSAGE_PROVIDER_FAILED)
        self.assertEqual(sum("单点登录配置无效" in line for line in captured.output), 1)

    @override_settings(ENVIRONMENT="pro", OIDC_ISSUER="http://idp.example.com")
    def test_production_rejects_plain_http_issuer_at_request_time(self):
        self.assert_oidc_error(self.client.post(AUTHORIZE_URL), policy.MESSAGE_PROVIDER_FAILED)


class OidcAuthorizeTests(OidcFlowTestCase):
    def test_authorize_stores_hashed_state_with_ttl_and_returns_pkce_url(self):
        flow, query = self.authorize()

        self.assertEqual(set(flow), {"authorizationUrl", "state", "flowSecret"})
        self.assertTrue(flow["authorizationUrl"].startswith(self.idp.discovery["authorization_endpoint"] + "?"))
        redis = login_throttle.get_login_redis()
        key = policy.state_key(flow["state"])
        self.assertTrue(0 < redis.ttl(key) <= policy.STATE_TTL_SECONDS)
        raw = redis.get(key)
        self.assertNotIn(flow["flowSecret"], raw)
        record = json.loads(raw)
        self.assertEqual(record["flowSecretHash"], policy.sha256_hex(flow["flowSecret"]))
        self.assertEqual(query["state"], flow["state"])
        self.assertEqual(query["nonce"], record["nonce"])
        self.assertEqual(query["code_challenge_method"], "S256")
        self.assertEqual(query["code_challenge"], policy.pkce_challenge(record["codeVerifier"]))
        self.assertEqual(query["response_type"], "code")
        self.assertEqual(query["client_id"], CLIENT_ID)
        self.assertEqual(query["redirect_uri"], REDIRECT_URI)
        self.assertEqual(query["scope"], "openid profile email")

    def test_discovery_issuer_mismatch_is_rejected(self):
        self.idp.discovery["issuer"] = "https://other.example.com"
        self.assert_oidc_error(self.client.post(AUTHORIZE_URL), policy.MESSAGE_PROVIDER_FAILED)


class OidcLoginFlowTests(OidcFlowTestCase):
    def test_full_login_issues_local_tokens_usable_for_info_and_refresh(self):
        data = self.assert_login_ok(self.sso_login())

        self.assertEqual(set(data), {"accessToken", "refreshToken", "tokenType", "expiresIn"})
        self.assertEqual(data["tokenType"], "bearer")
        self.assertEqual(data["expiresIn"], int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()))
        self.assertIsInstance(data["expiresIn"], int)
        identity = OidcIdentity.objects.select_related("user").get()
        self.assertEqual((identity.issuer, identity.subject), (ISSUER, SUBJECT))
        self.assertEqual(identity.email, "alice@example.com")
        self.assertIsNotNone(identity.last_login_at)

        info_client = APIClient()
        info_client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['accessToken']}")
        info = info_client.get("/api/v1/oauth/info/")
        self.assertEqual(info.status_code, 200, info.content)
        self.assertEqual(info.json()["data"]["username"], identity.user.username)

        refreshed = self.client.post(
            "/api/v1/oauth/refresh-token/", {"refreshToken": data["refreshToken"]}, format="json"
        )
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertIn("accessToken", refreshed.json()["data"])

    def test_token_request_uses_pkce_basic_auth_and_cached_metadata(self):
        flow, query = self.authorize()
        self.idp.id_token = KEY_1.sign(self.claims(query["nonce"]))
        self.assert_login_ok(self.client.post(LOGIN_URL, self.login_body(flow), format="json"))

        request = self.idp.token_requests[-1]
        self.assertEqual(request["url"], self.idp.discovery["token_endpoint"])
        self.assertEqual(request["form"]["grant_type"], "authorization_code")
        self.assertEqual(request["form"]["code"], "authorization-code-123")
        self.assertEqual(request["form"]["redirect_uri"], REDIRECT_URI)
        self.assertEqual(policy.pkce_challenge(request["form"]["code_verifier"]), query["code_challenge"])
        self.assertNotIn("client_secret", request["form"])
        expected = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        self.assertEqual(request["headers"]["Authorization"], f"Basic {expected}")
        self.assertEqual((self.idp.discovery_fetches, self.idp.jwks_fetches), (1, 1))

    @override_settings(OIDC_CLIENT_SECRET="")
    def test_public_client_sends_client_id_without_secret(self):
        self.assert_login_ok(self.sso_login())
        request = self.idp.token_requests[-1]
        self.assertEqual(request["form"]["client_id"], CLIENT_ID)
        self.assertNotIn("Authorization", request["headers"])

    def test_second_login_reuses_identity_without_overwriting_profile(self):
        self.assert_login_ok(self.sso_login())
        user_count = Users.objects.count()
        self.assert_login_ok(self.sso_login(name="Changed", email="changed@example.com"))

        self.assertEqual(Users.objects.count(), user_count)
        identity = OidcIdentity.objects.select_related("user").get()
        self.assertEqual((identity.user.name, identity.user.email), ("Alice", "alice@example.com"))

    def test_state_is_single_use_and_bound_to_flow_secret(self):
        flow, query = self.authorize()
        self.idp.id_token = KEY_1.sign(self.claims(query["nonce"]))
        body = self.login_body(flow)
        self.assert_login_ok(self.client.post(LOGIN_URL, body, format="json"))
        replay = self.client.post(LOGIN_URL, body, format="json")
        self.assert_oidc_error(replay, policy.MESSAGE_FLOW_INVALID)

        unknown = self.client.post(LOGIN_URL, self.login_body(flow, state="unknown-state"), format="json")
        self.assert_oidc_error(unknown, policy.MESSAGE_FLOW_INVALID)

        flow, _query = self.authorize()
        wrong = self.client.post(LOGIN_URL, self.login_body(flow, flowSecret="wrong"), format="json")
        self.assert_oidc_error(wrong, policy.MESSAGE_FLOW_INVALID)
        self.assertFalse(login_throttle.get_login_redis().exists(policy.state_key(flow["state"])))
        retry = self.client.post(LOGIN_URL, self.login_body(flow), format="json")
        self.assert_oidc_error(retry, policy.MESSAGE_FLOW_INVALID)

    def test_malformed_body_is_rejected_before_consuming_state(self):
        flow, _query = self.authorize()
        cases = (
            {"authorizationCode": None},
            {"authorizationCode": ""},
            {"state": None},
            {"flowSecret": None},
            {"authorizationCode": 123},
            {"authorizationCode": "x" * 2049},
            {"iss": 1},
            {"iss": "x" * 2049},
        )
        for overrides in cases:
            with self.subTest(overrides=str(overrides)[:40]):
                response = self.client.post(LOGIN_URL, self.login_body(flow, **overrides), format="json")
                self.assert_oidc_error(response, policy.MESSAGE_FLOW_INVALID)
        for raw in ("[]", "{not json"):
            with self.subTest(raw=raw):
                response = self.client.post(LOGIN_URL, raw, content_type="application/json")
                self.assert_oidc_error(response, policy.MESSAGE_FLOW_INVALID)
        self.assertTrue(login_throttle.get_login_redis().exists(policy.state_key(flow["state"])))

    def test_token_endpoint_failures_are_provider_errors(self):
        for token_response in ({"access_token": "only"}, {"error": "invalid_grant"}):
            with self.subTest(token_response=token_response):
                self.idp.token_response = token_response
                self.assert_oidc_error(self.sso_login(), policy.MESSAGE_PROVIDER_FAILED)
        self.assertFalse(OidcIdentity.objects.exists())


class OidcIdTokenValidationTests(OidcFlowTestCase):
    def test_invalid_id_tokens_are_rejected(self):
        now = int(time.time())
        cases = {
            "nonce": {"nonce": "another-nonce"},
            "iss": {"iss": "https://evil.example.com"},
            "aud": {"aud": "another-client"},
            "multi_aud_without_azp": {"aud": [CLIENT_ID, "another-client"]},
            "azp": {"azp": "another-client"},
            "expired": {"exp": now - 3600, "iat": now - 7200},
        }
        for name, overrides in cases.items():
            with self.subTest(name):
                self.assert_oidc_error(self.sso_login(**overrides), policy.MESSAGE_PROVIDER_FAILED)
        for name, signer in (("alg_none", unsigned_token), ("hs256_client_secret", hs256_token)):
            with self.subTest(name):
                self.assert_oidc_error(self.sso_login(signer=signer), policy.MESSAGE_PROVIDER_FAILED)
        self.assertFalse(OidcIdentity.objects.exists())

    def test_multi_audience_with_matching_azp_is_accepted(self):
        self.assert_login_ok(self.sso_login(aud=[CLIENT_ID, "another-client"], azp=CLIENT_ID))

    def test_callback_iss_parameter_rules(self):
        mismatch = self.sso_login(body={"iss": "https://evil.example.com"})
        self.assert_oidc_error(mismatch, policy.MESSAGE_PROVIDER_FAILED)

        oidc_service.reset_metadata_cache()
        self.idp.discovery["authorization_response_iss_parameter_supported"] = True
        missing = self.sso_login(body={"iss": None})
        self.assert_oidc_error(missing, policy.MESSAGE_PROVIDER_FAILED)
        self.assert_login_ok(self.sso_login())

    def test_unknown_kid_refetches_jwks_once(self):
        self.assert_login_ok(self.sso_login())
        self.assertEqual(self.idp.jwks_fetches, 1)

        self.assert_oidc_error(self.sso_login(signer=KEY_2.sign), policy.MESSAGE_PROVIDER_FAILED)
        self.assertEqual(self.idp.jwks_fetches, 2)

        self.idp.jwks = {"keys": [KEY_1.jwk(), KEY_2.jwk()]}
        self.assert_login_ok(self.sso_login(signer=KEY_2.sign))
        self.assertEqual(self.idp.jwks_fetches, 3)
        self.assert_login_ok(self.sso_login(signer=KEY_2.sign))
        self.assertEqual(self.idp.jwks_fetches, 3)


class OidcProtectionTests(OidcFlowTestCase):
    def test_redis_outage_returns_503(self):
        with patch.object(login_throttle, "get_login_redis", side_effect=RedisConnectionError("down")):
            for url in (AUTHORIZE_URL, LOGIN_URL):
                with self.subTest(url):
                    response = self.client.post(url, {}, format="json")
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json()["code"], 503)

    def test_state_store_outage_after_throttle_returns_503(self):
        redis = login_throttle.get_login_redis()
        broken = Mock(eval=redis.eval, set=Mock(side_effect=RedisConnectionError("down")),
                      pipeline=Mock(side_effect=RedisConnectionError("down")))
        with patch.object(login_throttle, "get_login_redis", return_value=broken):
            self.assertEqual(self.client.post(AUTHORIZE_URL).status_code, 503)
            body = {"authorizationCode": "code", "state": "state", "flowSecret": "secret"}
            self.assertEqual(self.client.post(LOGIN_URL, body, format="json").status_code, 503)

    def test_ip_limit_returns_429_and_leaves_account_keys_untouched(self):
        redis = login_throttle.get_login_redis()
        self.assert_login_ok(self.sso_login())
        self.assertFalse(redis.exists(*login_throttle.OIDC_ACCOUNT_KEYS))

        now_ms = int(time.time() * 1000)
        ip_key = rate_limit_keys("", "127.0.0.1")[2]
        redis.zadd(ip_key, {f"attempt-{index}": now_ms for index in range(IP_ATTEMPT_LIMIT)})
        for url in (AUTHORIZE_URL, LOGIN_URL):
            with self.subTest(url):
                response = self.client.post(url, {}, format="json")
                self.assertEqual(response.status_code, 429)
                self.assertEqual(response.json()["code"], 429)
                self.assertIn("Retry-After", response)


class OidcAuditMaskingTests(OidcFlowTestCase):
    def test_operation_log_never_contains_code_flow_secret_or_tokens(self):
        code = "authorization-code-must-not-leak"
        with self.assertLogs("operation", level="INFO") as captured:
            flow, query = self.authorize()
            self.idp.id_token = KEY_1.sign(self.claims(query["nonce"]))
            response = self.client.post(
                LOGIN_URL, self.login_body(flow, authorizationCode=code), format="json"
            )
        tokens = self.assert_login_ok(response)

        secrets = (code, flow["flowSecret"], tokens["accessToken"], tokens["refreshToken"])
        logs = OperationLog.objects.filter(path__in=(AUTHORIZE_URL, LOGIN_URL))
        self.assertEqual(logs.count(), 2)
        persisted = " ".join(
            f"{log.request_body} {log.response_body} {json.dumps(log.request_context, ensure_ascii=False)}"
            for log in logs
        )
        printed = "\n".join(captured.output)
        for secret in secrets:
            self.assertNotIn(secret, persisted)
            self.assertNotIn(secret, printed)


class OidcHttpHelperTests(SimpleTestCase):
    """真实 HTTP 辅助函数：不跟随重定向、带超时和 Accept 头，异常不外泄。"""

    def response(self, status_code=200, payload=None):
        json_method = Mock(side_effect=ValueError("no json")) if payload is None else Mock(return_value=payload)
        return Mock(status_code=status_code, json=json_method)

    def test_get_and_post_use_safe_request_options(self):
        with patch.object(requests, "get", return_value=self.response(payload={"ok": 1})) as get:
            self.assertEqual(oidc_service._get_json("https://idp.example.com/x"), {"ok": 1})
        get.assert_called_once_with(
            "https://idp.example.com/x",
            headers={"Accept": "application/json"},
            timeout=policy.HTTP_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
        headers = {"Accept": "application/json"}
        with patch.object(requests, "post", return_value=self.response(payload={"ok": 2})) as post:
            self.assertEqual(oidc_service._post_form("https://idp.example.com/t", {"a": "b"}, headers), {"ok": 2})
        post.assert_called_once_with(
            "https://idp.example.com/t",
            data={"a": "b"},
            headers=headers,
            timeout=policy.HTTP_TIMEOUT_SECONDS,
            allow_redirects=False,
        )

    def test_redirect_non_json_and_network_errors_become_provider_errors(self):
        outcomes = (
            {"return_value": self.response(302, {"redirect": True})},
            {"return_value": self.response(500, {"error": "boom"})},
            {"return_value": self.response(200, None)},
            {"side_effect": requests.ConnectionError("secret detail")},
        )
        for outcome in outcomes:
            with self.subTest(outcome=str(outcome)[:30]):
                with patch.object(requests, "get", **outcome), self.assertRaises(policy.OidcError) as caught:
                    oidc_service._get_json("https://idp.example.com/x")
                self.assertEqual(caught.exception.message, policy.MESSAGE_PROVIDER_FAILED)
                with patch.object(requests, "post", **outcome), self.assertRaises(policy.OidcError):
                    oidc_service._post_form("https://idp.example.com/t", {}, {})


class OidcJwksCacheTests(OidcFlowTestCase):
    def test_malformed_jwks_is_not_cached(self):
        self.idp.jwks = {"keys": "not-a-list"}
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_PROVIDER_FAILED)
        self.idp.jwks = {"keys": [KEY_1.jwk()]}
        self.assert_login_ok(self.sso_login())
        self.assertEqual(self.idp.jwks_fetches, 2)
