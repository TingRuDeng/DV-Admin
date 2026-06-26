"""
Token 黑名单 Key 与内存清理 helper

这些函数保持无状态，避免 TokenBlacklistService 同时承载 Key 规则和存储流程。
"""

import hashlib
from datetime import datetime, timezone

BLACKLIST_PREFIX = "token_blacklist"
USER_TOKENS_PREFIX = "user_tokens"


def get_blacklist_key(token: str) -> str:
    """生成 Token 黑名单 Key，避免把完整 Token 写入 Redis Key。"""
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
    return f"{BLACKLIST_PREFIX}:{token_hash}"


def get_user_tokens_key(user_id: int) -> str:
    """生成用户 Token 集合 Key，保留既有测试和后续扩展入口。"""
    return f"{USER_TOKENS_PREFIX}:{user_id}"


def get_user_revocation_key(user_id: int) -> str:
    """生成用户批量撤销 Key。"""
    return f"{BLACKLIST_PREFIX}:user:{user_id}"


def cleanup_expired_memory_blacklist(memory_blacklist: dict[str, datetime]) -> None:
    """清理内存黑名单中过期的 Token Key。"""
    now = datetime.now(timezone.utc)
    expired_keys = [
        key for key, expires_at in memory_blacklist.items() if expires_at <= now
    ]
    for key in expired_keys:
        memory_blacklist.pop(key, None)
