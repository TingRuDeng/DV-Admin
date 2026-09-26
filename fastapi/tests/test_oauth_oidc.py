"""OIDC 单点登录端点：发起、回调、ID Token 校验、state 一次性、限速与存储故障。"""

import base64
import hashlib
import socket
import time
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from oidc_fixtures import (
    AUTHORIZE_PATH,
    CLIENT_ID,
    CLIENT_SECRET,
    ISSUER,
    LOGIN_PATH,
    REDIRECT_URI,
    REMOVE,
    ROTATED_KEY,
    assert_oidc_error,
    authorize,
    callback_body,
    private_pem,
    public_jwk,
    sso_login,
)
from redis.asyncio import Redis

from app.core.config import settings
from app.core.login_throttle_policy import IP_ATTEMPT_LIMIT, rate_limit_keys
from app.core.oidc_policy import (
    MESSAGE_DISABLED,
    MESSAGE_FLOW_INVALID,
    MESSAGE_PROVIDER_FAILED,
    STATE_TTL_SECONDS,
    state_key,
)
from app.core.redis import redis_manager
from app.core.security import decode_token
from app.db.models.oauth import OidcIdentity, Users
from app.db.models.system import OperationLog
from app.middleware.request_logging import RequestLoggingMiddleware
from app.services import login_throttle, oidc_state

pytest_plugins = ["oidc_fixtures", "token_blacklist_fixtures"]

REAL_GET_OIDC_REDIS = oidc_state.get_oidc_redis


def test_disabled_oidc_rejects_both_endpoints(client, db, oidc_redis, monkeypatch):
    monkeypatch.setattr(settings, "oidc_enabled", False)

    assert_oidc_error(client.post(AUTHORIZE_PATH), MESSAGE_DISABLED)
    assert_oidc_error(
        client.post(LOGIN_PATH, json={"authorizationCode": "c", "state": "s", "flowSecret": "f"}),
        MESSAGE_DISABLED,
    )


def test_authorize_returns_pkce_url_and_stores_hashed_state(client, db, fake_idp, oidc_redis, run):
    flow = authorize(client)

    assert set(flow) == {"authorizationUrl", "state", "flowSecret"}
    parts = urlsplit(flow["authorizationUrl"])
    assert f"{parts.scheme}://{parts.netloc}{parts.path}" == fake_idp.discovery["authorization_endpoint"]
    query = {key: values[0] for key, values in parse_qs(parts.query).items()}
    assert query["response_type"] == "code"
    assert query["client_id"] == CLIENT_ID
    assert query["redirect_uri"] == REDIRECT_URI
    assert query["scope"] == "openid profile email"
    assert query["state"] == flow["state"]
    assert query["code_challenge_method"] == "S256"
    assert len(query["nonce"]) >= 32 and len(query["code_challenge"]) == 43

    key = state_key(flow["state"])
    record = run(oidc_redis.get(key))
    assert 0 < run(oidc_redis.ttl(key)) <= STATE_TTL_SECONDS
    assert flow["flowSecret"] not in record and flow["state"] not in record
    assert hashlib.sha256(flow["flowSecret"].encode()).hexdigest() in record
    assert query["nonce"] in record
    assert not run(oidc_redis.exists(f"oidc:state:{flow['state']}"))


