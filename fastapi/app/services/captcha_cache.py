"""
验证码缓存实现。

本模块只负责验证码缓存读写，不包含验证码生成或登录校验编排。
"""

import time
from typing import Any


class CaptchaCache:
    """
    验证码缓存基类。

    定义验证码缓存的异步接口，便于服务层注入不同缓存实现。
    """

    async def get(self, key: str) -> str | None:
        """获取验证码。"""
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int) -> None:
        """设置验证码。"""
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        """删除验证码。"""
        raise NotImplementedError


class MemoryCaptchaCache(CaptchaCache):
    """
    内存验证码缓存。

    使用内存字典存储验证码，适用于单机开发环境。
    """

    def __init__(self) -> None:
        self._cache: dict[str, tuple[str, float]] = {}
        self._cleanup_interval = 100
        self._access_count = 0

    async def get(self, key: str) -> str | None:
        """获取未过期的验证码，并按访问次数触发过期清理。"""
        self._access_count += 1
        if self._access_count >= self._cleanup_interval:
            self._cleanup_expired()
            self._access_count = 0

        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]
        if time.time() > expire_time:
            del self._cache[key]
            return None

        return value

    async def set(self, key: str, value: str, ttl: int) -> None:
        """按 TTL 写入验证码。"""
        expire_time = time.time() + ttl
        self._cache[key] = (value, expire_time)

    async def delete(self, key: str) -> None:
        """删除验证码，缺失时保持幂等。"""
        self._cache.pop(key, None)

    def _cleanup_expired(self) -> None:
        """清理已过期的验证码，避免开发环境长期运行时累积无效数据。"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self._cache.items()
            if current_time > expire_time
        ]
        for key in expired_keys:
            del self._cache[key]


class RedisCaptchaCache(CaptchaCache):
    """
    Redis 验证码缓存。

    使用 Redis 存储验证码，适用于分布式生产环境。
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis: Any = None

    async def _get_redis(self) -> Any:
        """延迟创建 Redis 连接，避免未使用验证码时提前连接外部服务。"""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except ImportError as exc:
                raise RuntimeError(
                    "Redis support requires the 'redis' package. "
                    "Install it with: pip install redis"
                ) from exc
        return self._redis

    async def get(self, key: str) -> str | None:
        """从 Redis 获取验证码。"""
        redis = await self._get_redis()
        return await redis.get(f"captcha:{key}")

    async def set(self, key: str, value: str, ttl: int) -> None:
        """按 TTL 将验证码写入 Redis。"""
        redis = await self._get_redis()
        await redis.setex(f"captcha:{key}", ttl, value)

    async def delete(self, key: str) -> None:
        """从 Redis 删除验证码。"""
        redis = await self._get_redis()
        await redis.delete(f"captcha:{key}")
