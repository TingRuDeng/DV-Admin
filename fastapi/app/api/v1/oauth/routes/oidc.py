"""OIDC 单点登录 API 路由（授权码 + PKCE），两个端点均无需登录。"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.api.v1.oauth.routes.login import login_client_ip
from app.core.config import settings
from app.core.error_codes import ERROR_CODE
from app.core.exceptions import AuthenticationError
from app.core.oidc_policy import (
    MESSAGE_DISABLED,
    MESSAGE_FLOW_INVALID,
    OidcError,
    authorization_url,
    check_response_issuer,
    profile_from_claims,
    read_flow_record,
    start_flow,
)
from app.schemas.base import ResponseModel
from app.schemas.oauth import OidcAuthorization, OidcLogin, Token
from app.services.login_throttle import enforce_ip_limit
from app.services.login_tokens import issue_login_tokens
from app.services.oidc_accounts import record_oidc_login, resolve_oidc_user
from app.services.oidc_provider import get_discovery, redeem_authorization_code
from app.services.oidc_state import pop_flow_state, save_flow_state

router = APIRouter()

_FAILURE_EXAMPLE = {
    "description": "单点登录失败",
    "content": {
        "application/json": {
            "example": {"code": 40000, "message": "身份提供方校验失败", "data": None}
        }
    },
}


def _failure(error: OidcError) -> AuthenticationError:
    return AuthenticationError(error.message, code=ERROR_CODE)


async def _begin(request: Request) -> None:
    if not settings.oidc_enabled:
        raise AuthenticationError(MESSAGE_DISABLED, code=ERROR_CODE)
    await enforce_ip_limit(login_client_ip(request))


async def _read_callback(request: Request) -> OidcLogin:
    """自行解析请求体：任何不合法的回调都返回 40000，而不是框架的 422 结构。"""
    try:
        payload = json.loads(await request.body() or b"{}")
    except ValueError:
        raise OidcError(MESSAGE_FLOW_INVALID) from None
    if not isinstance(payload, dict):
        raise OidcError(MESSAGE_FLOW_INVALID)
    return OidcLogin.model_validate(payload)


@router.post(
    "/oidc/authorize/",
    response_model=ResponseModel[OidcAuthorization],
    summary="发起单点登录",
    description="""
## 发起 OIDC 单点登录

生成 state、nonce 和 PKCE verifier，返回身份提供方授权地址。

### 响应数据
- `authorizationUrl`: 浏览器跳转地址（包含 state、nonce、S256 code_challenge）
- `state`: 本次流程标识，10 分钟内有效且只能使用一次
- `flowSecret`: 与 state 绑定的一次性密钥，回调时必须原样提交，不要写入 URL

### 错误码
- `40000`: 未启用单点登录或身份提供方校验失败
- `429`: 同一 IP 请求过于频繁
- `503`: 登录保护或单点登录状态存储暂不可用
    """,
    responses={401: _FAILURE_EXAMPLE},
)
async def oidc_authorize(request: Request) -> ResponseModel[OidcAuthorization]:
    await _begin(request)
    try:
        discovery = await get_discovery()
    except OidcError as error:
        raise _failure(error) from None
    flow = start_flow()
    await save_flow_state(flow["state"], flow["record"])
    url = authorization_url(
        discovery,
        settings.oidc_client_id,
        settings.oidc_redirect_uri,
        settings.oidc_scopes,
        flow["state"],
        flow["nonce"],
        flow["code_verifier"],
    )
    return ResponseModel.success(
        data=OidcAuthorization(
            authorization_url=url,
            state=flow["state"],
            flow_secret=flow["flow_secret"],
        )
    )


@router.post(
    "/oidc/login/",
    response_model=ResponseModel[Token],
    summary="单点登录回调换取令牌",
    description="""
## 完成 OIDC 单点登录

提交身份提供方回调的授权码，校验 ID Token 后签发与密码登录相同的本地令牌。

### 请求参数
- `authorizationCode` (必填): 回调中的 `code`
- `state` (必填): 回调中的 `state`
- `flowSecret` (必填): 发起时返回的 `flowSecret`
- `iss` (可选): 回调中的 `iss`（RFC 9207）

### 响应数据
与 `/login/` 相同：`accessToken`、`refreshToken`、`tokenType`、`expiresIn`、`refreshExpiresIn`

### 错误码
- `40000`: 未启用、state 无效或已使用、身份提供方校验失败、账号未开通或已禁用
- `429`: 同一 IP 请求过于频繁
- `503`: 登录保护或单点登录状态存储暂不可用
    """,
    responses={401: _FAILURE_EXAMPLE},
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": OidcLogin.model_json_schema()}},
        }
    },
)
async def oidc_login(request: Request) -> ResponseModel[Token]:
    session_started_at = datetime.now(timezone.utc)
    await _begin(request)
    try:
        code, state, flow_secret, iss = (await _read_callback(request)).flow_fields()
        record = read_flow_record(await pop_flow_state(state), flow_secret)
        discovery = await get_discovery()
        check_response_issuer(discovery, iss)
        claims = await redeem_authorization_code(discovery, code, record)
        profile = profile_from_claims(claims)
        user = await resolve_oidc_user(profile, discovery["issuer"])
    except OidcError as error:
        raise _failure(error) from None
    await record_oidc_login(user, discovery["issuer"], profile["subject"])
    return ResponseModel.success(data=issue_login_tokens(user, session_started_at))
