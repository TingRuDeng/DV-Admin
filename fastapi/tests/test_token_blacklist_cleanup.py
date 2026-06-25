"""
Token 黑名单删除清理测试。
"""
from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError

from app.services.token_blacklist import TokenBlacklistService

pytest_plugins = ["token_blacklist_fixtures"]


class TestTokenBlacklistCleanup:
    """测试黑名单移除和用户撤销标记清理。"""

    @pytest.mark.asyncio
    async def test_remove_token_from_blacklist_success(self):
        """测试从黑名单移除 Token 成功。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.remove_token_from_blacklist("test_token")

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_token_from_blacklist_redis_error(self):
        """测试从黑名单移除 Token 时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.remove_token_from_blacklist("test_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_user_revocation_success(self):
        """测试清除用户 Token 撤销标记成功。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.clear_user_revocation(123)

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_user_revocation_redis_error(self):
        """测试清除用户 Token 撤销标记时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.clear_user_revocation(123)

        assert result is False
