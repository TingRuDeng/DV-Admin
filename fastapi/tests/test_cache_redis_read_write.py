"""
Redis 缓存读写测试。
"""
from unittest.mock import AsyncMock

import pytest

from app.core.cache import RedisCache


class TestRedisCacheReadWrite:
    """测试 Redis 缓存读取和写入。"""

    @pytest.mark.asyncio
    async def test_get_success(self):
        """测试获取缓存成功。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "value"}')
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """测试获取不存在的缓存。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_get_string_value(self):
        """测试获取字符串值。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="plain_string")
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value == "plain_string"

    @pytest.mark.asyncio
    async def test_get_error(self):
        """测试获取缓存错误。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_dict_value(self):
        """测试设置字典值。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        cache._redis = mock_redis

        result = await cache.set("test_key", {"key": "value"}, ttl=100)
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_string_value(self):
        """测试设置字符串值。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        cache._redis = mock_redis

        result = await cache.set("test_key", "test_value", ttl=100)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_with_zero_ttl(self):
        """测试设置永不过期的缓存。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        cache._redis = mock_redis

        result = await cache.set("test_key", "test_value", ttl=-1)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_error(self):
        """测试设置缓存错误。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.set("test_key", "test_value", ttl=100)
        assert result is False
