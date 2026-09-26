# -*- coding: utf-8 -*-
"""OIDC 授权码登录：请求身份提供方、校验回调并解析本地账号。

协议判断全部复用与 FastAPI 字节一致的 oidc_policy，本模块只负责 IO 与持久化。
"""

import logging
import time
from dataclasses import dataclass

import requests
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from drf_admin.apps.oauth import login_throttle
from drf_admin.apps.oauth import oidc_policy as policy
from drf_admin.apps.oauth.models import OidcIdentity
from drf_admin.apps.system.models import Users
from drf_admin.settings_helpers import is_production_environment

logger = logging.getLogger("info")

MAX_PARAMETER_LENGTH = 2048
_metadata_cache: dict[tuple[str, str], tuple[float, dict]] = {}
_reported_config_errors: set[tuple[str, ...]] = set()


@dataclass(frozen=True)
class OidcConfig:
    issuer: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: str
    auto_provision: bool
    match_by_email: bool
    allowed_domains: tuple[str, ...]


def load_config() -> OidcConfig:
    if not settings.OIDC_ENABLED:
        raise policy.OidcError(policy.MESSAGE_DISABLED)
    errors = policy.settings_errors(
        settings.OIDC_ISSUER,
        settings.OIDC_CLIENT_ID,
        settings.OIDC_REDIRECT_URI,
        is_production_environment(settings.ENVIRONMENT),
    )
    if errors:
        # 非生产环境允许带病启动，但只提示一次，避免每次请求刷屏
        if tuple(errors) not in _reported_config_errors:
            _reported_config_errors.add(tuple(errors))
            logger.warning("单点登录配置无效: %s", "，".join(errors))
        raise policy.OidcError(policy.MESSAGE_PROVIDER_FAILED)
    return OidcConfig(
        issuer=settings.OIDC_ISSUER,
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
        redirect_uri=settings.OIDC_REDIRECT_URI,
        scopes=settings.OIDC_SCOPES,
        auto_provision=settings.OIDC_AUTO_PROVISION,
        match_by_email=settings.OIDC_MATCH_EXISTING_BY_EMAIL,
        allowed_domains=tuple(policy.split_setting(settings.OIDC_ALLOWED_EMAIL_DOMAINS)),
    )


# ---- 身份提供方 HTTP：只记录异常类名和状态码，不记录响应内容 ----


def _parse_json(response):
    if not 200 <= response.status_code < 300:
        logger.warning("身份提供方响应异常: HTTP %s", response.status_code)
        raise policy.OidcError()
    try:
        return response.json()
    except ValueError as error:
        logger.warning("身份提供方响应不是 JSON: HTTP %s", response.status_code)
        raise policy.OidcError() from error


def _get_json(url):
    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=policy.HTTP_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        logger.warning("身份提供方请求失败: %s", type(error).__name__)
        raise policy.OidcError() from error
    return _parse_json(response)


