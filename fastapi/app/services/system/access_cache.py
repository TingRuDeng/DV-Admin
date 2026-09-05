"""用户权限与动态菜单缓存失效 helper。"""

from collections.abc import Iterable
from typing import cast

from app.core.cache import CacheKeys, cache_service
from app.db.models.oauth import Users


async def clear_user_access_cache(user_ids: Iterable[int]) -> None:
    """清除指定用户的权限与动态菜单缓存。"""
    for user_id in set(user_ids):
        await cache_service.delete(
            CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=user_id)
        )
        await cache_service.delete(
            CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user_id)
        )


async def get_role_user_ids(role_id: int) -> list[int]:
    """返回被指定角色影响的用户 ID。"""
    user_ids = await Users.filter(roles__id=role_id).values_list("id", flat=True)
    return cast(list[int], user_ids)


async def get_roles_user_ids(role_ids: Iterable[int]) -> list[int]:
    """返回被多个角色影响的去重用户 ID。"""
    normalized_ids = set(role_ids)
    if not normalized_ids:
        return []
    user_ids = (
        await Users.filter(roles__id__in=normalized_ids)
        .distinct()
        .values_list("id", flat=True)
    )
    return cast(list[int], user_ids)


async def get_permission_user_ids(permission_id: int) -> list[int]:
    """返回通过任一角色持有指定权限的用户 ID。"""
    user_ids = (
        await Users.filter(roles__permissions__id=permission_id)
        .distinct()
        .values_list("id", flat=True)
    )
    return cast(list[int], user_ids)
