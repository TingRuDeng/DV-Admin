"""
内存缓存后端。
"""
import fnmatch
import time
from typing import Any

from app.core.cache_backend import CacheBackend
from app.core.config import settings


class MemoryCache(CacheBackend):
    """
    内存缓存实现。

    使用字典存储，支持 TTL 过期。适用于单实例部署或开发环境。
    """

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = settings.cache_ttl

    async def get(self, key: str) -> Any | None:
        """获取缓存值。"""
        if key not in self._cache:
            return None

        item = self._cache[key]
        if item["expires_at"] and time.time() > item["expires_at"]:
            del self._cache[key]
            return None

        return item["value"]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值。"""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl if ttl > 0 else None

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }
        return True

    async def delete(self, key: str) -> bool:
        """删除缓存。"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        value = await self.get(key)
        return value is not None

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存。"""
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count

        keys_to_delete = [
            key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)
        ]
        for key in keys_to_delete:
            del self._cache[key]

        return len(keys_to_delete)

    def _cleanup_expired(self) -> int:
        """清理过期缓存。"""
        current_time = time.time()
        expired_keys = [
            key
            for key, value in self._cache.items()
            if value["expires_at"] and current_time > value["expires_at"]
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)