def test_full_login_issues_local_tokens_usable_for_info_and_refresh(client, db, fake_idp, run):
    response = sso_login(client, fake_idp)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 20000
    tokens = body["data"]
    assert tokens["tokenType"] == "bearer"
    assert tokens["expiresIn"] == settings.access_token_expire_minutes * 60
    assert tokens["refreshExpiresIn"] == settings.refresh_token_expire_days * 86400

    user = run(Users.get(username="alice"))
    assert decode_token(tokens["accessToken"])["sub"] == str(user.id)
    assert user.last_login is not None
    identity = run(OidcIdentity.get(issuer=ISSUER, subject="idp-user-1"))
    assert identity.user_id == user.id and identity.last_login_at is not None
    assert identity.email == "alice@example.com"

    token_request = fake_idp.token_requests[0]
    assert token_request["url"] == fake_idp.discovery["token_endpoint"]
    assert token_request["form"]["grant_type"] == "authorization_code"
    assert token_request["form"]["redirect_uri"] == REDIRECT_URI
    expected_basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    assert token_request["headers"]["Authorization"] == f"Basic {expected_basic}"
    assert "client_secret" not in token_request["form"]

    info = client.get(
        "/api/v1/oauth/info/", headers={"Authorization": f"Bearer {tokens['accessToken']}"}
    )
    assert info.status_code == 200
    assert info.json()["data"]["username"] == "alice"

    refreshed = client.post(
        "/api/v1/oauth/refresh-token/", json={"refreshToken": tokens["refreshToken"]}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["data"]["accessToken"]


def test_public_client_sends_client_id_without_secret(client, db, fake_idp, monkeypatch):
    monkeypatch.setattr(settings, "oidc_client_secret", "")

    assert sso_login(client, fake_idp).status_code == 200

    token_request = fake_idp.token_requests[0]
    assert token_request["form"]["client_id"] == CLIENT_ID
    assert "Authorization" not in token_request["headers"]


def test_second_login_reuses_identity(client, db, fake_idp, run):
    first = sso_login(client, fake_idp)
    second = sso_login(client, fake_idp)

    assert first.status_code == second.status_code == 200
    assert run(Users.all().count()) == 1
    assert run(OidcIdentity.all().count()) == 1
    first_sub = decode_token(first.json()["data"]["accessToken"])["sub"]
    assert decode_token(second.json()["data"]["accessToken"])["sub"] == first_sub


def test_state_is_single_use(client, db, fake_idp):
    body = callback_body(client, fake_idp)
    assert client.post(LOGIN_PATH, json=body).status_code == 200

    body["authorizationCode"] = fake_idp.grant(authorize(client)["authorizationUrl"])
    assert_oidc_error(client.post(LOGIN_PATH, json=body), MESSAGE_FLOW_INVALID)


def test_unknown_state_is_rejected(client, db, fake_idp):
    assert_oidc_error(sso_login(client, fake_idp, state="never-issued"), MESSAGE_FLOW_INVALID)
    assert fake_idp.token_requests == []


def test_wrong_flow_secret_consumes_state(client, db, fake_idp, oidc_redis, run):
    body = callback_body(client, fake_idp)
    genuine_secret = body["flowSecret"]

    body["flowSecret"] = "attacker-guess"
    assert_oidc_error(client.post(LOGIN_PATH, json=body), MESSAGE_FLOW_INVALID)
    assert not run(oidc_redis.exists(state_key(body["state"])))

    body["flowSecret"] = genuine_secret
    assert_oidc_error(client.post(LOGIN_PATH, json=body), MESSAGE_FLOW_INVALID)
    assert fake_idp.token_requests == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"authorizationCode": REMOVE},
        {"state": ""},
        {"flowSecret": 12345},
        {"state": "s" * 2049},
        {"iss": 42},
        {"iss": "i" * 2049},
    ],
)
def test_malformed_callback_body_uses_flow_error_envelope(client, db, fake_idp, overrides):
    assert_oidc_error(sso_login(client, fake_idp, **overrides), MESSAGE_FLOW_INVALID)


@pytest.mark.parametrize(
    "content", [b"", b"{}", b'{"unexpected": "field"}', b"[]", b'"text"', b"null", b"{not json"]
)
def test_missing_or_malformed_body_uses_flow_error_envelope(client, db, fake_idp, content):
    response = client.post(
        LOGIN_PATH, content=content, headers={"Content-Type": "application/json"}
    )
    assert_oidc_error(response, MESSAGE_FLOW_INVALID)


def _now() -> int:
    return int(time.time())


