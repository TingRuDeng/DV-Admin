"""
用户 Token 批量撤销测试。
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError

from app.services.token_blacklist import TokenBlacklistService

pytest_plugins = ["token_blacklist_fixtures"]


class TestTokenBlacklistUserRevocation:
    """测试用户级 Token 批量撤销。"""

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_success(self):
        """测试撤销用户所有 Token 成功。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        service._redis = mock_redis

        result = await service.revoke_all_user_tokens(123, "force_logout")

        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_redis_error(self):
        """测试撤销用户所有 Token 时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.revoke_all_user_tokens(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_true(self):
        """测试用户 Token 已被批量撤销。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        now = datetime.now(timezone.utc)
        revoked_time = now - timedelta(hours=1)
        mock_redis.get = AsyncMock(return_value=revoked_time.isoformat())
        service._redis = mock_redis

        token_issued_at = now - timedelta(hours=2)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_false_not_revoked(self):
        """测试用户 Token 未被批量撤销。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        service._redis = mock_redis

        token_issued_at = datetime.now(timezone.utc) - timedelta(hours=1)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_false_after_revoked(self):
        """测试签发时间晚于撤销时间的 Token 未被撤销。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        now = datetime.now(timezone.utc)
        revoked_time = now - timedelta(hours=2)
        mock_redis.get = AsyncMock(return_value=revoked_time.isoformat())
        service._redis = mock_redis

        token_issued_at = now - timedelta(hours=1)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_redis_error(self):
        """测试检查用户 Token 撤销状态时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        token_issued_at = datetime.now(timezone.utc)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False
