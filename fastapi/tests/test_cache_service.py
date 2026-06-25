"""
缓存服务测试。
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.core.cache import CacheService, MemoryCache


class TestCacheService:
    """测试缓存服务。"""

    @pytest.mark.asyncio
    async def test_init_with_redis(self):
        """测试使用 Redis 初始化。"""
        service = CacheService()

        with patch("app.core.redis.redis_manager") as mock_manager:
            mock_manager.is_connected = AsyncMock(return_value=True)

            await service.init()

            assert service._use_redis is True

    @pytest.mark.asyncio
    async def test_init_without_redis(self):
        """测试不使用 Redis 初始化。"""
        service = CacheService()

        with patch("app.core.redis.redis_manager") as mock_manager:
            mock_manager.is_connected = AsyncMock(return_value=False)

            await service.init()

            assert service._use_redis is False

    @pytest.mark.asyncio
    async def test_init_with_exception(self):
        """测试初始化时发生异常。"""
        service = CacheService()

        with patch("app.core.redis.redis_manager") as mock_manager:
            mock_manager.is_connected = AsyncMock(side_effect=Exception("Connection failed"))

            await service.init()

            assert service._use_redis is False

    @pytest.mark.asyncio
    async def test_get_or_set_existing(self):
        """测试获取或设置已存在的缓存。"""
        service = CacheService()
        service._backend = MemoryCache()
        await service.set("test_key", "existing_value")

        value = await service.get_or_set("test_key", lambda: "new_value")
        assert value == "existing_value"

    @pytest.mark.asyncio
    async def test_get_or_set_new(self):
        """测试获取或设置新缓存。"""
        service = CacheService()
        service._backend = MemoryCache()

        async def factory():
            return "new_value"

        value = await service.get_or_set("test_key", factory)
        assert value == "new_value"

        # 验证工厂结果已写入当前缓存后端。
        cached_value = await service.get("test_key")
        assert cached_value == "new_value"

    @pytest.mark.asyncio
    async def test_get_or_set_with_non_callable(self):
        """测试获取或设置非可调用值。"""
        service = CacheService()
        service._backend = MemoryCache()

        value = await service.get_or_set("test_key", "direct_value")
        assert value == "direct_value"

    def test_is_using_redis_true(self):
        """测试检查是否使用 Redis。"""
        service = CacheService()
        service._use_redis = True
        assert service.is_using_redis is True

    def test_is_using_redis_false(self):
        """测试检查是否不使用 Redis。"""
        service = CacheService()
        service._use_redis = False
        assert service.is_using_redis is False
