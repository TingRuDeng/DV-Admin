"""
缓存服务兼容导出入口。

实际实现已按职责拆分到同目录下的专用模块；保留本入口是为了兼容
既有 `from app.core.cache import ...` 调用点。
"""
from app.core.cache_backend import CacheBackend
from app.core.cache_keys import CacheKeys
from app.core.cache_memory import MemoryCache
from app.core.cache_redis import RedisCache
from app.core.cache_service import CacheService, cache_service

__all__ = [
    "CacheBackend",
    "CacheKeys",
    "CacheService",
    "MemoryCache",
    "RedisCache",
    "cache_service",
]
