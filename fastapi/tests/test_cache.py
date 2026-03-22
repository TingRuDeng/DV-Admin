# -*- coding: utf-8 -*-
"""
缓存服务模块测试
测试 app/core/cache.py 的功能
"""
import pytest
import pytest_asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.cache import (
    MemoryCache,
    RedisCache,
    CacheService,
    CacheKeys,
    cache_service,
)


class TestMemoryCache:
    """测试内存缓存"""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """测试设置和获取缓存"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """测试获取不存在的键"""
        cache = MemoryCache()
        value = await cache.get("nonexistent_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self):
        """测试设置带过期时间的缓存"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=1)
        value = await cache.get("test_key")
        assert value == "test_value"

        # 等待过期
        time.sleep(1.1)
        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_zero_ttl(self):
        """测试设置永不过期的缓存"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=0)
        value = await cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_delete_existing_key(self):
        """测试删除存在的键"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        result = await cache.delete("test_key")
        assert result is True
        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self):
        """测试删除不存在的键"""
        cache = MemoryCache()
        result = await cache.delete("nonexistent_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """测试检查存在的键"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        result = await cache.exists("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """测试检查不存在的键"""
        cache = MemoryCache()
        result = await cache.exists("nonexistent_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_expired_key(self):
        """测试检查已过期的键"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=1)
        time.sleep(1.1)
        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self):
        """测试清除所有缓存"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        count = await cache.clear()
        assert count == 3

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_clear_with_pattern(self):
        """测试按模式清除缓存"""
        cache = MemoryCache()
        await cache.set("test_key1", "value1")
        await cache.set("test_key2", "value2")
        await cache.set("other_key", "value3")

        count = await cache.clear("test_*")
        assert count == 2

        assert await cache.get("test_key1") is None
        assert await cache.get("test_key2") is None
        assert await cache.get("other_key") == "value3"

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """测试清理过期缓存"""
        cache = MemoryCache()
        await cache.set("key1", "value1", ttl=1)
        await cache.set("key2", "value2", ttl=1)
        await cache.set("key3", "value3", ttl=100)

        time.sleep(1.1)

        count = cache._cleanup_expired()
        assert count == 2

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") == "value3"


class TestRedisCache:
    """测试 Redis 缓存"""

    @pytest.mark.asyncio
    async def test_get_redis_success(self):
        """测试获取 Redis 客户端成功"""
        cache = RedisCache()

        with patch('app.core.redis.redis_manager') as mock_manager:
            mock_client = MagicMock()
            mock_manager.client = mock_client

            redis = await cache._get_redis()
            assert redis is mock_client

    @pytest.mark.asyncio
    async def test_get_redis_failure(self):
        """测试获取 Redis 客户端失败"""
        cache = RedisCache()

        with patch('app.core.redis.redis_manager') as mock_manager:
            # 模拟 client 属性访问时抛出异常
            type(mock_manager).client = property(lambda self: (_ for _ in ()).throw(Exception("Connection failed")))

            with pytest.raises(Exception):
                await cache._get_redis()

    def test_make_key(self):
        """测试生成带前缀的键"""
        cache = RedisCache()
        key = cache._make_key("test_key")
        assert key == "cache:test_key"

    @pytest.mark.asyncio
    async def test_get_success(self):
        """测试获取缓存成功"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "value"}')
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """测试获取不存在的缓存"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_get_string_value(self):
        """测试获取字符串值"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="plain_string")
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value == "plain_string"

    @pytest.mark.asyncio
    async def test_get_error(self):
        """测试获取缓存错误"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_dict_value(self):
        """测试设置字典值"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        cache._redis = mock_redis

        result = await cache.set("test_key", {"key": "value"}, ttl=100)
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_string_value(self):
        """测试设置字符串值"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        cache._redis = mock_redis

        result = await cache.set("test_key", "test_value", ttl=100)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_with_zero_ttl(self):
        """测试设置永不过期的缓存"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        cache._redis = mock_redis

        # 设置一个很大的 TTL 来模拟永不过期
        result = await cache.set("test_key", "test_value", ttl=-1)
        # 由于 TTL 为负数，会使用默认 TTL
        assert result is True

    @pytest.mark.asyncio
    async def test_set_error(self):
        """测试设置缓存错误"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.set("test_key", "test_value", ttl=100)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """测试删除缓存成功"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        cache._redis = mock_redis

        result = await cache.delete("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_error(self):
        """测试删除缓存错误"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.delete("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """测试检查存在的键"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """测试检查不存在的键"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_error(self):
        """测试检查键错误"""
        cache = RedisCache()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=Exception("Connection lost"))
        cache._redis = mock_redis

        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self):
        """测试清除所有缓存"""
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
        """测试按模式清除缓存"""
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
        """测试清除缓存错误"""
        cache = RedisCache()

        mock_redis = AsyncMock()

        async def mock_scan_iter(match):
            raise Exception("Connection lost")

        mock_redis.scan_iter = mock_scan_iter
        cache._redis = mock_redis

        count = await cache.clear()
        assert count == 0


class TestCacheService:
    """测试缓存服务"""

    @pytest.mark.asyncio
    async def test_init_with_redis(self):
        """测试使用 Redis 初始化"""
        service = CacheService()

        with patch('app.core.redis.redis_manager') as mock_manager:
            mock_manager.is_connected = AsyncMock(return_value=True)

            await service.init()

            assert service._use_redis is True

    @pytest.mark.asyncio
    async def test_init_without_redis(self):
        """测试不使用 Redis 初始化"""
        service = CacheService()

        with patch('app.core.redis.redis_manager') as mock_manager:
            mock_manager.is_connected = AsyncMock(return_value=False)

            await service.init()

            assert service._use_redis is False

    @pytest.mark.asyncio
    async def test_init_with_exception(self):
        """测试初始化时发生异常"""
        service = CacheService()

        with patch('app.core.redis.redis_manager') as mock_manager:
            mock_manager.is_connected = AsyncMock(side_effect=Exception("Connection failed"))

            await service.init()

            assert service._use_redis is False

    @pytest.mark.asyncio
    async def test_get_or_set_existing(self):
        """测试获取或设置已存在的缓存"""
        service = CacheService()
        service._backend = MemoryCache()
        await service.set("test_key", "existing_value")

        value = await service.get_or_set("test_key", lambda: "new_value")
        assert value == "existing_value"

    @pytest.mark.asyncio
    async def test_get_or_set_new(self):
        """测试获取或设置新缓存"""
        service = CacheService()
        service._backend = MemoryCache()

        async def factory():
            return "new_value"

        value = await service.get_or_set("test_key", factory)
        assert value == "new_value"

        # 验证已缓存
        cached_value = await service.get("test_key")
        assert cached_value == "new_value"

    @pytest.mark.asyncio
    async def test_get_or_set_with_non_callable(self):
        """测试获取或设置非可调用值"""
        service = CacheService()
        service._backend = MemoryCache()

        value = await service.get_or_set("test_key", "direct_value")
        assert value == "direct_value"

    def test_is_using_redis_true(self):
        """测试检查是否使用 Redis（是）"""
        service = CacheService()
        service._use_redis = True
        assert service.is_using_redis is True

    def test_is_using_redis_false(self):
        """测试检查是否使用 Redis（否）"""
        service = CacheService()
        service._use_redis = False
        assert service.is_using_redis is False


class TestCacheKeys:
    """测试缓存键常量"""

    def test_format_key(self):
        """测试格式化缓存键"""
        key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code="test_code")
        assert key == "dict:code:test_code"

    def test_format_key_user_permissions(self):
        """测试格式化用户权限缓存键"""
        key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=123)
        assert key == "user:permissions:123"

    def test_format_key_role_detail(self):
        """测试格式化角色详情缓存键"""
        key = CacheKeys.format_key(CacheKeys.ROLE_DETAIL, role_id=456)
        assert key == "role:detail:456"

    def test_format_key_dept_detail(self):
        """测试格式化部门详情缓存键"""
        key = CacheKeys.format_key(CacheKeys.DEPT_DETAIL, dept_id=789)
        assert key == "dept:detail:789"

    def test_format_key_menu_detail(self):
        """测试格式化菜单详情缓存键"""
        key = CacheKeys.format_key(CacheKeys.MENU_DETAIL, menu_id=101)
        assert key == "menu:detail:101"