ID_TOKEN_ATTACKS = {
    "nonce mismatch": lambda idp, nonce: idp.sign(idp.id_token_claims("another-nonce")),
    "iss mismatch": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce, iss="https://evil.example.test")
    ),
    "aud mismatch": lambda idp, nonce: idp.sign(idp.id_token_claims(nonce, aud="other-client")),
    "multi aud without azp": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce, aud=[CLIENT_ID, "other-client"])
    ),
    "azp mismatch": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce, aud=[CLIENT_ID, "other-client"], azp="other-client")
    ),
    "expired": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce, iat=_now() - 7200, exp=_now() - 3600)
    ),
    "missing sub": lambda idp, nonce: idp.sign(idp.id_token_claims(nonce, sub=REMOVE)),
    "alg none": lambda idp, nonce: jwt.encode(
        idp.id_token_claims(nonce), None, algorithm="none", headers={"kid": "primary"}
    ),
    "hs256 with client secret": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce), key=CLIENT_SECRET, algorithm="HS256"
    ),
    "signed by another key with a published kid": lambda idp, nonce: idp.sign(
        idp.id_token_claims(nonce), key=private_pem(ROTATED_KEY)
    ),
}


@pytest.mark.parametrize("attack", sorted(ID_TOKEN_ATTACKS))
def test_invalid_id_tokens_are_rejected(client, db, fake_idp, run, attack):
    fake_idp.id_token_factory = ID_TOKEN_ATTACKS[attack]

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_PROVIDER_FAILED)
    assert run(Users.all().count()) == 0


def test_token_endpoint_failure_is_rejected(client, db, fake_idp):
    body = callback_body(client, fake_idp)
    body["authorizationCode"] = "code-the-idp-never-issued"

    assert_oidc_error(client.post(LOGIN_PATH, json=body), MESSAGE_PROVIDER_FAILED)


def test_discovery_issuer_mismatch_is_rejected(client, db, fake_idp, oidc_redis, run):
    fake_idp.discovery["issuer"] = ISSUER + "/"

    assert_oidc_error(client.post(AUTHORIZE_PATH), MESSAGE_PROVIDER_FAILED)
    assert run(oidc_redis.keys("oidc:state:*")) == []


def test_callback_iss_mismatch_is_rejected(client, db, fake_idp):
    response = sso_login(client, fake_idp, iss="https://evil.example.test")

    assert_oidc_error(response, MESSAGE_PROVIDER_FAILED)
    assert fake_idp.token_requests == []


def test_callback_iss_required_when_provider_advertises_it(client, db, fake_idp):
    fake_idp.discovery["authorization_response_iss_parameter_supported"] = True

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_PROVIDER_FAILED)
    assert sso_login(client, fake_idp, iss=ISSUER).status_code == 200


def test_unknown_kid_refetches_jwks_once(client, db, fake_idp):
    assert sso_login(client, fake_idp).status_code == 200
    assert fake_idp.jwks_fetches == 1

    fake_idp.jwks = {"keys": [fake_idp.jwks["keys"][0], public_jwk(ROTATED_KEY, "rotated")]}
    fake_idp.signing_key, fake_idp.kid = ROTATED_KEY, "rotated"
    assert sso_login(client, fake_idp).status_code == 200
    assert fake_idp.jwks_fetches == 2

    assert sso_login(client, fake_idp).status_code == 200
    assert fake_idp.jwks_fetches == 2

    fake_idp.kid = "never-published"
    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_PROVIDER_FAILED)
    assert fake_idp.jwks_fetches == 3


def test_discovery_is_cached_in_process(client, db, fake_idp):
    authorize(client)
    authorize(client)

    assert fake_idp.discovery_fetches == 1


def test_misconfigured_provider_fails_without_network(client, db, fake_idp, monkeypatch):
    monkeypatch.setattr(settings, "oidc_redirect_uri", "")

    assert_oidc_error(client.post(AUTHORIZE_PATH), MESSAGE_PROVIDER_FAILED)
    assert_oidc_error(
        client.post(LOGIN_PATH, json={"authorizationCode": "c", "state": "s", "flowSecret": "f"}),
        MESSAGE_FLOW_INVALID,
    )
    assert fake_idp.discovery_fetches == 0


