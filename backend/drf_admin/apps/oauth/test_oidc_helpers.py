# -*- coding: utf-8 -*-
"""
单点登录测试辅助：进程内假身份提供方与登录流程封装
"""

import base64
import copy
import json
import time
from collections import Counter
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import TestCase, override_settings
from jwt.algorithms import RSAAlgorithm
from rest_framework.test import APIClient

from drf_admin.apps.oauth.oidc_policy import OidcError, discovery_url
from drf_admin.apps.oauth.services import oidc as oidc_service

AUTHORIZE_URL = "/api/v1/oauth/oidc/authorize/"
LOGIN_URL = "/api/v1/oauth/oidc/login/"
ISSUER = "https://idp.example.com/realms/dv"
CLIENT_ID = "dv-admin"
# 足够长，避免 HS256 伪造用例触发 PyJWT 短密钥告警
CLIENT_SECRET = "client-secret-for-tests-only-0123456789abcdef"
REDIRECT_URI = "https://admin.example.com/oidc/callback"
SUBJECT = "subject-1"

OIDC_SETTINGS = {
    "OIDC_ENABLED": True,
    "OIDC_ISSUER": ISSUER,
    "OIDC_CLIENT_ID": CLIENT_ID,
    "OIDC_CLIENT_SECRET": CLIENT_SECRET,
    "OIDC_REDIRECT_URI": REDIRECT_URI,
    "OIDC_SCOPES": "openid profile email",
    "OIDC_AUTO_PROVISION": True,
    "OIDC_MATCH_EXISTING_BY_EMAIL": False,
    "OIDC_ALLOWED_EMAIL_DOMAINS": "",
}


class SigningKey:
    """RS256 签名密钥及其公开 JWK。"""

    def __init__(self, kid):
        self.kid = kid
        self._private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._pem = self._private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )

    def jwk(self):
        value = RSAAlgorithm.to_jwk(self._private.public_key(), as_dict=True)
        value.update(kid=self.kid, use="sig", alg="RS256")
        return value

    def sign(self, claims):
        return jwt.encode(claims, self._pem, algorithm="RS256", headers={"kid": self.kid})


# 生成 RSA 密钥较慢，整个测试进程共用
KEY_1 = SigningKey("key-1")
KEY_2 = SigningKey("key-2")


def unsigned_token(claims):
    def segment(value):
        raw = json.dumps(value).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    return f"{segment({'alg': 'none', 'typ': 'JWT'})}.{segment(claims)}."


def hs256_token(claims):
    return jwt.encode(claims, CLIENT_SECRET, algorithm="HS256", headers={"kid": KEY_1.kid})


class FakeIdp:
    """替换服务层 HTTP 函数，记录每个端点被请求的次数。"""

    def __init__(self):
        self.discovery = {
            "issuer": ISSUER,
            "authorization_endpoint": f"{ISSUER}/protocol/openid-connect/auth",
            "token_endpoint": f"{ISSUER}/protocol/openid-connect/token",
            "jwks_uri": f"{ISSUER}/protocol/openid-connect/certs",
            "response_types_supported": ["code"],
            "code_challenge_methods_supported": ["S256"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        }
        self.jwks = {"keys": [KEY_1.jwk()]}
        self.fetches = Counter()
        self.token_requests = []
        self.token_response = None
        self.id_token = None

    @property
    def jwks_fetches(self):
        return self.fetches[self.discovery["jwks_uri"]]

    @property
    def discovery_fetches(self):
        return self.fetches[discovery_url(ISSUER)]

    def get_json(self, url):
        self.fetches[url] += 1
        if url == discovery_url(ISSUER):
            return copy.deepcopy(self.discovery)
        if url == self.discovery["jwks_uri"]:
            return copy.deepcopy(self.jwks)
        raise OidcError()

    def post_form(self, url, form, headers):
        self.token_requests.append({"url": url, "form": dict(form), "headers": dict(headers)})
        if self.token_response is not None:
            return self.token_response
        return {"access_token": "idp-access-token", "token_type": "Bearer", "id_token": self.id_token}


@override_settings(**OIDC_SETTINGS)
class OidcFlowTestCase(TestCase):
    """启用单点登录并接入假身份提供方的测试基类。"""

    def setUp(self):
        oidc_service.reset_metadata_cache()
        self.addCleanup(oidc_service.reset_metadata_cache)
        self.idp = FakeIdp()
        for name, fake in (("_get_json", self.idp.get_json), ("_post_form", self.idp.post_form)):
            patcher = patch.object(oidc_service, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.client = APIClient()

    def authorize(self):
        """发起授权，返回 (响应 data, 授权地址查询参数)。"""
        response = self.client.post(AUTHORIZE_URL, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        query = {key: values[0] for key, values in parse_qs(urlsplit(data["authorizationUrl"]).query).items()}
        return data, query

    def claims(self, nonce, **overrides):
        now = int(time.time())
        claims = {
            "iss": ISSUER,
            "sub": SUBJECT,
            "aud": CLIENT_ID,
            "exp": now + 300,
            "iat": now,
            "nonce": nonce,
            "email": "alice@example.com",
            "email_verified": True,
            "preferred_username": "alice",
            "name": "Alice",
        }
        claims.update(overrides)
        return {key: value for key, value in claims.items() if value is not None}

    def login_body(self, flow, **overrides):
        body = {
            "authorizationCode": "authorization-code-123",
            "state": flow["state"],
            "flowSecret": flow["flowSecret"],
            "iss": ISSUER,
        }
        body.update(overrides)
        return {key: value for key, value in body.items() if value is not None}

    def sso_login(self, signer=KEY_1.sign, body=None, **claims):
        """完整走一次 授权 → 身份提供方签发 → 回调登录。"""
        flow, query = self.authorize()
        self.idp.id_token = signer(self.claims(**{"nonce": query["nonce"], **claims}))
        return self.client.post(LOGIN_URL, self.login_body(flow, **(body or {})), format="json")

    def assert_oidc_error(self, response, message):
        self.assertEqual(response.status_code, 400, response.content)
        payload = response.json()
        self.assertEqual(payload["code"], 40000)
        self.assertEqual(payload["errors"], message)

    def assert_login_ok(self, response):
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["code"], 20000)
        return response.json()["data"]
