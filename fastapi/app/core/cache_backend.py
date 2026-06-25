"""
缓存后端抽象接口。
"""
from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    """缓存后端抽象基类。"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """获取缓存值。"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值。"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存。"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        pass

    @abstractmethod
    async def clear(self, pattern: str | None = None) -> int:
        """清除缓存。"""
        pass
