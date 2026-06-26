"""
Redis 缓存连接与键生成测试。
"""
from unittest.mock import MagicMock, patch

import pytest

from app.core.cache import RedisCache


class TestRedisCacheConnection:
    """测试 Redis 缓存连接和键前缀。"""

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
