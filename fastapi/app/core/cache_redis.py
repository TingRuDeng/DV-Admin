"""
Redis 缓存后端。
"""
import json
from typing import Any

from loguru import logger

from app.core.cache_backend import CacheBackend
from app.core.config import settings


class RedisCache(CacheBackend):
    """
    Redis 缓存实现。

    使用 Redis 作为缓存后端，支持分布式部署。
    """

    def __init__(self):
        self._redis = None
        self._default_ttl = settings.cache_ttl
        self._prefix = "cache:"

    async def _get_redis(self):
        """获取 Redis 客户端。"""
        if self._redis is None:
            from app.core.redis import redis_manager

            try:
                self._redis = redis_manager.client
            except Exception as e:
                logger.warning(f"Redis 连接失败，将使用内存缓存: {e}")
                raise
        return self._redis

    def _make_key(self, key: str) -> str:
        """生成带前缀的键。"""
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值。"""
        try:
            redis = await self._get_redis()
            value = await redis.get(self._make_key(key))
            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.warning(f"Redis get 失败: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值。"""
        try:
            redis = await self._get_redis()
            ttl = ttl or self._default_ttl

            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)

            if ttl > 0:
                await redis.setex(self._make_key(key), ttl, value)
            else:
                await redis.set(self._make_key(key), value)

            return True
        except Exception as e:
            logger.warning(f"Redis set 失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存。"""
        try:
            redis = await self._get_redis()
            await redis.delete(self._make_key(key))
            return True
        except Exception as e:
            logger.warning(f"Redis delete 失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        try:
            redis = await self._get_redis()
            return await redis.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.warning(f"Redis exists 失败: {e}")
            return False

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存。"""
        try:
            redis = await self._get_redis()
            match_pattern = f"{self._prefix}{pattern}" if pattern else f"{self._prefix}*"

            keys = []
            async for key in redis.scan_iter(match=match_pattern):
                keys.append(key)

            if keys:
                await redis.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis clear 失败: {e}")
            return 0
