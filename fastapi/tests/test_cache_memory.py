"""
内存缓存测试。
"""
import time

import pytest

from app.core.cache import MemoryCache


class TestMemoryCache:
    """测试内存缓存。"""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """测试设置和获取缓存。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """测试获取不存在的键。"""
        cache = MemoryCache()
        value = await cache.get("nonexistent_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self):
        """测试设置带过期时间的缓存。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=1)
        value = await cache.get("test_key")
        assert value == "test_value"

        # 等待真实过期窗口，验证 TTL 清理路径。
        time.sleep(1.1)
        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_zero_ttl(self):
        """测试设置永不过期的缓存。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=0)
        value = await cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_delete_existing_key(self):
        """测试删除存在的键。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        result = await cache.delete("test_key")
        assert result is True
        value = await cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self):
        """测试删除不存在的键。"""
        cache = MemoryCache()
        result = await cache.delete("nonexistent_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """测试检查存在的键。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value")
        result = await cache.exists("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """测试检查不存在的键。"""
        cache = MemoryCache()
        result = await cache.exists("nonexistent_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_expired_key(self):
        """测试检查已过期的键。"""
        cache = MemoryCache()
        await cache.set("test_key", "test_value", ttl=1)
        time.sleep(1.1)
        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self):
        """测试清除所有缓存。"""
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
        """测试按模式清除缓存。"""
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
        """测试清理过期缓存。"""
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
