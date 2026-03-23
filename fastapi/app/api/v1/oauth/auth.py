"""
认证 API 路由

提供登录、登出、Token 刷新等认证接口。
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_subject,
    verify_password,
    verify_token_type,
)
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import Token, UserInfo, UserLogin
from app.services.token_blacklist import token_blacklist_service

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
- `40001`: 用户名或密码错误
- `40002`: 用户已被禁用
- `40003`: 认证失败
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
                        "code": 40001,
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
        raise AuthenticationError("用户名或密码错误")

    # 验证密码
    if not verify_password(form_data.password, user.password):
        raise AuthenticationError("用户名或密码错误")

    # 检查用户状态
    if not user.is_active:
        raise AuthenticationError("用户已被禁用")

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
- `40001`: 用户名或密码错误
- `40002`: 用户已被禁用
- `40003`: 验证码错误
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
                        "code": 40001,
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
            raise AuthenticationError("验证码错误或已过期")

    # 查询用户
    user = await Users.get_or_none(username=login_data.username)
    if not user:
        raise AuthenticationError("用户名或密码错误")

    # 验证密码
    if not verify_password(login_data.password, user.password):
        raise AuthenticationError("用户名或密码错误")

    # 检查用户状态
    if not user.is_active:
        raise AuthenticationError("用户已被禁用")

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
    refresh_token: str = Query(..., alias="refreshToken"),
) -> ResponseModel[Token]:
    # 解码刷新令牌
    payload = decode_token(refresh_token)
    if not payload:
        raise AuthenticationError(message="无效的刷新令牌", code=40002)

    # 验证令牌类型
    if not verify_token_type(payload, "refresh"):
        raise AuthenticationError(message="无效的令牌类型", code=40002)

    # 获取用户ID
    user_id = get_token_subject(payload)
    if not user_id:
        raise AuthenticationError(message="无法获取用户信息", code=40002)

    # 查询用户
    user = await Users.get_or_none(id=int(user_id))
    if not user:
        raise AuthenticationError(message="用户不存在", code=40002)

    if not user.is_active:
        raise AuthenticationError(message="用户已被禁用", code=40002)

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


@router.get(
    "/info/",
    response_model=ResponseModel[UserInfo],
    summary="获取当前用户信息",
    description="""
## 获取当前登录用户信息

返回当前登录用户的详细信息，包括基本信息、部门、角色、权限等。

### 请求头
- `Authorization` (必填): Bearer {accessToken}

### 响应数据
- `id`: 用户ID
- `username`: 用户名
- `name`: 真实姓名
- `email`: 邮箱
- `mobile`: 手机号
- `avatar`: 头像URL
- `gender`: 性别（0: 未知, 1: 男, 2: 女）
- `isActive`: 是否激活（1: 是, 0: 否）
- `deptId`: 部门ID
- `deptName`: 部门名称
- `roleNames`: 角色名称列表（逗号分隔）
- `roles`: 角色列表（JSON字符串）
- `perms`: 权限标识列表
- `createdAt`: 创建时间
- `updatedAt`: 更新时间

### 使用说明
1. 前端在用户登录后调用此接口获取用户信息
2. 用于显示用户头像、名称等信息
3. 用于前端权限控制（根据 `perms` 字段）

### 错误码
- `401`: 未授权，令牌无效或已过期
    """,
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "id": 1,
                            "username": "admin",
                            "name": "管理员",
                            "email": "admin@example.com",
                            "mobile": "13800138000",
                            "avatar": "/media/avatar/admin.png",
                            "gender": 1,
                            "isActive": 1,
                            "deptId": 1,
                            "deptName": "技术部",
                            "roleNames": "管理员、超级管理员",
                            "roles": "[\"管理员\", \"超级管理员\"]",
                            "perms": ["system:users:query", "system:users:add", "system:users:edit"],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z"
                        }
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
async def get_current_user_info(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[UserInfo]:
    # 获取部门名称
    dept_name = None
    if current_user.dept_id:
        from app.db.models.system import Departments

        dept = await Departments.get_or_none(id=current_user.dept_id)
        if dept:
            dept_name = dept.name

    # 获取角色名称
    await current_user.fetch_related("roles")
    role_names = "、".join([role.name for role in current_user.roles])

    # 构造 roles (JSON字符串)
    import json
    roles_json = json.dumps([role.name for role in current_user.roles])

    # 获取权限
    permissions = await current_user.get_permissions()

    # 处理头像 URL
    avatar = current_user.avatar
    if avatar and not avatar.startswith(("http", "/media")):
        avatar = f"/media/{avatar}"

    user_info = UserInfo(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email if current_user.email else "",
        mobile=current_user.mobile if current_user.mobile else "",
        avatar=avatar,
        gender=current_user.gender,
        is_active=current_user.is_active,
        dept_id=current_user.dept_id,
        dept_name=dept_name if dept_name else "",
        role_names=role_names,
        roles=roles_json,
        perms=permissions,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

    return ResponseModel.success(data=user_info)


@router.get(
    "/menus/routes/",
    response_model=ResponseModel[list],
    summary="获取用户菜单路由",
    description="""