def _closed_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def test_state_store_outage_returns_503(client, db, fake_idp, monkeypatch, run):
    body = callback_body(client, fake_idp)
    broken = Redis.from_url(
        f"redis://127.0.0.1:{_closed_port()}/0", socket_connect_timeout=0.2, socket_timeout=0.2
    )
    monkeypatch.setattr(oidc_state, "get_oidc_redis", lambda: broken)
    try:
        for response in (client.post(AUTHORIZE_PATH), client.post(LOGIN_PATH, json=body)):
            assert response.status_code == 503
            assert response.json()["code"] == 503
    finally:
        run(broken.aclose())

    # 真实 getter 在 Redis 未初始化时抛 RuntimeError，同样必须 503 而不是降级。
    monkeypatch.setattr(oidc_state, "get_oidc_redis", REAL_GET_OIDC_REDIS)
    monkeypatch.setattr(redis_manager, "_client", None)
    assert client.post(AUTHORIZE_PATH).status_code == 503
    assert client.post(LOGIN_PATH, json=body).status_code == 503


def test_throttle_store_outage_returns_503(client, db, fake_idp, monkeypatch):
    def uninitialized():
        raise RuntimeError("Redis 未初始化")

    monkeypatch.setattr(login_throttle, "get_login_redis", uninitialized)

    assert client.post(AUTHORIZE_PATH).status_code == 503
    assert client.post(LOGIN_PATH, json={}).status_code == 503
    assert fake_idp.discovery_fetches == 0


def test_ip_throttle_limits_both_endpoints(client, db, fake_idp, oidc_redis, run):
    for _ in range(IP_ATTEMPT_LIMIT):
        assert client.post(AUTHORIZE_PATH).status_code == 200

    limited = [client.post(AUTHORIZE_PATH), client.post(LOGIN_PATH, json={})]
    for response in limited:
        assert response.status_code == 429
        assert 1 <= int(response.headers["Retry-After"]) <= 60

    ip_key = rate_limit_keys("", "127.0.0.1")[2]
    assert run(oidc_redis.zcard(ip_key)) == IP_ATTEMPT_LIMIT
    assert not run(oidc_redis.exists("login:oidc:failures", "login:oidc:cooldown"))


def test_operation_log_never_persists_code_or_flow_secret(client, db, fake_idp, run):
    success = callback_body(client, fake_idp)
    assert client.post(LOGIN_PATH, json=success).status_code == 200
    failure = callback_body(client, fake_idp, flowSecret="wrong-flow-secret-value")
    assert client.post(LOGIN_PATH, json=failure).status_code == 401

    rows = run(OperationLog.filter(path__startswith="/api/v1/oauth/oidc/").order_by("id"))
    assert {row.path for row in rows} == {AUTHORIZE_PATH, LOGIN_PATH}
    secrets = {
        success["authorizationCode"],
        success["flowSecret"],
        failure["authorizationCode"],
        "wrong-flow-secret-value",
    }
    for row in rows:
        persisted = " ".join(
            (row.request_body, str(row.request_context), row.response_body, row.error_msg)
        )
        assert not [secret for secret in secrets if secret in persisted]
        if row.path == AUTHORIZE_PATH:
            assert row.response_body == ""
            assert "flowSecret" not in persisted
    login_rows = [row for row in rows if row.path == LOGIN_PATH]
    assert all(row.request_context["body"]["flowSecret"] == "******" for row in login_rows)
    assert all(row.request_context["body"]["authorizationCode"] == "******" for row in login_rows)


def test_flow_secret_from_authorize_response_is_not_persisted(client, db, fake_idp, run):
    flow = authorize(client)

    row = run(OperationLog.get(path=AUTHORIZE_PATH))
    persisted = " ".join((row.request_body, str(row.request_context), row.response_body))
    assert flow["flowSecret"] not in persisted and flow["state"] not in persisted



def test_oidc_request_bodies_are_excluded_from_request_logs():
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)

    assert middleware._should_exclude_body(AUTHORIZE_PATH)
    assert middleware._should_exclude_body(LOGIN_PATH)
