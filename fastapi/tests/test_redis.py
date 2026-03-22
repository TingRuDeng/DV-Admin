# -*- coding: utf-8 -*-
"""
Redis 连接管理模块测试
测试 app/core/redis.py 的功能
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.redis import RedisManager, redis_manager, get_redis


class TestRedisManager:
    """测试 Redis 连接管理器"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 重置实例
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager1 = RedisManager()
        manager2 = RedisManager()

        assert manager1 is manager2

    def test_new_creates_instance(self):
        """测试 __new__ 方法创建实例"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        assert isinstance(manager, RedisManager)

    @pytest.mark.asyncio
    async def test_init_success(self):
        """测试初始化成功"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        with patch('app.core.redis.ConnectionPool.from_url') as mock_pool_from_url, \
             patch('app.core.redis.Redis') as mock_redis_class:
            # 设置 mock
            mock_pool = MagicMock()
            mock_pool_from_url.return_value = mock_pool

            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_redis_class.return_value = mock_client

            await manager.init()

            assert manager._pool is not None
            assert manager._client is not None
            mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_already_initialized(self):
        """测试重复初始化"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        manager._pool = MagicMock()
        manager._client = MagicMock()

        # 再次初始化应该直接返回
        await manager.init()

        # pool 应该还是原来的对象
        assert manager._pool is not None

    @pytest.mark.asyncio
    async def test_init_redis_error(self):
        """测试初始化 Redis 错误"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        with patch('app.core.redis.ConnectionPool.from_url') as mock_pool_from_url:
            from redis.exceptions import RedisError
            mock_pool_from_url.side_effect = RedisError("Connection failed")

            with pytest.raises(RedisError):
                await manager.init()

            assert manager._pool is None
            assert manager._client is None

    @pytest.mark.asyncio
    async def test_close_with_client_and_pool(self):
        """测试关闭连接池（有客户端和连接池）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        manager._client = mock_client

        mock_pool = AsyncMock()
        mock_pool.disconnect = AsyncMock()
        manager._pool = mock_pool

        await manager.close()

        mock_client.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()
        assert manager._client is None
        assert manager._pool is None

    @pytest.mark.asyncio
    async def test_close_without_client(self):
        """测试关闭连接池（无客户端）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        manager._client = None
        manager._pool = None

        # 应该不抛出异常
        await manager.close()

    @pytest.mark.asyncio
    async def test_close_with_client_only(self):
        """测试关闭连接池（只有客户端）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        manager._client = mock_client
        manager._pool = None

        await manager.close()

        mock_client.close.assert_called_once()
        assert manager._client is None

    def test_client_property_success(self):
        """测试获取客户端属性成功"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        mock_client = MagicMock()
        manager._client = mock_client

        client = manager.client
        assert client is mock_client

    def test_client_property_not_initialized(self):
        """测试获取客户端属性（未初始化）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        manager._client = None

        with pytest.raises(RuntimeError) as exc_info:
            _ = manager.client

        assert "Redis 未初始化" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_is_connected_true(self):
        """测试检查连接状态（已连接）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        manager._client = mock_client

        result = await manager.is_connected()
        assert result is True

    @pytest.mark.asyncio
    async def test_is_connected_false_no_client(self):
        """测试检查连接状态（无客户端）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()
        manager._client = None

        result = await manager.is_connected()
        assert result is False

    @pytest.mark.asyncio
    async def test_is_connected_false_ping_error(self):
        """测试检查连接状态（ping 错误）"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        manager = RedisManager()

        mock_client = AsyncMock()
        from redis.exceptions import RedisError
        mock_client.ping = AsyncMock(side_effect=RedisError("Connection lost"))
        manager._client = mock_client

        result = await manager.is_connected()
        assert result is False


class TestGetRedis:
    """测试 get_redis 依赖函数"""

    @pytest.mark.asyncio
    async def test_get_redis(self):
        """测试获取 Redis 客户端"""
        RedisManager._instance = None
        RedisManager._pool = None
        RedisManager._client = None

        # 设置 mock
        mock_client = MagicMock()
        redis_manager._client = mock_client

        client = await get_redis()
        assert client is mock_client

        # 清理
        redis_manager._client = None
