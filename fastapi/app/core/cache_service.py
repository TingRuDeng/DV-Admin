"""
缓存服务编排。
"""
from collections.abc import Callable
from inspect import isawaitable
from typing import Any

from loguru import logger

from app.core.cache_backend import CacheBackend
from app.core.cache_memory import MemoryCache
from app.core.cache_redis import RedisCache


class CacheService:
    """
    缓存服务。

    统一缓存接口，Redis 可用时使用 Redis，否则使用内存缓存。
    """

    def __init__(self):
        self._memory_cache = MemoryCache()
        self._redis_cache = RedisCache()
        self._backend: CacheBackend = self._memory_cache
        self._use_redis = False

    async def init(self) -> None:
        """初始化缓存服务。"""
        try:
            from app.core.redis import redis_manager

            if await redis_manager.is_connected():
                self._backend = self._redis_cache
                self._use_redis = True
                logger.info("缓存服务使用 Redis 后端")
            else:
                self._backend = self._memory_cache
                self._use_redis = False
                logger.info("Redis 未连接，缓存服务使用内存后端")
        except Exception as e:
            self._backend = self._memory_cache
            self._use_redis = False
            logger.warning(f"Redis 初始化失败，使用内存缓存: {e}")

    async def get(self, key: str) -> Any | None:
        """获取缓存值。"""
        return await self._backend.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值。"""
        return await self._backend.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """删除缓存。"""
        return await self._backend.delete(key)

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        return await self._backend.exists(key)

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存。"""
        return await self._backend.clear(pattern)

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any] | Any,
        ttl: int | None = None,
    ) -> Any:
        """获取缓存，不存在则通过工厂函数或直接值创建。"""
        value = await self.get(key)
        if value is not None:
            return value

        produced = factory() if callable(factory) else factory
        value = await produced if isawaitable(produced) else produced
        await self.set(key, value, ttl)
        return value

    @property
    def is_using_redis(self) -> bool:
        """是否使用 Redis。"""
        return self._use_redis


cache_service = CacheService()
