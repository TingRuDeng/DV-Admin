from datetime import datetime

from app.services.token_blacklist_keys import cleanup_expired_memory_blacklist


class TokenBlacklistMemoryStore:
    """Token 黑名单内存降级存储，只在 Redis 不可用时使用。"""

    def __init__(self) -> None:
        """初始化内存黑名单和用户撤销标记。"""
        self.blacklist: dict[str, datetime] = {}
        self.user_revocations: dict[int, datetime] = {}

    def add_token(self, key: str, expires_at: datetime) -> None:
        """记录单个 Token 黑名单过期时间。"""
        self.blacklist[key] = expires_at

    def has_token(self, key: str) -> bool:
        """清理过期项后检查 Token 是否仍在内存黑名单中。"""
        self.cleanup_expired_tokens()
        return key in self.blacklist

    def cleanup_expired_tokens(self) -> None:
        """清理已过期的内存黑名单 Token。"""
        cleanup_expired_memory_blacklist(self.blacklist)

    def remove_token(self, key: str) -> None:
        """从内存黑名单移除 Token。"""
        self.blacklist.pop(key, None)

    def revoke_user(self, user_id: int, revoked_at: datetime) -> None:
        """记录用户级批量撤销时间。"""
        self.user_revocations[user_id] = revoked_at

    def is_user_revoked(self, user_id: int, token_issued_at: datetime) -> bool:
        """检查用户 Token 签发时间是否早于内存撤销时间。"""
        revoked_at = self.user_revocations.get(user_id)
        return revoked_at is not None and token_issued_at < revoked_at

    def clear_user_revocation(self, user_id: int) -> None:
        """清除用户级批量撤销标记。"""
        self.user_revocations.pop(user_id, None)
