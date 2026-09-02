"""
角色服务菜单权限测试。
"""
import uuid

import pytest

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound
from app.services.system.role_service import role_service

pytest_plugins = ["role_service_fixtures"]


class TestRoleServiceAssignMenus:
    """测试角色权限分配及关联用户缓存失效。"""

    @pytest.mark.asyncio
    async def test_assign_menus_clears_assigned_user_access_cache(
        self,
        db,
        test_role_for_service,
        test_permission_for_service,
    ):
        """撤权或授权后不应继续返回关联用户的旧权限与菜单。"""
        from app.db.models.oauth import Users

        user = await Users.create(
            username=f"角色缓存用户_{uuid.uuid4().hex[:8]}",
            password="not-used",
            name="角色缓存用户",
            is_active=1,
        )
        await user.roles.add(test_role_for_service)
        permission_cache_key = CacheKeys.format_key(
            CacheKeys.USER_PERMISSIONS,
            user_id=user.id,
        )
        menu_cache_key = CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user.id)
        await cache_service.set(permission_cache_key, ["stale:permission"])
        await cache_service.set(menu_cache_key, [{"path": "/stale"}])

        result = await role_service.assign_menus(
            test_role_for_service.id,
            [test_permission_for_service.id],
        )

        assert result == [test_permission_for_service.id]
        assert await cache_service.get(permission_cache_key) is None
        assert await cache_service.get(menu_cache_key) is None


class TestRoleServiceGetMenuIds:
    """测试获取角色菜单 ID 列表。"""

    @pytest.mark.asyncio
    async def test_get_menu_ids(self, db, test_role_for_service, test_permission_for_service):
        """测试获取角色菜单 ID 列表。"""
        await test_role_for_service.permissions.add(test_permission_for_service)

        result = await role_service.get_menu_ids(test_role_for_service.id)

        assert isinstance(result, list)
        assert test_permission_for_service.id in result

    @pytest.mark.asyncio
    async def test_get_menu_ids_nonexistent_role(self, db):
        """测试获取不存在角色的菜单 ID。"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get_menu_ids(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_menu_ids_empty(self, db, test_role_for_service):
        """测试获取无权限角色的菜单 ID。"""
        result = await role_service.get_menu_ids(test_role_for_service.id)

        assert isinstance(result, list)
        assert len(result) == 0


class TestRoleServiceGetMenus:
    """测试获取角色菜单列表。"""

    @pytest.mark.asyncio
    async def test_get_menus(self, db, test_role_for_service):
        """测试获取角色菜单列表。"""
        from app.db.models.system import Permissions

        menu_perm = await Permissions.create(
            name=f"测试菜单_{uuid.uuid4().hex[:6]}",
            type="MENU",
            route_name=f"TestMenu_{uuid.uuid4().hex[:6]}",
            route_path="/test/menu",
        )
        button_perm = await Permissions.create(
            name=f"测试按钮_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"test:button:{uuid.uuid4().hex[:6]}",
        )

        await test_role_for_service.permissions.add(menu_perm, button_perm)

        result = await role_service.get_menus(test_role_for_service.id)

        assert isinstance(result, list)
        for menu in result:
            assert menu["type"] in ["CATALOG", "MENU"]

    @pytest.mark.asyncio
    async def test_get_menus_nonexistent_role(self, db):
        """测试获取不存在角色的菜单。"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get_menus(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_menus_empty(self, db, test_role_for_service):
        """测试获取无菜单角色的菜单列表。"""
        result = await role_service.get_menus(test_role_for_service.id)

        assert isinstance(result, list)
        assert len(result) == 0
