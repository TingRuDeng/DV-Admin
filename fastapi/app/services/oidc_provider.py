"""与身份提供方的 HTTP 交互：discovery、JWKS、授权码兑换和 ID Token 校验。

所有请求都有超时、不跟随重定向；日志只记录异常类名或状态码，不记录令牌、授权码或响应内容。
"""

import time
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings
from app.core.oidc_policy import (
    HTTP_TIMEOUT_SECONDS,
    MESSAGE_PROVIDER_FAILED,
    METADATA_CACHE_SECONDS,
    OidcError,
    UnknownSigningKey,
    discovery_url,
    id_token_from_response,
    token_request,
    validate_discovery,
    verify_id_token,
)

_ACCEPT_JSON = {"Accept": "application/json"}
# InvalidURL 不是 HTTPError 子类；discovery 给出畸形端点时也必须按身份提供方失败处理。
_HTTP_FAILURES = (httpx.HTTPError, httpx.InvalidURL)
_metadata_cache: dict[tuple[str, str], tuple[float, Any]] = {}
_config_warning_logged = False


def reset_metadata_cache() -> None:
    """清空进程内 discovery/JWKS 缓存和配置告警标记（测试用）。"""
    global _config_warning_logged
    _metadata_cache.clear()
    _config_warning_logged = False


def ensure_provider_configured() -> None:
    """非生产环境配置不完整时，请求统一失败并只告警一次；生产环境在启动时已拒绝。"""
    global _config_warning_logged
    errors = settings.oidc_config_errors
    if not errors:
        return
    if not _config_warning_logged:
        _config_warning_logged = True
        logger.warning("OIDC 单点登录配置无效：" + "；".join(errors))
    raise OidcError(MESSAGE_PROVIDER_FAILED)


def _http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=False)


def _json_payload(response: httpx.Response) -> Any:
    if not 200 <= response.status_code < 300:
        logger.warning(f"OIDC 身份提供方返回非成功状态: {response.status_code}")
        raise OidcError()
    try:
        return response.json()
    except ValueError:
        logger.warning("OIDC 身份提供方返回了非 JSON 响应")
        raise OidcError() from None


async def _get_json(url: str) -> Any:
    try:
        async with _http_client() as client:
            response = await client.get(url, headers=_ACCEPT_JSON)
    except _HTTP_FAILURES as error:
        logger.warning(f"OIDC 身份提供方请求失败: {type(error).__name__}")
        raise OidcError() from None
    return _json_payload(response)


async def _post_form(url: str, form: dict[str, str], headers: dict[str, str]) -> Any:
    try:
        async with _http_client() as client:
            response = await client.post(url, data=form, headers={**_ACCEPT_JSON, **headers})
    except _HTTP_FAILURES as error:
        logger.warning(f"OIDC 令牌端点请求失败: {type(error).__name__}")
        raise OidcError() from None
    return _json_payload(response)


def _cached(key: tuple[str, str]) -> Any:
    entry = _metadata_cache.get(key)
    if entry and time.monotonic() - entry[0] < METADATA_CACHE_SECONDS:
        return entry[1]
    return None


async def get_discovery() -> dict:
    """读取并校验 discovery；只缓存校验通过的文档，首次请求时才访问网络。"""
    ensure_provider_configured()
    issuer = settings.oidc_issuer
    key = ("discovery", issuer)
    discovery = _cached(key)
    if discovery is None:
        discovery = validate_discovery(await _get_json(discovery_url(issuer)), issuer)
        _metadata_cache[key] = (time.monotonic(), discovery)
    return discovery


async def get_jwks(discovery: dict, force: bool = False) -> Any:
    key = ("jwks", discovery["issuer"] + "|" + discovery["jwks_uri"])
    jwks = None if force else _cached(key)
    if jwks is None:
        jwks = await _get_json(discovery["jwks_uri"])
        _metadata_cache[key] = (time.monotonic(), jwks)
    return jwks


async def redeem_authorization_code(discovery: dict, code: str, record: dict[str, str]) -> dict:
    """用授权码和 PKCE verifier 换取 ID Token，校验通过后返回 claims。"""
    url, form, headers = token_request(
        discovery,
        settings.oidc_client_id,
        settings.oidc_client_secret,
        settings.oidc_redirect_uri,
        code,
        record["codeVerifier"],
    )
    id_token = id_token_from_response(await _post_form(url, form, headers))
    arguments = (discovery, settings.oidc_client_id, record["nonce"])
    try:
        return verify_id_token(id_token, await get_jwks(discovery), *arguments)
    except UnknownSigningKey:
        pass
    # kid 不在缓存的 JWKS 中：身份提供方可能已轮换密钥，强制刷新一次后重试。
    try:
        return verify_id_token(id_token, await get_jwks(discovery, force=True), *arguments)
    except UnknownSigningKey:
        raise OidcError() from None
