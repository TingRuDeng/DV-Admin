"""
单 Token 黑名单测试。
"""
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import RedisError

from app.services.token_blacklist import TokenBlacklistService

pytest_plugins = ["token_blacklist_fixtures"]


class TestTokenBlacklistTokens:
    """测试单个 Token 的加入和查询。"""

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_success(self):
        """测试添加 Token 到黑名单成功。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        service._redis = mock_redis

        now = datetime.now(timezone.utc)
        expiration = now + timedelta(hours=1)

        with patch("app.services.token_blacklist.decode_token") as mock_decode, \
             patch("app.services.token_blacklist.get_token_expiration") as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist(
                "test_token",
                user_id=1,
                reason="logout",
            )

            assert result is True
            mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_decode_failed(self):
        """测试添加 Token 到黑名单时解码失败。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        with patch("app.services.token_blacklist.decode_token") as mock_decode:
            mock_decode.return_value = None

            result = await service.add_token_to_blacklist("invalid_token")

            assert result is False
            mock_redis.setex.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_no_expiration(self):
        """测试添加无过期时间的 Token。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        with patch("app.services.token_blacklist.decode_token") as mock_decode, \
             patch("app.services.token_blacklist.get_token_expiration") as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = None

            result = await service.add_token_to_blacklist("test_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_expired(self):
        """测试添加已过期的 Token 到黑名单。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        now = datetime.now(timezone.utc)
        expiration = now - timedelta(hours=1)

        with patch("app.services.token_blacklist.decode_token") as mock_decode, \
             patch("app.services.token_blacklist.get_token_expiration") as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist("expired_token")

            assert result is True
            mock_redis.setex.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_redis_error(self):
        """测试添加 Token 到黑名单时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        now = datetime.now(timezone.utc)
        expiration = now + timedelta(hours=1)

        with patch("app.services.token_blacklist.decode_token") as mock_decode, \
             patch("app.services.token_blacklist.get_token_expiration") as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist("test_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_consume_refresh_token_uses_atomic_redis_write(self):
        """Redis 通过 SET NX 保证同一刷新令牌只消费一次。"""
        service = TokenBlacklistService()
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(side_effect=[True, None])
        service._redis = mock_redis
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)

        with patch(
            "app.services.token_blacklist.decode_token",
            return_value={"sub": "1", "type": "refresh"},
        ), \
             patch(
                 "app.services.token_blacklist.get_token_expiration",
                 return_value=expiration,
             ):
            first = await service.consume_refresh_token("refresh_token", user_id=1)
            replay = await service.consume_refresh_token("refresh_token", user_id=1)

        assert first is True
        assert replay is False
        assert mock_redis.set.call_count == 2
        assert mock_redis.set.call_args.kwargs["nx"] is True

    @pytest.mark.asyncio
    async def test_consume_refresh_token_fails_closed_on_redis_error(self):
        """刷新轮换存储异常时不得继续签发令牌。"""
        service = TokenBlacklistService()
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)

        with patch(
            "app.services.token_blacklist.decode_token",
            return_value={"sub": "1", "type": "refresh"},
        ), \
             patch(
                 "app.services.token_blacklist.get_token_expiration",
                 return_value=expiration,
             ):
            result = await service.consume_refresh_token("refresh_token", user_id=1)

        assert result is False

    @pytest.mark.asyncio
    async def test_consume_refresh_token_is_atomic_in_memory_fallback(self):
        """开发环境内存降级在并发任务中也只能成功一次。"""
        service = TokenBlacklistService()
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)

        with patch.object(service, "_get_redis_or_none", return_value=None), \
             patch("app.services.token_blacklist.settings") as mock_settings, \
             patch(
                 "app.services.token_blacklist.decode_token",
                 return_value={"sub": "1", "type": "refresh"},
             ), \
             patch(
                 "app.services.token_blacklist.get_token_expiration",
                 return_value=expiration,
             ):
            mock_settings.is_production = False
            results = await asyncio.gather(
                service.consume_refresh_token("refresh_token", user_id=1),
                service.consume_refresh_token("refresh_token", user_id=1),
            )

        assert sorted(results) == [False, True]

    @pytest.mark.asyncio
    async def test_consume_refresh_token_requires_redis_in_production(self):
        """生产环境不能用进程内存冒充跨实例单次消费。"""
        service = TokenBlacklistService()
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)

        with patch.object(service, "_get_redis_or_none", return_value=None), \
             patch("app.services.token_blacklist.settings") as mock_settings, \
             patch(
                 "app.services.token_blacklist.decode_token",
                 return_value={"sub": "1", "type": "refresh"},
             ), \
             patch(
                 "app.services.token_blacklist.get_token_expiration",
                 return_value=expiration,
             ):
            mock_settings.is_production = True
            result = await service.consume_refresh_token("refresh_token", user_id=1)

        assert result is False
        assert service._memory_store.blacklist == {}

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_true(self):
        """测试检查 Token 已在黑名单中。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.is_token_blacklisted("blacklisted_token")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_false(self):
        """测试检查 Token 不在黑名单中。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        service._redis = mock_redis

        result = await service.is_token_blacklisted("valid_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_redis_error(self):
        """测试检查 Token 黑名单时 Redis 错误。"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.is_token_blacklisted("test_token")

        assert result is False
