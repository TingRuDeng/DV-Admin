"""
验证码服务模块

提供验证码生成、存储和验证功能。
支持内存缓存和 Redis 缓存两种方式。
"""

import random
import string
import uuid

from app.core.config import settings


class CaptchaCache:
    """
    验证码缓存基类

    定义验证码缓存的接口。
    """

    async def get(self, key: str) -> str | None:
        """获取验证码"""
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int) -> None:
        """设置验证码"""
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        """删除验证码"""
        raise NotImplementedError


class MemoryCaptchaCache(CaptchaCache):
    """
    内存验证码缓存

    使用内存字典存储验证码，适用于单机开发环境。
    注意：不支持分布式环境，重启后数据丢失。
    """

    def __init__(self):
        self._cache: dict[str, tuple[str, float]] = {}
        self._cleanup_interval = 100
        self._access_count = 0

    async def get(self, key: str) -> str | None:
        """获取验证码"""
        import time

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
        """设置验证码"""
        import time

        expire_time = time.time() + ttl
        self._cache[key] = (value, expire_time)

    async def delete(self, key: str) -> None:
        """删除验证码"""
        self._cache.pop(key, None)

    def _cleanup_expired(self) -> None:
        """清理过期的验证码"""
        import time

        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self._cache.items()
            if current_time > expire_time
        ]
        for key in expired_keys:
            del self._cache[key]


class RedisCaptchaCache(CaptchaCache):
    """
    Redis 验证码缓存

    使用 Redis 存储验证码，适用于分布式生产环境。
    """

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis = None

    async def _get_redis(self):
        """获取 Redis 连接"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except ImportError:
                raise RuntimeError(
                    "Redis support requires the 'redis' package. "
                    "Install it with: pip install redis"
                )
        return self._redis

    async def get(self, key: str) -> str | None:
        """获取验证码"""
        redis = await self._get_redis()
        return await redis.get(f"captcha:{key}")

    async def set(self, key: str, value: str, ttl: int) -> None:
        """设置验证码"""
        redis = await self._get_redis()
        await redis.setex(f"captcha:{key}", ttl, value)

    async def delete(self, key: str) -> None:
        """删除验证码"""
        redis = await self._get_redis()
        await redis.delete(f"captcha:{key}")


class CaptchaService:
    """
    验证码服务

    提供验证码生成、存储和验证功能。
    """

    def __init__(self, cache: CaptchaCache | None = None):
        """
        初始化验证码服务

        Args:
            cache: 验证码缓存实例，默认使用内存缓存
        """
        self._cache = cache or MemoryCaptchaCache()
        self._ttl = settings.cache_ttl  # 默认 5 分钟

    def generate_code(self, length: int = 4) -> str:
        """
        生成随机验证码

        Args:
            length: 验证码长度，默认 4 位

        Returns:
            随机验证码字符串
        """
        return ''.join(random.choices(string.digits, k=length))

    def generate_key(self) -> str:
        """
        生成验证码 key

        Returns:
            唯一的验证码 key
        """
        return str(uuid.uuid4())

    async def create(self, length: int = 4) -> tuple[str, str]:
        """
        创建验证码

        Args:
            length: 验证码长度，默认 4 位

        Returns:
            (captcha_key, captcha_code) 元组
        """
        captcha_key = self.generate_key()
        captcha_code = self.generate_code(length)

        # 存储到缓存
        await self._cache.set(captcha_key, captcha_code, self._ttl)

        return captcha_key, captcha_code

    async def verify(self, captcha_key: str, captcha_code: str, delete: bool = True) -> bool:
        """
        验证验证码

        Args:
            captcha_key: 验证码 key
            captcha_code: 用户输入的验证码
            delete: 验证后是否删除验证码，默认删除

        Returns:
            验证是否成功
        """
        if not captcha_key or not captcha_code:
            return False

        # 从缓存获取验证码
        stored_code = await self._cache.get(captcha_key)

        if not stored_code:
            return False

        # 验证码不区分大小写
        is_valid = stored_code.lower() == captcha_code.lower()

        # 验证后删除验证码（一次性使用）
        if delete:
            await self._cache.delete(captcha_key)

        return is_valid


# 全局验证码服务实例
_captcha_service: CaptchaService | None = None


def get_captcha_service() -> CaptchaService:
    """
    获取验证码服务实例（单例模式）

    Returns:
        验证码服务实例
    """
    global _captcha_service

    if _captcha_service is None:
        # 根据配置选择缓存方式
        # 开发环境使用内存缓存，生产环境建议使用 Redis
        if settings.is_production and settings.redis_url:
            try:
                cache = RedisCaptchaCache(settings.redis_url)
                _captcha_service = CaptchaService(cache)
            except Exception:
                # Redis 连接失败，降级到内存缓存
                _captcha_service = CaptchaService()
        else:
            _captcha_service = CaptchaService()

    return _captcha_service


# 便捷函数
async def create_captcha(length: int = 4) -> tuple[str, str]:
    """
    创建验证码

    Args:
        length: 验证码长度

    Returns:
        (captcha_key, captcha_code) 元组
    """
    return await get_captcha_service().create(length)


async def verify_captcha(captcha_key: str, captcha_code: str, delete: bool = True) -> bool:
    """
    验证验证码

    Args:
        captcha_key: 验证码 key
        captcha_code: 用户输入的验证码
        delete: 验证后是否删除验证码

    Returns:
        验证是否成功
    """
    return await get_captcha_service().verify(captcha_key, captcha_code, delete)
