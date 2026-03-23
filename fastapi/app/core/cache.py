"""
缓存服务模块

提供统一的缓存接口，支持内存缓存和 Redis 缓存。
自动降级：Redis 不可用时使用内存缓存。
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from app.core.config import settings


class CacheBackend(ABC):
    """缓存后端抽象基类"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass

    @abstractmethod
    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存"""
        pass


class MemoryCache(CacheBackend):
    """
    内存缓存实现

    使用字典存储，支持 TTL 过期。
    适用于单实例部署或开发环境。
    """

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = settings.cache_ttl

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key not in self._cache:
            return None

        item = self._cache[key]

        # 检查是否过期
        if item["expires_at"] and time.time() > item["expires_at"]:
            del self._cache[key]
            return None

        return item["value"]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl if ttl > 0 else None

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }
        return True

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        value = await self.get(key)
        return value is not None

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存"""
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count

        # 简单的模式匹配（支持 * 通配符）
        import fnmatch

        keys_to_delete = [
            k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)
        ]
        for key in keys_to_delete:
            del self._cache[key]

        return len(keys_to_delete)

    def _cleanup_expired(self) -> int:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            k
            for k, v in self._cache.items()
            if v["expires_at"] and current_time > v["expires_at"]
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


class RedisCache(CacheBackend):
    """
    Redis 缓存实现

    使用 Redis 作为缓存后端，支持分布式部署。
    """

    def __init__(self):
        self._redis = None
        self._default_ttl = settings.cache_ttl
        self._prefix = "cache:"

    async def _get_redis(self):
        """获取 Redis 客户端"""
        if self._redis is None:
            from app.core.redis import redis_manager

            try:
                self._redis = redis_manager.client
            except Exception as e:
                logger.warning(f"Redis 连接失败，将使用内存缓存: {e}")
                raise
        return self._redis

    def _make_key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        try:
            redis = await self._get_redis()
            value = await redis.get(self._make_key(key))
            if value is None:
                return None

            # 尝试反序列化 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.warning(f"Redis get 失败: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        try:
            redis = await self._get_redis()
            ttl = ttl or self._default_ttl

            # 序列化值
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
        """删除缓存"""
        try:
            redis = await self._get_redis()
            await redis.delete(self._make_key(key))
            return True
        except Exception as e:
            logger.warning(f"Redis delete 失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            redis = await self._get_redis()
            return await redis.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.warning(f"Redis exists 失败: {e}")
            return False

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存"""
        try:
            redis = await self._get_redis()
            if pattern is None:
                pattern = f"{self._prefix}*"
            else:
                pattern = f"{self._prefix}{pattern}"

            # 使用 SCAN 命令安全删除
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await redis.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis clear 失败: {e}")
            return 0


class CacheService:
    """
    缓存服务

    统一的缓存接口，自动选择缓存后端。
    Redis 可用时使用 Redis，否则降级到内存缓存。
    """

    def __init__(self):
        self._backend: CacheBackend | None = None
        self._memory_cache = MemoryCache()
        self._redis_cache = RedisCache()
        self._use_redis = False

    async def init(self) -> None:
        """初始化缓存服务"""
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
        """获取缓存值"""
        return await self._backend.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        return await self._backend.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self._backend.delete(key)

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return await self._backend.exists(key)

    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存"""
        return await self._backend.clear(pattern)

    async def get_or_set(
        self, key: str, factory: callable, ttl: int | None = None
    ) -> Any:
        """
        获取缓存，不存在则通过工厂函数创建

        Args:
            key: 缓存键
            factory: 创建值的异步函数
            ttl: 过期时间（秒）

        Returns:
            缓存值
        """
        value = await self.get(key)
        if value is not None:
            return value

        # 通过工厂函数创建值
        value = await factory() if callable(factory) else factory
        await self.set(key, value, ttl)
        return value

    @property
    def is_using_redis(self) -> bool:
        """是否使用 Redis"""
        return self._use_redis


# 全局缓存服务实例
cache_service = CacheService()


# 缓存键生成器
class CacheKeys:
    """缓存键常量"""

    # 字典缓存
    DICT_BY_CODE = "dict:code:{code}"  # 根据编码获取字典项
    DICT_ALL = "dict:all"  # 所有字典

    # 权限缓存
    USER_PERMISSIONS = "user:permissions:{user_id}"  # 用户权限
    USER_MENUS = "user:menus:{user_id}"  # 用户菜单
    ROLE_PERMISSIONS = "role:permissions:{role_id}"  # 角色权限

    # 角色缓存
    ROLE_OPTIONS = "role:options"  # 角色选项
    ROLE_DETAIL = "role:detail:{role_id}"  # 角色详情

    # 部门缓存
    DEPT_TREE = "dept:tree"  # 部门树
    DEPT_DETAIL = "dept:detail:{dept_id}"  # 部门详情

    # 菜单缓存
    MENU_TREE = "menu:tree"  # 菜单树
    MENU_DETAIL = "menu:detail:{menu_id}"  # 菜单详情

    @staticmethod
    def format_key(template: str, **kwargs) -> str:
        """格式化缓存键"""
        return template.format(**kwargs)
