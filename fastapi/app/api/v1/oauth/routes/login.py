"""OAuth 登录相关 API 路由。"""

from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.error_codes import ERROR_CODE
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import Token, UserLogin

router = APIRouter()

@router.post(
    "/token/",
    response_model=ResponseModel[Token],
    summary="OAuth2 登录获取令牌",
    description="""
## OAuth2 兼容的登录接口

使用用户名和密码获取访问令牌，适用于 OAuth2 标准流程。

### 请求格式
- Content-Type: `application/x-www-form-urlencoded`
- 请求体参数：
  - `username` (必填): 用户名
  - `password` (必填): 密码
  - `grant_type` (可选): 授权类型，通常为 `password`
  - `scope` (可选): 权限范围

### 响应数据
返回包含以下字段的令牌信息：
- `accessToken`: 访问令牌，用于 API 认证
- `refreshToken`: 刷新令牌，用于获取新的访问令牌
- `tokenType`: 令牌类型，固定为 `bearer`
- `expiresIn`: 访问令牌过期时间（秒）
- `refreshExpiresIn`: 刷新令牌过期时间（秒）

### 错误码
- `40000`: 用户名或密码错误、用户已被禁用或认证失败
    """,
    responses={
        200: {
            "description": "登录成功",
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
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": 40000,
                        "message": "用户名或密码错误",
                        "data": None
                    }
                }
            }
        }
    }
)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> ResponseModel[Token]:
    # 查询用户
    user = await Users.get_or_none(username=form_data.username)
    if not user:
        raise AuthenticationError("用户名或密码错误", code=ERROR_CODE)

    # 验证密码
    if not verify_password(form_data.password, user.password):
        raise AuthenticationError("用户名或密码错误", code=ERROR_CODE)

    # 检查用户状态
    if not user.is_active:
        raise AuthenticationError("用户已被禁用", code=ERROR_CODE)

    # 更新最后登录时间
    from datetime import datetime, timezone

    user.last_login = datetime.now(timezone.utc)
    await user.save()

    # 生成令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        extra_claims={"username": user.username, "name": user.name},
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )

    return ResponseModel.success(
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )
    )


@router.post(
    "/login/",
    response_model=ResponseModel[Token],
    summary="用户登录",
    description="""
## 用户登录接口

标准的登录接口，支持用户名密码登录和验证码验证。

### 请求参数
- `username` (必填): 用户名，长度 3-50 字符
- `password` (必填): 密码，长度 6-20 字符
- `captchaKey` (可选): 验证码缓存 key，由 `/captcha/` 接口返回
- `captchaCode` (可选): 用户输入的验证码

### 响应数据
返回包含以下字段的令牌信息：
- `accessToken`: 访问令牌，有效期默认 2 小时
- `refreshToken`: 刷新令牌，有效期默认 7 天
- `tokenType`: 令牌类型，固定为 `bearer`
- `expiresIn`: 访问令牌过期时间（秒）
- `refreshExpiresIn`: 刷新令牌过期时间（秒）

### 使用说明
1. 登录成功后，将 `accessToken` 存储在本地
2. 后续请求在 Header 中携带：`Authorization: Bearer {accessToken}`
3. 当 `accessToken` 过期时，使用 `/refresh-token/` 接口刷新令牌

### 错误码
- `40000`: 用户名或密码错误、用户已被禁用或验证码错误
    """,
    responses={
        200: {
            "description": "登录成功",
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
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": 40000,
                        "message": "用户名或密码错误",
                        "data": None
                    }
                }
            }
        }
    }
)
async def login(
    request: Request,
    login_data: UserLogin,
) -> ResponseModel[Token]:
    from app.services.captcha_service import verify_captcha

    # 验证码验证（如果提供了验证码）
    if login_data.captcha_key and login_data.captcha_code:
        is_valid = await verify_captcha(
            login_data.captcha_key,
            login_data.captcha_code,
            delete=True  # 验证后删除验证码
        )
        if not is_valid:
            raise AuthenticationError("验证码错误或已过期", code=ERROR_CODE)

    # 查询用户
    user = await Users.get_or_none(username=login_data.username)
    if not user:
        raise AuthenticationError("用户名或密码错误", code=ERROR_CODE)

    # 验证密码
    if not verify_password(login_data.password, user.password):
        raise AuthenticationError("用户名或密码错误", code=ERROR_CODE)

    # 检查用户状态
    if not user.is_active:
        raise AuthenticationError("用户已被禁用", code=ERROR_CODE)

    # 更新最后登录时间
    from datetime import datetime, timezone

    user.last_login = datetime.now(timezone.utc)
    await user.save()

    # 生成令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        extra_claims={"username": user.username, "name": user.name},
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )

    return ResponseModel.success(
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )
    )

