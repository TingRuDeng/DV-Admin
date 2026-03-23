"""
安全工具模块

提供 JWT 认证、密码加密等安全相关功能。
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt", "django_pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    创建访问令牌

    Args:
        subject: 令牌主题（通常是用户ID）
        expires_delta: 过期时间增量
        extra_claims: 额外的声明数据

    Returns:
        JWT 令牌字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.effective_secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    创建刷新令牌

    Args:
        subject: 令牌主题（通常是用户ID）
        expires_delta: 过期时间增量

    Returns:
        JWT 刷新令牌字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.effective_secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """
    解码令牌

    Args:
        token: JWT 令牌字符串

    Returns:
        解码后的令牌数据，如果无效则返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.effective_secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """
    验证令牌类型

    Args:
        payload: 解码后的令牌数据
        expected_type: 期望的令牌类型（access 或 refresh）

    Returns:
        类型是否匹配
    """
    token_type = payload.get("type")
    return token_type == expected_type


def get_token_subject(payload: dict[str, Any]) -> str | None:
    """
    获取令牌主题（用户ID）

    Args:
        payload: 解码后的令牌数据

    Returns:
        用户ID字符串
    """
    return payload.get("sub")


def get_token_expiration(payload: dict[str, Any]) -> datetime | None:
    """
    获取令牌过期时间

    Args:
        payload: 解码后的令牌数据

    Returns:
        过期时间
    """
    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    return None


def get_token_issued_at(payload: dict[str, Any]) -> datetime | None:
    """
    获取令牌签发时间

    Args:
        payload: 解码后的令牌数据

    Returns:
        签发时间
    """
    iat = payload.get("iat")
    if iat:
        return datetime.fromtimestamp(iat, tz=timezone.utc)
    return None
