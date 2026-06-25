"""用户缓存清理服务。"""

from app.core.cache import CacheKeys, cache_service


class UserCacheMixin:
    """提供用户权限和菜单缓存清理能力。"""

    async def _clear_user_cache(self, user_id: int) -> None:
        """
        清除用户缓存

        Args:
            user_id: 用户ID
        """
        # 清除用户权限缓存
        cache_key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=user_id)
        await cache_service.delete(cache_key)
        # 清除用户菜单缓存
        cache_key = CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user_id)
        await cache_service.delete(cache_key)

