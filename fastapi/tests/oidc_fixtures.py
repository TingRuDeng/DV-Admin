"""单点登录测试共享的假身份提供方和夹具。

假身份提供方像真实 IdP 一样记住授权地址里的 nonce 和 PKCE challenge，
兑换授权码时校验 code_verifier，再用 RSA 私钥签发 ID Token。
"""

import copy
import secrets
import time
from collections import Counter
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app.core.config import settings
from app.core.oidc_policy import OidcError, discovery_url, pkce_challenge
from app.services import oidc_provider, oidc_state

ISSUER = "https://idp.example.test/realms/dv"
CLIENT_ID = "dv-admin"
CLIENT_SECRET = "oidc-client-secret-for-tests-0123456789abcdef"
REDIRECT_URI = "https://admin.example.test/oidc/callback"
AUTHORIZE_PATH = "/api/v1/oauth/oidc/authorize/"
LOGIN_PATH = "/api/v1/oauth/oidc/login/"
REMOVE = object()

PRIMARY_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ROTATED_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def private_pem(key: rsa.RSAPrivateKey) -> bytes:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def public_jwk(key: rsa.RSAPrivateKey, kid: str) -> dict:
    jwk = RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return jwk


class FakeIdp:
    """可按用例改写 discovery、JWKS、claims 和 ID Token 的内存身份提供方。"""

    def __init__(self) -> None:
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
        self.jwks = {"keys": [public_jwk(PRIMARY_KEY, "primary")]}
        self.signing_key = PRIMARY_KEY
        self.kid = "primary"
        self.claims = {
            "sub": "idp-user-1",
            "email": "alice@example.com",
            "email_verified": True,
            "name": "Alice",
            "preferred_username": "alice",
        }
        self.id_token_factory = None
        self.fetches: Counter = Counter()
        self.token_requests: list[dict] = []
        self.grants: dict[str, dict] = {}

    @property
    def jwks_fetches(self) -> int:
        return self.fetches[self.discovery["jwks_uri"]]

    @property
    def discovery_fetches(self) -> int:
        return self.fetches[discovery_url(ISSUER)]

    def grant(self, authorization_url: str) -> str:
        """模拟浏览器完成 IdP 登录：记住授权请求并返回回调里的授权码。"""
        query = parse_qs(urlsplit(authorization_url).query)
        code = f"code-{secrets.token_urlsafe(12)}"
        self.grants[code] = {
            "nonce": query["nonce"][0],
            "code_challenge": query["code_challenge"][0],
        }
        return code

    def id_token_claims(self, nonce: str, **overrides) -> dict:
        now = int(time.time())
        claims = {"iss": ISSUER, "aud": CLIENT_ID, "iat": now, "exp": now + 300, "nonce": nonce}
        claims.update(self.claims)
        claims.update(overrides)
        return {key: value for key, value in claims.items() if value is not REMOVE}

    def sign(self, claims: dict, key=None, kid=None, algorithm: str = "RS256") -> str:
        signing_key = private_pem(self.signing_key) if key is None else key
        return jwt.encode(claims, signing_key, algorithm=algorithm, headers={"kid": kid or self.kid})

    async def get_json(self, url: str):
        self.fetches[url] += 1
        if url == discovery_url(ISSUER):
            return copy.deepcopy(self.discovery)
        if url == self.discovery["jwks_uri"]:
            return copy.deepcopy(self.jwks)
        raise OidcError()

    async def post_form(self, url: str, form: dict, headers: dict):
        self.token_requests.append({"url": url, "form": dict(form), "headers": dict(headers)})
        grant = self.grants.pop(form.get("code", ""), None)
        if grant is None or pkce_challenge(form["code_verifier"]) != grant["code_challenge"]:
            # 真实 IdP 返回 400 invalid_grant，_post_form 会把它转换为 OidcError。
            raise OidcError()
        if self.id_token_factory is not None:
            return {"id_token": self.id_token_factory(self, grant["nonce"])}
        return {
            "access_token": "idp-access-token",
            "token_type": "Bearer",
            "id_token": self.sign(self.id_token_claims(grant["nonce"])),
        }


@pytest.fixture
def oidc_redis(isolated_login_counters, monkeypatch):
    """state 存储与登录限速共用每个用例清空的真实 Redis。"""
    monkeypatch.setattr(oidc_state, "get_oidc_redis", lambda: isolated_login_counters)
    return isolated_login_counters


@pytest.fixture
def fake_idp(monkeypatch, oidc_redis):
    idp = FakeIdp()
    monkeypatch.setattr(oidc_provider, "_get_json", idp.get_json)
    monkeypatch.setattr(oidc_provider, "_post_form", idp.post_form)
    for name, value in {
        "oidc_enabled": True,
        "oidc_issuer": ISSUER,
        "oidc_client_id": CLIENT_ID,
        "oidc_client_secret": CLIENT_SECRET,
        "oidc_redirect_uri": REDIRECT_URI,
        "oidc_scopes": "openid profile email",
        "oidc_auto_provision": True,
        "oidc_match_existing_by_email": False,
        "oidc_allowed_email_domains": "",
    }.items():
        monkeypatch.setattr(settings, name, value)
    oidc_provider.reset_metadata_cache()
    yield idp
    oidc_provider.reset_metadata_cache()


@pytest.fixture
def run(session_loop):
    """在同步用例里执行 ORM 协程，与同步 ASGI 客户端共用会话事件循环。"""
    return session_loop.run_until_complete


def authorize(client) -> dict:
    response = client.post(AUTHORIZE_PATH)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 20000
    return body["data"]


def callback_body(client, idp: FakeIdp, **overrides) -> dict:
    """发起一次授权并返回回调请求体，可用 overrides 篡改或删除字段。"""
    flow = authorize(client)
    body = {
        "authorizationCode": idp.grant(flow["authorizationUrl"]),
        "state": flow["state"],
        "flowSecret": flow["flowSecret"],
    }
    body.update(overrides)
    return {key: value for key, value in body.items() if value is not REMOVE}


def sso_login(client, idp: FakeIdp, **overrides):
    return client.post(LOGIN_PATH, json=callback_body(client, idp, **overrides))


def assert_oidc_error(response, message: str) -> None:
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["code"] == 40000
    assert body["message"] == message
    assert body["data"] is None
