"""
Redis 连接管理模块

提供 Redis 连接池管理和基础操作。
"""

from typing import Optional

from loguru import logger
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from app.core.config import settings


class RedisManager:
    """
    Redis 连接管理器

    单例模式管理 Redis 连接池。
    """

    _instance: Optional["RedisManager"] = None
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    def __new__(cls) -> "RedisManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self) -> None:
        """
        初始化 Redis 连接池
        """
        if self._pool is not None:
            return

        try:
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                password=settings.redis_password,
                decode_responses=True,
                max_connections=10,
            )
            self._client = Redis(connection_pool=self._pool)
            # 测试连接
            await self._client.ping()
            logger.info("Redis 连接池初始化成功")
        except RedisError as e:
            logger.error(f"Redis 连接池初始化失败: {e}")
            self._pool = None
            self._client = None
            raise

    async def close(self) -> None:
        """
        关闭 Redis 连接池
        """
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis 客户端已关闭")

        if self._pool:
            await self._pool.disconnect()
            self._pool = None
            logger.info("Redis 连接池已关闭")

    @property
    def client(self) -> Redis:
        """
        获取 Redis 客户端

        Returns:
            Redis 客户端实例

        Raises:
            RuntimeError: Redis 未初始化
        """
        if self._client is None:
            raise RuntimeError("Redis 未初始化，请先调用 init()")
        return self._client

    async def is_connected(self) -> bool:
        """
        检查 Redis 是否已连接

        Returns:
            是否已连接
        """
        if self._client is None:
            return False
        try:
            await self._client.ping()
            return True
        except RedisError:
            return False


# 全局 Redis 管理器实例
redis_manager = RedisManager()


async def get_redis() -> Redis:
    """
    获取 Redis 客户端依赖

    Returns:
        Redis 客户端实例
    """
    return redis_manager.client
