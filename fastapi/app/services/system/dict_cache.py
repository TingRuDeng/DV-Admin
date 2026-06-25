"""
字典服务缓存辅助能力
"""

from app.core.cache import CacheKeys, cache_service


class DictCacheMixin:
    """字典服务共享缓存操作"""

    # 缓存 TTL（秒），按原服务语义保留 10 分钟。
    CACHE_TTL = 600

    async def _clear_dict_cache(self, code: str | None = None) -> None:
        """
        清除字典缓存。

        Args:
            code: 字典编码，为 None 时清除所有字典缓存。
        """
        if code:
            cache_key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code=code)
            await cache_service.delete(cache_key)
            return

        await cache_service.clear("dict:*")
