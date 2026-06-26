"""
Redis 缓存删除、存在性与清理测试。
"""
import warnings
from unittest.mock import AsyncMock

import pytest

from app.core.cache import RedisCache


class FailingAsyncIterator:
    """模拟 Redis scan_iter 在迭代阶段抛错。"""

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise Exception("Connection lost")


class FailingScanRedis:
    """模拟 scan_iter 返回异步迭代器的 Redis 客户端。"""

    def scan_iter(self, match):
        return FailingAsyncIterator()

    async def delete(self, *keys):
        return 0


class TestRedisCacheDeleteClear:
    """测试 Redis 缓存删除、存在性与批量清理。"""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """测试删除缓存成功。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        cache._redis = mock_redis

        result = await cache.delete("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_error(self):
        """测试删除缓存错误。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.delete("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """测试检查存在的键。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """测试检查不存在的键。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_error(self):
        """测试检查键错误。"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self):
        """测试清除所有缓存。"""
        cache = RedisCache()

        mock_redis = AsyncMock()

        async def mock_scan_iter(match):
            for key in ["cache:key1", "cache:key2"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete = AsyncMock(return_value=2)
        cache._redis = mock_redis

        count = await cache.clear()
        assert count == 2

    @pytest.mark.asyncio
    async def test_clear_with_pattern(self):
        """测试按模式清除缓存。"""
        cache = RedisCache()

        mock_redis = AsyncMock()

        async def mock_scan_iter(match):
            for key in ["cache:test_key1", "cache:test_key2"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete = AsyncMock(return_value=2)
        cache._redis = mock_redis

        count = await cache.clear("test_*")
        assert count == 2

    @pytest.mark.asyncio
    async def test_clear_error(self):
        """测试清除缓存错误。"""
        cache = RedisCache()

        cache._redis = FailingScanRedis()

        with warnings.catch_warnings():
            warnings.filterwarnings("error", message=".*was never awaited.*")
            count = await cache.clear()
        assert count == 0
