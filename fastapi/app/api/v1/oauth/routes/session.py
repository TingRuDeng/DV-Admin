"""OAuth 会话相关 API 路由。"""

from datetime import timedelta

from fastapi import APIRouter, Request

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.error_codes import REFRESH_TOKEN_INVALID_CODE
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_subject,
    verify_token_type,
)
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import RefreshTokenRequest, Token
from app.services.token_blacklist import token_blacklist_service

router = APIRouter()

@router.post(
    "/refresh-token/",
    response_model=ResponseModel[Token],
    summary="刷新访问令牌",
    description="""
## 刷新访问令牌

使用刷新令牌获取新的访问令牌和刷新令牌。

### 请求参数
- `refreshToken` (必填): 刷新令牌，登录时返回的 `refreshToken` 字段

### 响应数据
返回新的令牌信息：
- `accessToken`: 新的访问令牌
- `refreshToken`: 新的刷新令牌
- `tokenType`: 令牌类型，固定为 `bearer`
- `expiresIn`: 访问令牌过期时间（秒）
- `refreshExpiresIn`: 刷新令牌过期时间（秒）

### 使用说明
1. 当 `accessToken` 过期时，使用此接口获取新令牌
2. 每次刷新都会生成新的访问令牌和刷新令牌
3. 旧的刷新令牌将失效
4. 如果刷新令牌也已过期，需要重新登录

### 错误码
- `40002`: 无效的刷新令牌
- `40002`: 无效的令牌类型
- `40002`: 用户不存在或已被禁用
    """,
    responses={
        200: {
            "description": "刷新成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "tokenType": "bearer",
                            "expiresIn": 7200,
                            "refreshExpiresIn": 604800
                        }
                    }
                }
            }
        },
        401: {
            "description": "刷新令牌无效",
            "content": {
                "application/json": {
                    "example": {
                        "code": 40002,
                        "message": "无效的刷新令牌",
                        "data": None
                    }
                }
            }
        }
    }
)
async def refresh_token(
    request: Request,
    token_data: RefreshTokenRequest,
) -> ResponseModel[Token]:
    # 解码刷新令牌
    payload = decode_token(token_data.refresh_token)
    if not payload:
        raise AuthenticationError(message="无效的刷新令牌", code=REFRESH_TOKEN_INVALID_CODE)

    # 验证令牌类型
    if not verify_token_type(payload, "refresh"):
        raise AuthenticationError(message="无效的令牌类型", code=REFRESH_TOKEN_INVALID_CODE)

    # 获取用户ID
    user_id = get_token_subject(payload)
    if not user_id:
        raise AuthenticationError(message="无法获取用户信息", code=REFRESH_TOKEN_INVALID_CODE)

    # 查询用户
    user = await Users.get_or_none(id=int(user_id))
    if not user:
        raise AuthenticationError(message="用户不存在", code=REFRESH_TOKEN_INVALID_CODE)

    if not user.is_active:
        raise AuthenticationError(message="用户已被禁用", code=REFRESH_TOKEN_INVALID_CODE)

    # 生成新的令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    new_access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        extra_claims={"username": user.username, "name": user.name},
    )
    new_refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )

    return ResponseModel.success(
        data=Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )
    )


@router.post(
    "/logout/",
    response_model=ResponseModel[None],
    summary="用户登出",
    description="""
## 用户登出接口

用户主动登出，清除登录状态。

### 请求头
- `Authorization` (必填): Bearer {accessToken}

### 功能说明
1. 记录用户登出日志
2. 由于 JWT 是无状态的，服务端不维护会话状态
3. 如需实现令牌黑名单功能，可在此接口将令牌加入黑名单

### 使用说明
1. 前端调用此接口后，清除本地存储的令牌
2. 重定向到登录页面

### 错误码
- `401`: 未授权，令牌无效或已过期
    """,
    responses={
        200: {
            "description": "登出成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "登出成功",
                        "data": None
                    }
                }
            }
        },
        401: {
            "description": "未授权",
            "content": {
                "application/json": {
                    "example": {
                        "code": 401,
                        "message": "未授权访问",
                        "data": None
                    }
                }
            }
        }
    }
)
async def logout(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[None]:
    # 从请求头获取 Token
    authorization = request.headers.get("Authorization")
    if authorization:
        # 解析 Authorization 头
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            # 将访问令牌加入黑名单
            await token_blacklist_service.add_token_to_blacklist(
                token=token,
                user_id=current_user.id,
                reason="logout",
            )

    return ResponseModel.success(message="登出成功")

