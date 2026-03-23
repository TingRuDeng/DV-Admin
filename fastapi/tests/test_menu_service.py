"""
菜单服务层测试
测试 MenuService 的所有方法
"""
import uuid

import pytest
import pytest_asyncio

from app.core.exceptions import NotFound
from app.db.models.system import Permissions
from app.schemas.system import MenuCreate, MenuUpdate
from app.services.system.menu_service import menu_service


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


class TestMenuServiceGetOptions:
    """测试获取菜单选项"""

    @pytest.mark.asyncio
    async def test_get_options_basic(self, db, test_menus_for_service):
        """测试基本获取菜单选项"""
        result = await menu_service.get_options()
        assert len(result) >= 1


class TestMenuServiceGet:
    """测试获取菜单详情"""

    @pytest.mark.asyncio
    async def test_get_existing(self, db, test_menus_for_service):
        """测试获取存在的菜单"""
        menu = test_menus_for_service["menu"]
        result = await menu_service.get(menu.id)
        assert result.id == menu.id
        assert result.name == menu.name

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
    async def test_delete_nonexistent(self, db):
        """测试删除不存在的菜单"""
        with pytest.raises(NotFound):
            await menu_service.delete(99999)
