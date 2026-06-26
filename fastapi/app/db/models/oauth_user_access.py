"""OAuth 用户权限与菜单访问 helper。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.cache import CacheKeys, cache_service
from app.db.models.system import Permissions, Roles

if TYPE_CHECKING:
    from app.db.models.oauth import Users

USER_ACCESS_CACHE_TTL_SECONDS = 600
MENU_PERMISSION_TYPES = {
    Permissions.TYPE_CATALOG,
    Permissions.TYPE_MENU,
    Permissions.TYPE_EXT_LINK,
}

MenuItem = dict[str, Any]
MenuEntry = dict[str, Any]


async def get_user_permissions(user: Users) -> list[str]:
    """获取用户所有权限标识，并沿用原有用户权限缓存语义。"""
    if user.is_superuser:
        return []

    cache_key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=user.id)
    cached = await cache_service.get(cache_key)
    if cached is not None:
        return cached

    permissions = await _collect_role_permissions(user)
    result = list(permissions)
    await cache_service.set(cache_key, result, ttl=USER_ACCESS_CACHE_TTL_SECONDS)
    return result


async def get_user_menus(user: Users) -> list[MenuItem]:
    """获取用户菜单树，并沿用原有用户菜单缓存语义。"""
    cache_key = CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user.id)
    cached = await cache_service.get(cache_key)
    if cached is not None:
        return cached

    menu_ids = await _collect_role_menu_ids(user)
    menus = await Permissions.filter(id__in=menu_ids, visible=1).order_by("sort")
    menu_tree = build_menu_tree(menus)

    await cache_service.set(cache_key, menu_tree, ttl=USER_ACCESS_CACHE_TTL_SECONDS)
    return menu_tree


async def _collect_role_permissions(user: Users) -> set[str]:
    """从用户角色中收集非空权限码。"""
    roles = await _get_roles_with_permissions(user)
    return {
        permission.perm
        for role in roles
        for permission in role.permissions
        if permission.perm
    }


async def _collect_role_menu_ids(user: Users) -> set[int]:
    """从用户角色权限中收集可作为菜单返回的权限 ID。"""
    roles = await _get_roles_with_permissions(user)
    return {
        permission.id
        for role in roles
        for permission in role.permissions
        if permission.type in MENU_PERMISSION_TYPES
    }


async def _get_roles_with_permissions(user: Users) -> list[Roles]:
    """按用户角色 ID 查询带权限预取的角色，避免访问角色权限时产生 N+1 查询。"""
    await user.fetch_related("roles")
    role_ids = [role.id for role in user.roles]
    if not role_ids:
        return []
    return await Roles.filter(id__in=role_ids).prefetch_related("permissions")


def build_menu_tree(menus: list[Permissions]) -> list[MenuItem]:
    """将扁平菜单权限列表转换为前端动态路由需要的树结构。"""
    menu_dict = _build_menu_dict(menus)
    menu_list = _attach_menu_children(menus, menu_dict)
    remove_empty_children(menu_list)
    return menu_list


def _build_menu_dict(menus: list[Permissions]) -> dict[int, MenuEntry]:
    """构建菜单 ID 到菜单条目的映射，便于后续按 parent_id 挂载子节点。"""
    return {
        menu.id: {"item": build_menu_item(menu), "parent_id": menu.parent_id}
        for menu in menus
    }


def build_menu_item(menu: Permissions) -> MenuItem:
    """构建单个前端路由菜单项，保持原有字段和默认值语义。"""
    menu_item: MenuItem = {
        "path": menu.route_path,
        "component": menu.component if menu.component else "Layout",
        "name": menu.route_name if menu.route_name else menu.route_path,
        "meta": {
            "title": menu.name,
            "icon": menu.icon if menu.icon else "",
            "hidden": False if menu.visible else True,
            "alwaysShow": False if menu.always_show is None else menu.always_show,
            "params": menu.params if menu.params else [],
            "keepAlive": False if menu.keep_alive is None else menu.keep_alive,
        },
        "children": [],
    }

    if menu.redirect:
        menu_item["redirect"] = menu.redirect

    return menu_item


def _attach_menu_children(
    menus: list[Permissions],
    menu_dict: dict[int, MenuEntry],
) -> list[MenuItem]:
    """按 parent_id 将菜单挂到父菜单，缺失父菜单时沿用原行为跳过。"""
    menu_list: list[MenuItem] = []
    for menu in menus:
        menu_entry = menu_dict[menu.id]
        if menu.parent_id is None:
            menu_list.append(menu_entry["item"])
            continue

        if menu.parent_id in menu_dict:
            parent_item = menu_dict[menu.parent_id]["item"]
            parent_item["children"].append(menu_entry["item"])

    return menu_list


def remove_empty_children(menu_items: list[MenuItem]) -> None:
    """递归删除空 children 字段，保持前端历史响应结构。"""
    for item in menu_items:
        children = item.get("children")
        if children == []:
            del item["children"]
        elif children:
            remove_empty_children(children)
