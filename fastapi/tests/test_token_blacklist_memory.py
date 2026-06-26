"""
Token 黑名单内存存储 helper 测试。
"""

from datetime import datetime, timedelta, timezone

from app.services.token_blacklist_memory import TokenBlacklistMemoryStore


class TestTokenBlacklistMemoryStore:
    """测试 Redis 不可用时使用的内存存储 helper。"""

    def test_has_token_cleans_expired_entries(self):
        """查询内存黑名单时必须先清理过期 Token。"""
        store = TokenBlacklistMemoryStore()
        active_key = "token_blacklist:active"
        expired_key = "token_blacklist:expired"
        now = datetime.now(timezone.utc)

        store.add_token(active_key, now + timedelta(minutes=5))
        store.add_token(expired_key, now - timedelta(minutes=5))

        assert store.has_token(active_key) is True
        assert store.has_token(expired_key) is False
        assert expired_key not in store.blacklist

    def test_user_revocation_compares_token_issue_time(self):
        """签发时间早于内存撤销时间的用户 Token 应视为已撤销。"""
        store = TokenBlacklistMemoryStore()
        now = datetime.now(timezone.utc)

        store.revoke_user(123, now)

        assert store.is_user_revoked(123, now - timedelta(seconds=1)) is True
        assert store.is_user_revoked(123, now + timedelta(seconds=1)) is False

    def test_clear_user_revocation_removes_marker(self):
        """清除用户撤销标记后不应继续判定为已撤销。"""
        store = TokenBlacklistMemoryStore()
        now = datetime.now(timezone.utc)

        store.revoke_user(123, now)
        store.clear_user_revocation(123)

        assert store.is_user_revoked(123, now - timedelta(seconds=1)) is False
