"""
角色服务层测试
测试 RoleService 的更多方法
"""
import uuid

import pytest
import pytest_asyncio

from app.core.exceptions import NotFound
from app.db.models.system import Permissions, Roles
from app.schemas.system import RoleCreate, RoleUpdate
from app.services.system.role_service import role_service


@pytest_asyncio.fixture
async def test_role_for_service(db):
    """创建测试角色"""
    role = await Roles.create(
        name=f"服务测试角色_{uuid.uuid4().hex[:6]}",
        code=f"service_role_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
    )
    return role


@pytest_asyncio.fixture
async def test_permissions_for_role(db):
    """创建测试权限"""
    perms = []
    for i in range(3):
        perm = await Permissions.create(
            name=f"角色测试权限_{i}_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"role:test:{i}_{uuid.uuid4().hex[:6]}",
        )
        perms.append(perm)
    return perms


class TestRoleServiceGetPage:
    """测试角色分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_role_for_service):
        """测试基本分页查询"""
        result = await role_service.get_page(page=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_search(self, db, test_role_for_service):
        """测试按名称搜索"""
        result = await role_service.get_page(
            page=1, page_size=10, search=test_role_for_service.name[:10]
        )
        assert result.total >= 1


class TestRoleServiceGet:
    """测试获取角色详情"""

    @pytest.mark.asyncio
    async def test_get_existing(self, db, test_role_for_service):
        """测试获取存在的角色"""
        result = await role_service.get(test_role_for_service.id)
        assert result.id == test_role_for_service.id

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db):
        """测试获取不存在的角色"""
        with pytest.raises(NotFound):
            await role_service.get(99999)


class TestRoleServiceGetOptions:
    """测试获取角色选项"""

    @pytest.mark.asyncio
    async def test_get_options(self, db, test_role_for_service):
        """测试获取角色选项列表"""
        result = await role_service.get_options()
        assert len(result) >= 1


class TestRoleServiceGetMenuIds:
    """测试获取角色菜单ID"""

    @pytest.mark.asyncio
    async def test_get_menu_ids(self, db, test_role_for_service):
        """测试获取角色菜单ID列表"""
        result = await role_service.get_menu_ids(test_role_for_service.id)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_menu_ids_nonexistent(self, db):
        """测试获取不存在角色的菜单ID"""
        with pytest.raises(NotFound):
            await role_service.get_menu_ids(99999)


class TestRoleServiceGetMenus:
    """测试获取角色菜单"""

    @pytest.mark.asyncio
    async def test_get_menus(self, db, test_role_for_service):
        """测试获取角色菜单列表"""
        result = await role_service.get_menus(test_role_for_service.id)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_menus_nonexistent(self, db):
        """测试获取不存在角色的菜单"""
        with pytest.raises(NotFound):
            await role_service.get_menus(99999)


class TestRoleServiceCreate:
    """测试创建角色"""

    @pytest.mark.asyncio
    async def test_create_basic(self, db):
        """测试基本创建"""
        role_in = RoleCreate(
            name=f"新角色_{uuid.uuid4().hex[:6]}",
            code=f"new_role_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=1,
        )
        result = await role_service.create(role_in)
        assert result.id is not None
        assert result.name == role_in.name

    @pytest.mark.asyncio
    async def test_create_with_permissions(self, db, test_permissions_for_role):
        """测试创建带权限的角色"""
        role_in = RoleCreate(
            name=f"权限角色_{uuid.uuid4().hex[:6]}",
            code=f"perm_role_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=1,
            permission_ids=[p.id for p in test_permissions_for_role],
        )
        result = await role_service.create(role_in)
        assert result.id is not None


class TestRoleServiceUpdate:
    """测试更新角色"""

    @pytest.mark.asyncio
    async def test_update_basic(self, db, test_role_for_service):
        """测试基本更新"""
        role_in = RoleUpdate(name=f"更新角色_{uuid.uuid4().hex[:6]}")
        result = await role_service.update(test_role_for_service.id, role_in)
        assert result.name == role_in.name

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db):
        """测试更新不存在的角色"""
        role_in = RoleUpdate(name="更新角色")
        with pytest.raises(NotFound):
            await role_service.update(99999, role_in)


class TestRoleServiceDelete:
    """测试删除角色"""

    @pytest.mark.asyncio
    async def test_delete_single(self, db):
        """测试删除单个角色"""
        role = await Roles.create(
            name=f"待删除角色_{uuid.uuid4().hex[:6]}",
            code=f"delete_role_{uuid.uuid4().hex[:6]}",
            status=1,
        )
        await role_service.delete(role.id)
        exists = await Roles.filter(id=role.id).exists()
        assert not exists

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db):
        """测试删除不存在的角色"""
        with pytest.raises(NotFound):
            await role_service.delete(99999)

    @pytest.mark.asyncio
    async def test_batch_delete(self, db):
        """测试批量删除角色"""
        roles = []
        for i in range(3):
            role = await Roles.create(
                name=f"批量删除角色_{i}_{uuid.uuid4().hex[:6]}",
                code=f"batch_delete_{i}_{uuid.uuid4().hex[:6]}",
                status=1,
            )
            roles.append(role)

        ids = [r.id for r in roles]
        await role_service.batch_delete(ids)

        for role_id in ids:
            exists = await Roles.filter(id=role_id).exists()
            assert not exists
