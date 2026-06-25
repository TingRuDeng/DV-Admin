"""
Token 黑名单内存降级测试。
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.services.token_blacklist import TokenBlacklistService

pytest_plugins = ["token_blacklist_fixtures"]


class TestTokenBlacklistMemoryFallback:
    """测试 Redis 不可用时的内存降级行为。"""

    @pytest.mark.asyncio
    async def test_falls_back_to_memory_when_redis_unavailable(self):
        """Redis 不可用时应降级到内存黑名单。"""
        service = TokenBlacklistService()
        token = "test_token_memory"
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(minutes=30)

        with patch("app.services.token_blacklist.redis_manager") as mock_manager, \
             patch("app.services.token_blacklist.decode_token") as mock_decode, \
             patch("app.services.token_blacklist.get_token_expiration") as mock_expiration:
            type(mock_manager).client = property(lambda _: (_ for _ in ()).throw(RuntimeError("Redis 未初始化")))
            mock_decode.return_value = {"sub": "1"}
            mock_expiration.return_value = expiration

            added = await service.add_token_to_blacklist(token, user_id=1)
            blacklisted = await service.is_token_blacklisted(token)

            assert added is True
            assert blacklisted is True

    @pytest.mark.asyncio
    async def test_user_revocation_falls_back_to_memory_when_redis_unavailable(self):
        """Redis 不可用时批量撤销标记也应使用内存存储。"""
        service = TokenBlacklistService()
        token_issued_at = datetime.now(timezone.utc) - timedelta(minutes=5)

        with patch("app.services.token_blacklist.redis_manager") as mock_manager:
            type(mock_manager).client = property(lambda _: (_ for _ in ()).throw(RuntimeError("Redis 未初始化")))

            revoked = await service.revoke_all_user_tokens(123)
            is_revoked = await service.is_user_tokens_revoked(123, token_issued_at)

            assert revoked is True
            assert is_revoked is True
