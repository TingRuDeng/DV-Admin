"""
认证依赖的 Token 解析辅助函数。

这些函数不访问数据库和外部存储，只负责请求 Token 与 JWT payload 的同步校验。
"""

from typing import Any

from app.core.exceptions import AuthenticationError
from app.core.security import decode_token, get_token_subject, verify_token_type


def extract_bearer_token(oauth_token: str | None, authorization: str | None) -> str | None:
    """优先使用 OAuth2 token，其次从 Authorization 头提取 Bearer token。"""
    if oauth_token:
        return oauth_token

    if not authorization:
        return None

    scheme, _, param = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None

    return param or None


def require_access_token_payload(token: str) -> dict[str, Any]:
    """解码并校验 access token payload。"""
    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("无效的认证令牌")

    if not verify_token_type(payload, "access"):
        raise AuthenticationError("无效的令牌类型")

    return payload


def require_token_user_id(payload: dict[str, Any]) -> int:
    """从 Token payload 中提取用户 ID。"""
    user_id = get_token_subject(payload)
    if not user_id:
        raise AuthenticationError("无法获取用户信息")

    return int(user_id)
