"""
API 依赖模块

定义 FastAPI 依赖注入函数，用于认证、权限检查等。
"""


from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import AuthenticationError, PermissionDenied
from app.core.security import (
    decode_token,
    get_token_issued_at,
    get_token_subject,
    verify_token_type,
)
from app.db.models.oauth import Users
from app.services.token_blacklist import token_blacklist_service
from fastapi import Depends, Header, Request

# OAuth2 密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/oauth/token", auto_error=False)


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    authorization: str | None = Header(None),
) -> Users:
    """
    获取当前用户

    从请求中提取并验证 JWT 令牌，返回当前用户对象。

    Args:
        request: FastAPI 请求对象
        token: OAuth2 令牌
        authorization: Authorization 头

    Returns:
        当前用户对象

    Raises:
        AuthenticationError: 认证失败
    """
    # 优先从 OAuth2 scheme 获取 token
    if not token and authorization:
        # 从 Authorization 头解析 token
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer":
            token = param

    if not token:
        raise AuthenticationError("未提供认证令牌")

    # 检查 Token 是否在黑名单中
    is_blacklisted = await token_blacklist_service.is_token_blacklisted(token)
    if is_blacklisted:
        raise AuthenticationError("令牌已被撤销")

    # 解码令牌
    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("无效的认证令牌")

    # 验证令牌类型
    if not verify_token_type(payload, "access"):
        raise AuthenticationError("无效的令牌类型")

    # 获取用户ID
    user_id = get_token_subject(payload)
    if not user_id:
        raise AuthenticationError("无法获取用户信息")

    # 检查用户的 Token 是否已被批量撤销
    token_issued_at = get_token_issued_at(payload)
    if token_issued_at:
        is_revoked = await token_blacklist_service.is_user_tokens_revoked(
            int(user_id), token_issued_at
        )
        if is_revoked:
            raise AuthenticationError("令牌已被撤销")

    # 查询用户
    user = await Users.get_or_none(id=int(user_id))
    if not user:
        raise AuthenticationError("用户不存在")

    if not user.is_active:
        raise AuthenticationError("用户已被禁用")

    # 将用户信息存储在请求状态中，供后续使用
    request.state.user = user
    request.state.user_id = user.id

    return user


async def get_current_active_user(
    current_user: Users = Depends(get_current_user),
) -> Users:
    """
    获取当前活跃用户

    确保用户处于激活状态。

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户对象
    """
    if not current_user.is_active:
        raise AuthenticationError("用户已被禁用")
    return current_user


class PermissionChecker:
    """
    权限检查器

    用于检查用户是否具有指定权限。
    """

    def __init__(self, *required_perms: str):
        """
        初始化权限检查器

        Args:
            required_perms: 所需的权限标识列表
        """
        self.required_perms = set(required_perms)

    async def __call__(self, user: Users = Depends(get_current_user)) -> Users:
        """
        检查权限

        Args:
            user: 当前用户

        Returns:
            用户对象

        Raises:
            PermissionDenied: 权限不足
        """
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return user

        # 获取用户权限
        user_perms = await user.get_permissions()
        user_perms_set = set(user_perms)

        # 检查是否有所需权限
        if not self.required_perms.issubset(user_perms_set):
            missing = self.required_perms - user_perms_set
            raise PermissionDenied(f"缺少权限: {', '.join(missing)}")

        return user


class RoleChecker:
    """
    角色检查器

    用于检查用户是否具有指定角色。
    """

    def __init__(self, *required_roles: str):
        """
        初始化角色检查器

        Args:
            required_roles: 所需的角色编码列表
        """
        self.required_roles = set(required_roles)

    async def __call__(self, user: Users = Depends(get_current_user)) -> Users:
        """
        检查角色

        Args:
            user: 当前用户

        Returns:
            用户对象

        Raises:
            PermissionDenied: 权限不足
        """
        # 超级管理员拥有所有角色权限
        if user.is_superuser:
            return user

        # 获取用户角色
        await user.fetch_related("roles")
        user_roles = {role.code for role in user.roles if role.code}

        # 检查是否有所需角色
        if not self.required_roles.issubset(user_roles):
            missing = self.required_roles - user_roles
            raise PermissionDenied(f"缺少角色: {', '.join(missing)}")

        return user


# 常用依赖
CurrentUser = Depends(get_current_user)
CurrentActiveUser = Depends(get_current_active_user)


# 权限依赖工厂函数
def require_permissions(*perms: str):
    """
    创建权限检查依赖

    Args:
        perms: 所需的权限标识

    Returns:
        权限检查依赖
    """
    return Depends(PermissionChecker(*perms))


def require_roles(*roles: str):
    """
    创建角色检查依赖

    Args:
        roles: 所需的角色编码

    Returns:
        角色检查依赖
    """
    return Depends(RoleChecker(*roles))


# 超级管理员检查
async def require_superuser(user: Users = Depends(get_current_user)) -> Users:
    """
    要求超级管理员权限

    Args:
        user: 当前用户

    Returns:
        用户对象

    Raises:
        PermissionDenied: 不是超级管理员
    """
    if not user.is_superuser:
        raise PermissionDenied("需要超级管理员权限")
    return user


RequireSuperuser = Depends(require_superuser)
