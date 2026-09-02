"""
菜单服务层测试
测试 MenuService 的所有方法
"""
import uuid

import pytest
import pytest_asyncio

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Permissions, Roles
from app.schemas.system import MenuCreate, MenuUpdate
from app.services.system.menu_service import menu_service


async def assign_permission_to_user(permission: Permissions) -> Users:
    """创建通过角色持有指定权限的用户。"""
    role = await Roles.create(
        name=f"菜单缓存角色_{uuid.uuid4().hex[:6]}",
        code=f"menu-cache-{uuid.uuid4().hex[:8]}",
        status=1,
    )
    user = await Users.create(
        username=f"菜单缓存用户_{uuid.uuid4().hex[:8]}",
        password="not-used",
        name="菜单缓存用户",
        is_active=1,
    )
    await role.permissions.add(permission)
    await user.roles.add(role)
    return user


async def seed_user_access_cache(user_id: int) -> tuple[str, str]:
    """写入可识别的旧权限与旧菜单缓存。"""
    permission_key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=user_id)
    menu_key = CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=user_id)
    await cache_service.set(permission_key, ["stale:permission"])
    await cache_service.set(menu_key, [{"path": "/stale"}])
    return permission_key, menu_key


@pytest_asyncio.fixture
async def test_menus_for_service(db):
    """创建测试菜单"""
    # 创建目录
    catalog = await Permissions.create(
        name=f"测试目录_{uuid.uuid4().hex[:6]}",
        type="CATALOG",
        sort=1,
    )

    # 创建菜单
    menu = await Permissions.create(
        name=f"测试菜单_{uuid.uuid4().hex[:6]}",
        type="MENU",
        route_name="TestMenu",
        route_path="/test/menu",
        component="test/menu/index",
        sort=1,
        parent_id=catalog.id,
        perm="test:menu:query",
    )

    # 创建按钮
    button = await Permissions.create(
        name=f"测试按钮_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        parent_id=menu.id,
        perm="test:menu:add",
    )

    return {"catalog": catalog, "menu": menu, "button": button}


class TestMenuServiceGetTree:
    """测试获取菜单树"""

    @pytest.mark.asyncio
    async def test_get_tree_basic(self, db, test_menus_for_service):
        """测试基本获取菜单树"""
        result = await menu_service.get_tree()
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_tree_includes_label_children_and_parent_id(self, db, test_menus_for_service):
        """菜单树输出必须包含树组件字段和统一父级 ID 字段。"""
        result = await menu_service.get_tree()
        catalog = next(item for item in result if item.id == test_menus_for_service["catalog"].id)
        child = next(item for item in catalog.children if item.id == test_menus_for_service["menu"].id)

        assert catalog.label == catalog.name
        assert isinstance(catalog.children, list)
        assert child.parent_id == catalog.id


class TestMenuServiceGetOptions:
    """测试获取菜单选项"""

    @pytest.mark.asyncio
    async def test_get_options_basic(self, db, test_menus_for_service):
        """菜单选项必须匹配前端 ElTreeSelect 的 id/label/children 契约。"""
        result = await menu_service.get_options()
        catalog = next(
            item for item in result if item["id"] == test_menus_for_service["catalog"].id
        )
        menu = next(
            item
            for item in catalog["children"]
            if item["id"] == test_menus_for_service["menu"].id
        )

        assert catalog["label"] == test_menus_for_service["catalog"].name
        assert menu["children"][0]["id"] == test_menus_for_service["button"].id
        assert "value" not in catalog


class TestMenuServiceGet:
    """测试获取菜单详情"""

    @pytest.mark.asyncio
    async def test_get_existing(self, db, test_menus_for_service):
        """测试获取存在的菜单"""
        menu = test_menus_for_service["menu"]
        result = await menu_service.get(menu.id)
        assert result.id == menu.id
        assert result.name == menu.name
        assert result.parent_id == test_menus_for_service["catalog"].id

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db):
        """测试获取不存在的菜单"""
        with pytest.raises(NotFound):
            await menu_service.get(99999)


class TestMenuServiceCreate:
    """测试创建菜单"""

    @pytest.mark.asyncio
    async def test_create_catalog(self, db):
        """测试创建目录"""
        menu_in = MenuCreate(
            name=f"新目录_{uuid.uuid4().hex[:6]}",
            type="CATALOG",
            sort=1,
        )
        result = await menu_service.create(menu_in)
        assert result.id is not None
        assert result.type == "CATALOG"

    @pytest.mark.asyncio
    async def test_create_menu(self, db, test_menus_for_service):
        """测试创建菜单"""
        catalog = test_menus_for_service["catalog"]
        menu_in = MenuCreate(
            name=f"新菜单_{uuid.uuid4().hex[:6]}",
            type="MENU",
            route_name="NewMenu",
            route_path="/new/menu",
            component="new/menu/index",
            sort=1,
            parent_id=catalog.id,
            perm="new:menu:query",
        )
        result = await menu_service.create(menu_in)
        assert result.type == "MENU"
        assert result.parent_id == catalog.id

    @pytest.mark.asyncio
    async def test_create_button(self, db, test_menus_for_service):
        """测试创建按钮"""
        menu = test_menus_for_service["menu"]
        menu_in = MenuCreate(
            name=f"新按钮_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            parent_id=menu.id,
            perm="new:menu:button",
        )
        result = await menu_service.create(menu_in)
        assert result.type == "BUTTON"


class TestMenuServiceUpdate:
    """测试更新菜单"""

    @pytest.mark.asyncio
    async def test_update_basic(self, db, test_menus_for_service):
        """测试基本更新菜单"""
        menu = test_menus_for_service["menu"]
        menu_in = MenuUpdate(name=f"更新菜单_{uuid.uuid4().hex[:6]}")
        result = await menu_service.update(menu.id, menu_in)
        assert result.name == menu_in.name

    @pytest.mark.asyncio
    async def test_update_clears_assigned_user_access_cache(self, db, test_menus_for_service):
        """菜单变更后重新登录必须读取新动态路由。"""
        menu = test_menus_for_service["menu"]
        user = await assign_permission_to_user(menu)
        permission_key, menu_key = await seed_user_access_cache(user.id)

        await menu_service.update(menu.id, MenuUpdate(name="缓存已更新菜单"))

        assert await cache_service.get(permission_key) is None
        assert await cache_service.get(menu_key) is None

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db):
        """测试更新不存在的菜单"""
        menu_in = MenuUpdate(name="更新菜单")
        with pytest.raises(NotFound):
            await menu_service.update(99999, menu_in)


class TestMenuServiceDelete:
    """测试删除菜单"""

    @pytest.mark.asyncio
    async def test_delete_basic(self, db):
        """测试删除菜单"""
        menu = await Permissions.create(
            name=f"待删除菜单_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm="delete:menu:test",
        )
        await menu_service.delete(menu.id)
        exists = await Permissions.filter(id=menu.id).exists()
        assert not exists

    @pytest.mark.asyncio
    async def test_delete_clears_assigned_user_access_cache(self, db):
        """权限对象删除后不得继续返回旧按钮权限或菜单。"""
        permission = await Permissions.create(
            name=f"待删除权限_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm="delete:permission:test",
        )
        user = await assign_permission_to_user(permission)
        permission_key, menu_key = await seed_user_access_cache(user.id)

        await menu_service.delete(permission.id)

        assert await cache_service.get(permission_key) is None
        assert await cache_service.get(menu_key) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db):
        """测试删除不存在的菜单"""
        with pytest.raises(NotFound):
            await menu_service.delete(99999)