## 获取当前用户的菜单路由

返回当前用户有权访问的菜单列表，用于前端动态路由生成。

### 请求头
- `Authorization` (必填): Bearer {accessToken}

### 响应数据
返回菜单树形结构，每个菜单项包含：
- `id`: 菜单ID
- `name`: 菜单名称
- `type`: 菜单类型（MENU: 菜单, BUTTON: 按钮, API: 接口）
- `routeName`: 路由名称
- `routePath`: 路由路径
- `component`: 组件路径
- `sort`: 排序
- `visible`: 是否可见
- `icon`: 图标
- `redirect`: 重定向路径
- `perm`: 权限标识
- `keepAlive`: 是否缓存
- `alwaysShow`: 是否一直显示
- `params`: 路由参数
- `children`: 子菜单列表

### 使用说明
1. 前端根据返回的菜单数据动态生成路由
2. 根据 `visible` 字段控制菜单显示
3. 根据 `children` 递归生成子菜单

### 错误码
- `401`: 未授权，令牌无效或已过期
    """,
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": [
                            {
                                "id": 1,
                                "name": "系统管理",
                                "type": "MENU",
                                "routeName": "System",
                                "routePath": "/system",
                                "component": "LAYOUT",
                                "sort": 1,
                                "visible": 1,
                                "icon": "setting",
                                "children": [
                                    {
                                        "id": 2,
                                        "name": "用户管理",
                                        "type": "MENU",
                                        "routeName": "User",
                                        "routePath": "user",
                                        "component": "/system/user/index",
                                        "sort": 1,
                                        "visible": 1,
                                        "icon": "user",
                                        "children": []
                                    }
                                ]
                            }
                        ]
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
async def get_user_menus(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[list]:
    menu_tree = await current_user.get_menus()

    return ResponseModel.success(data=menu_tree)


@router.get(
    "/captcha/",
    response_model=ResponseModel[dict],
    summary="获取验证码",
    description="""
## 获取图形验证码

生成并返回图形验证码，用于登录验证。

### 功能说明
1. 生成随机验证码
2. 返回验证码图片的 Base64 编码
3. 返回验证码缓存 key，用于后续验证

### 响应数据
- `captchaKey`: 验证码缓存 key，登录时需要传递
- `captchaBase64`: 验证码图片的 Base64 编码，可直接在 img 标签中使用

### 使用说明
1. 前端调用此接口获取验证码
2. 将 `captchaBase64` 设置为 img 标签的 src
3. 用户输入验证码后，将 `captchaKey` 和用户输入的验证码一起传递给登录接口
4. 验证码有效期通常为 5 分钟

### 示例
```html
<img src="data:image/png;base64,{captchaBase64}" />
```
    """,
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "captchaKey": "550e8400-e29b-41d4-a716-446655440000",
                            "captchaBase64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
                        }
                    }
                }
            }
        }
    }
)
async def get_captcha(
    request: Request,
) -> ResponseModel[dict]:
    import base64

    from captcha.image import ImageCaptcha

    from app.services.captcha_service import create_captcha

    # 创建验证码（自动存储到缓存）
    captcha_key, captcha_code = await create_captcha(length=4)

    # 生成验证码图片
    image = ImageCaptcha()
    data = image.generate(captcha_code)
    image_base64 = base64.b64encode(data.read()).decode()

    return ResponseModel.success(
        data={
            "captchaKey": captcha_key,
            "captchaBase64": f"data:image/png;base64,{image_base64}",
        }
    )