def _post_form(url, form, headers):
    try:
        response = requests.post(
            url,
            data=form,
            headers=headers,
            timeout=policy.HTTP_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        logger.warning("身份提供方请求失败: %s", type(error).__name__)
        raise policy.OidcError() from error
    return _parse_json(response)


def _cached(kind, issuer, load, refresh=False):
    key = (kind, issuer)
    entry = _metadata_cache.get(key)
    now = time.monotonic()
    if entry and not refresh and now - entry[0] < policy.METADATA_CACHE_SECONDS:
        return entry[1]
    value = load()
    _metadata_cache[key] = (now, value)
    return value


def reset_metadata_cache():
    """测试辅助：清空进程内 discovery/JWKS 缓存和配置告警记录。"""
    _metadata_cache.clear()
    _reported_config_errors.clear()


def get_discovery(config):
    def load():
        document = _get_json(policy.discovery_url(config.issuer))
        return policy.validate_discovery(document, config.issuer)

    return _cached("discovery", config.issuer, load)


def get_jwks(config, discovery, refresh=False):
    def load():
        jwks = _get_json(discovery["jwks_uri"])
        # 结构不对的 JWKS 不能进缓存，否则会持续拒绝登录直到过期
        if not isinstance(jwks, dict) or not isinstance(jwks.get("keys"), list):
            raise policy.OidcError()
        return jwks

    return _cached("jwks", config.issuer, load, refresh)


def _verify_id_token(config, discovery, id_token, nonce):
    try:
        jwks = get_jwks(config, discovery)
        return policy.verify_id_token(id_token, jwks, discovery, config.client_id, nonce)
    except policy.UnknownSigningKey:
        # 提供方可能已轮换密钥：强制刷新一次，仍找不到则按提供方校验失败处理
        jwks = get_jwks(config, discovery, refresh=True)
        return policy.verify_id_token(id_token, jwks, discovery, config.client_id, nonce)


# ---- 一次性 state 记录 ----


def _save_flow_record(state, record):
    try:
        login_throttle.get_login_redis().set(
            policy.state_key(state), record, ex=policy.STATE_TTL_SECONDS
        )
    except login_throttle.REDIS_ERRORS as error:
        raise login_throttle.LoginProtectionUnavailable() from error


def _pop_flow_record(state):
    """GET + DEL 放在同一个 MULTI/EXEC 中，同一 state 只能被消费一次。"""
    key = policy.state_key(state)
    try:
        pipeline = login_throttle.get_login_redis().pipeline(transaction=True)
        pipeline.get(key)
        pipeline.delete(key)
        raw, _deleted = pipeline.execute()
    except login_throttle.REDIS_ERRORS as error:
        raise login_throttle.LoginProtectionUnavailable() from error
    return raw


def _is_bounded_text(value):
    return isinstance(value, str) and len(value) <= MAX_PARAMETER_LENGTH


def _login_parameters(data):
    if not hasattr(data, "get"):
        data = {}
    required = [data.get(name) for name in ("authorization_code", "state", "flow_secret")]
    iss = data.get("iss")
    if not all(value and _is_bounded_text(value) for value in required):
        raise policy.OidcError(policy.MESSAGE_FLOW_INVALID)
    if iss is not None and not _is_bounded_text(iss):
        raise policy.OidcError(policy.MESSAGE_FLOW_INVALID)
    code, state, flow_secret = required
    return code, state, flow_secret, iss


# ---- 本地账号解析 ----


def _find_identity(issuer, subject):
    return (
        OidcIdentity.objects.select_related("user")
        .filter(issuer=issuer, subject=subject)
        .first()
    )


def _existing_user(config, issuer, profile):
    """按已验证邮箱匹配已有账号；超级管理员不参与匹配。"""
    if not (config.match_by_email and profile["email_verified"]):
        return None
    matches = list(
        Users.objects.filter(email__iexact=profile["email"], is_superuser=False)[:2]
    )
    if len(matches) > 1:
        raise policy.OidcError(policy.MESSAGE_EMAIL_AMBIGUOUS)
    if not matches:
        return None
    if matches[0].oidc_identities.filter(issuer=issuer).exists():
        # 该账号已绑定同一提供方的另一个身份，不能再被邮箱接管
        raise policy.OidcError(policy.MESSAGE_NOT_PROVISIONED)
    return matches[0]


def _create_user(issuer, profile):
    username = next(
        (
            candidate
            for candidate in policy.username_candidates(profile, issuer)
            if not Users.objects.filter(username=candidate).exists()
        ),
        None,
    )
    if username is None:
        raise policy.OidcError()
    # password=None 生成不可用密码；post_save 信号负责分配默认角色
    return Users.objects.create_user(
        username=username,
        password=None,
        name=profile["name"] or username[: policy.NAME_MAX_LENGTH],
        email=profile["email"],
        is_active=1,
    )


def _link_identity(config, issuer, profile):
    user = _existing_user(config, issuer, profile)
    if user is None and not (
        config.auto_provision and policy.email_domain_allowed(profile, config.allowed_domains)
    ):
        raise policy.OidcError(policy.MESSAGE_NOT_PROVISIONED)
    try:
        with transaction.atomic():
            if user is None:
                user = _create_user(issuer, profile)
            return OidcIdentity.objects.create(
                issuer=issuer, subject=profile["subject"], user=user, email=profile["email"]
            )
    except IntegrityError:
        # 并发首登：以先写入的绑定为准
        identity = _find_identity(issuer, profile["subject"])
        if identity is None:
            raise policy.OidcError() from None
        return identity


def resolve_identity(config, issuer, profile):
    identity = _find_identity(issuer, profile["subject"])
    if identity is None:
        identity = _link_identity(config, issuer, profile)
    if not identity.user.is_active:
        raise policy.OidcError(policy.MESSAGE_USER_DISABLED)
    return identity


# ---- 接口流程 ----


def start_authorization(client_ip):
    config = load_config()
    login_throttle.enforce_ip_limit(client_ip)
    discovery = get_discovery(config)
    flow = policy.start_flow()
    _save_flow_record(flow["state"], flow["record"])
    return {
        "authorizationUrl": policy.authorization_url(
            discovery,
            config.client_id,
            config.redirect_uri,
            config.scopes,
            flow["state"],
            flow["nonce"],
            flow["code_verifier"],
        ),
        "state": flow["state"],
        "flowSecret": flow["flow_secret"],
    }


def complete_login(data, client_ip):
    """校验回调并返回本地用户；任何 OidcError 都由视图转成 40000。"""
    config = load_config()
    login_throttle.enforce_ip_limit(client_ip)
    code, state, flow_secret, iss = _login_parameters(data)
    record = policy.read_flow_record(_pop_flow_record(state), flow_secret)
    discovery = get_discovery(config)
    policy.check_response_issuer(discovery, iss)
    url, form, headers = policy.token_request(
        discovery,
        config.client_id,
        config.client_secret,
        config.redirect_uri,
        code,
        record["codeVerifier"],
    )
    id_token = policy.id_token_from_response(_post_form(url, form, headers))
    claims = _verify_id_token(config, discovery, id_token, record["nonce"])
    profile = policy.profile_from_claims(claims)
    identity = resolve_identity(config, discovery["issuer"], profile)
    identity.last_login_at = timezone.now()
    identity.save(update_fields=["last_login_at", "update_time"])
    return identity.user
