"""
Token 黑名单记录构造辅助函数。

本模块只处理无副作用的数据构造，Redis 与内存存储分支仍由服务层编排。
"""

from dataclasses import dataclass
from datetime import datetime

from app.services.token_blacklist_keys import get_blacklist_key, get_user_revocation_key


@dataclass(frozen=True)
class TokenBlacklistRecord:
    """Token 黑名单写入 Redis 或内存前的标准化记录。"""

    key: str
    ttl: int
    expires_at: datetime
    value: dict[str, int | str | None]


@dataclass(frozen=True)
class UserRevocationRecord:
    """用户级 Token 撤销写入 Redis 或内存前的标准化记录。"""

    key: str
    ttl: int
    revoked_at: datetime


def build_token_blacklist_record(
    *,
    token: str,
    user_id: int | None,
    reason: str,
    expires_at: datetime,
    revoked_at: datetime,
) -> TokenBlacklistRecord | None:
    """根据过期时间构造黑名单记录，已过期 Token 返回 None。"""
    ttl = int((expires_at - revoked_at).total_seconds())
    if ttl <= 0:
        return None

    return TokenBlacklistRecord(
        key=get_blacklist_key(token),
        ttl=ttl,
        expires_at=expires_at,
        value={
            "user_id": user_id,
            "reason": reason,
            "revoked_at": revoked_at.isoformat(),
        },
    )


def build_user_revocation_record(
    *,
    user_id: int,
    refresh_token_expire_days: int,
    revoked_at: datetime,
) -> UserRevocationRecord:
    """构造用户级 Token 批量撤销记录。"""
    return UserRevocationRecord(
        key=get_user_revocation_key(user_id),
        ttl=refresh_token_expire_days * 24 * 60 * 60,
        revoked_at=revoked_at,
    )


def is_token_revoked_by_time(token_issued_at: datetime, revoked_at_str: str) -> bool:
    """根据 Token 签发时间和用户撤销时间判断是否已撤销。"""
    revoked_at = datetime.fromisoformat(revoked_at_str)
    return token_issued_at < revoked_at
