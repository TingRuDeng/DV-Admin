"""OAuth 用户权限与菜单访问逻辑测试。"""

import pytest

from app.core.cache import CacheKeys, cache_service
from app.db.models.oauth import Users
from app.db.models.system import Roles


async def _clear_user_access_cache(user_id: int) -> None:
    """清理用户访问缓存，避免同一测试内权限变更后读到旧值。"""
    await cache_service.delete(CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=user_id))
    await cache_service.delete(CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user_id))


class TestOAuthUserAccess:
    """测试用户模型暴露的权限和菜单访问方法。"""

    @pytest.mark.asyncio
    async def test_get_permissions_returns_role_permission_codes(self, test_user_with_role):
        """用户权限列表应包含角色绑定的权限码。"""
        user = await Users.get(id=test_user_with_role["id"])
        await _clear_user_access_cache(user.id)

        permissions = await user.get_permissions()

        assert "system:users:query" in permissions
        assert await user.has_perm("system:users:query") is True
        assert await user.has_perm("system:users:missing") is False

    @pytest.mark.asyncio
    async def test_has_role_matches_user_role_code(self, test_user_with_role):
        """用户角色判断应按角色编码匹配。"""
        user = await Users.get(id=test_user_with_role["id"])

        assert await user.has_role("admin") is True
        assert await user.has_role("missing") is False

    @pytest.mark.asyncio
    async def test_get_menus_builds_tree_without_empty_children(
        self,
        test_permissions,
        test_role,
        test_user_with_role,
    ):
        """用户菜单应返回树结构，并删除空 children 字段。"""
        role = await Roles.get(id=test_role["id"])
        await role.permissions.add(test_permissions["system_catalog"])

        user = await Users.get(id=test_user_with_role["id"])
        await _clear_user_access_cache(user.id)

        menus = await user.get_menus()

        assert menus[0]["meta"]["title"] == "系统管理"
        child_titles = {child["meta"]["title"] for child in menus[0]["children"]}
        assert "用户管理" in child_titles
        user_menu = next(
            child for child in menus[0]["children"]
            if child["meta"]["title"] == "用户管理"
        )
        assert "children" not in user_menu

    @pytest.mark.asyncio
    async def test_superuser_has_all_permissions_without_permission_list(self, db):
        """超级用户保持空权限列表和任意权限命中语义。"""
        user = await Users.create(
            username="super_access_user",
            password="hashed",
            name="超级用户",
            is_active=1,
            is_superuser=True,
        )

        assert await user.get_permissions() == []
        assert await user.has_perm("system:anything") is True
