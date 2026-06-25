"""
Redis 缓存测试。
"""
import warnings
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestRedisCache:
    """测试 Redis 缓存。"""

    @pytest.mark.asyncio
    async def test_get_redis_success(self):
        """测试获取 Redis 客户端成功。"""
        cache = RedisCache()

        with patch("app.core.redis.redis_manager") as mock_manager:
            mock_client = MagicMock()
            mock_manager.client = mock_client

            redis = await cache._get_redis()
            assert redis is mock_client

    @pytest.mark.asyncio
    async def test_get_redis_failure(self):
        """测试获取 Redis 客户端失败。"""
        cache = RedisCache()

        with patch("app.core.redis.redis_manager") as mock_manager:
            # 通过属性访问异常覆盖 Redis 连接失败分支。
            type(mock_manager).client = property(lambda self: (_ for _ in ()).throw(Exception("Connection failed")))

            with pytest.raises(Exception):
                await cache._get_redis()

    def test_make_key(self):
        """测试生成带前缀的键。"""
        cache = RedisCache()
        key = cache._make_key("test_key")
        assert key == "cache:test_key"

    @pytest.mark.asyncio
    async def test_get_success(self):
        """测试获取缓存成功。"""
        cache = RedisCache()

        mock_redis = MagicMock()
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
