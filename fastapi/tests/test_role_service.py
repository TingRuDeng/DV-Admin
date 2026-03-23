"""
角色服务层测试
测试 RoleService 的所有方法，包括 CRUD 操作、边界条件和异常情况
"""
import uuid

import pytest
import pytest_asyncio

from app.core.exceptions import NotFound, ValidationError
from app.schemas.system import RoleCreate, RoleUpdate
from app.services.system.role_service import role_service


@pytest_asyncio.fixture
async def test_permission_for_service(db):
    """创建测试权限"""
    from app.db.models.system import Permissions

    perm = await Permissions.create(
        name=f"测试权限_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm:{uuid.uuid4().hex[:6]}",
    )
    return perm


@pytest_asyncio.fixture
async def test_role_for_service(db):
    """创建测试角色"""
    from app.db.models.system import Roles

    role = await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
    )
    return role


class TestRoleServiceGetPage:
    """测试角色分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_role_for_service):
        """测试基本分页查询"""
        result = await role_service.get_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_page_with_search(self, db, test_role_for_service):
        """测试带搜索条件的分页查询"""
        result = await role_service.get_page(
            page=1,
            page_size=10,
            search=test_role_for_service.name[:10]
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果"""
        result = await role_service.get_page(
            page=1,
            page_size=10,
            search="nonexistent_role_12345"
        )

        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_pagination(self, db):
        """测试分页功能"""
        from app.db.models.system import Roles

        # 创建多个角色
        for i in range(15):
            await Roles.create(
                name=f"分页角色_{i}_{uuid.uuid4().hex[:6]}",
                code=f"page_role_{i}_{uuid.uuid4().hex[:6]}",
                status=1,
                sort=i,
            )

        # 测试第一页
        result1 = await role_service.get_page(page=1, page_size=10)
        assert len(result1.results) == 10

        # 测试第二页
        result2 = await role_service.get_page(page=2, page_size=10)
        assert len(result2.results) >= 5


class TestRoleServiceGet:
    """测试获取角色详情"""

    @pytest.mark.asyncio
    async def test_get_existing_role(self, db, test_role_for_service):
        """测试获取存在的角色"""
        result = await role_service.get(test_role_for_service.id)

        assert result.id == test_role_for_service.id
        assert result.name == test_role_for_service.name
        assert result.code == test_role_for_service.code

    @pytest.mark.asyncio
    async def test_get_nonexistent_role(self, db):
        """测试获取不存在的角色"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_role_with_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试获取带权限的角色"""
        # 关联权限
        await test_role_for_service.permissions.add(test_permission_for_service)

        result = await role_service.get(test_role_for_service.id)

        assert result.id == test_role_for_service.id
        assert hasattr(result, 'permissions')
        assert test_permission_for_service.id in result.permissions


class TestRoleServiceCreate:
    """测试创建角色"""

    @pytest.mark.asyncio
    async def test_create_role_basic(self, db):
        """测试基本创建角色"""
        role_data = RoleCreate(
            name=f"新角色_{uuid.uuid4().hex[:8]}",
            code=f"new_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
        )

        result = await role_service.create(role_data)

        assert result.name == role_data.name
        assert result.code == role_data.code
        assert result.status == 1

    @pytest.mark.asyncio
    async def test_create_role_with_permissions(self, db, test_permission_for_service):
        """测试创建角色并关联权限"""
        role_data = RoleCreate(
            name=f"带权限角色_{uuid.uuid4().hex[:8]}",
            code=f"perm_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
            permission_ids=[test_permission_for_service.id],
        )

        result = await role_service.create(role_data)

        assert result.name == role_data.name

        # 验证权限关联
        from app.db.models.system import Roles
        role = await Roles.get(id=result.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, db, test_role_for_service):
        """测试创建重复角色名"""
        role_data = RoleCreate(
            name=test_role_for_service.name,
            code=f"dup_code_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
        )

        with pytest.raises(ValidationError) as exc_info:
            await role_service.create(role_data)

        assert "角色名称已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_role_with_all_fields(self, db):
        """测试创建角色包含所有字段"""
        role_data = RoleCreate(
            name=f"完整角色_{uuid.uuid4().hex[:8]}",
            code=f"full_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=10,
            is_default=1,
            desc="这是一个完整的角色描述",
        )

        result = await role_service.create(role_data)

        assert result.name == role_data.name
        assert result.code == role_data.code
        assert result.status == 1
        assert result.sort == 10
        assert result.is_default == 1
        assert result.desc == "这是一个完整的角色描述"


class TestRoleServiceUpdate:
    """测试更新角色"""

    @pytest.mark.asyncio
    async def test_update_role_basic(self, db, test_role_for_service):
        """测试基本更新角色"""
        update_data = RoleUpdate(
            name="更新后的角色名",
            desc="更新后的描述",
        )

        result = await role_service.update(test_role_for_service.id, update_data)

        assert result.name == "更新后的角色名"
        assert result.desc == "更新后的描述"

    @pytest.mark.asyncio
    async def test_update_role_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试更新角色权限"""
        update_data = RoleUpdate(
            permission_ids=[test_permission_for_service.id]
        )

        result = await role_service.update(test_role_for_service.id, update_data)

        # 验证权限更新
        from app.db.models.system import Roles
        role = await Roles.get(id=test_role_for_service.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 1

    @pytest.mark.asyncio
    async def test_update_role_clear_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试清空角色权限"""
        # 先添加权限
        await test_role_for_service.permissions.add(test_permission_for_service)

        # 清空权限
        update_data = RoleUpdate(permission_ids=[])
        result = await role_service.update(test_role_for_service.id, update_data)

        # 验证权限已清空
        from app.db.models.system import Roles
        role = await Roles.get(id=test_role_for_service.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, db):
        """测试更新不存在的角色"""
        update_data = RoleUpdate(name="更新名字")

        with pytest.raises(NotFound) as exc_info:
            await role_service.update(99999, update_data)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_role_status(self, db, test_role_for_service):
        """测试更新角色状态"""
        update_data = RoleUpdate(status=0)

        result = await role_service.update(test_role_for_service.id, update_data)

        assert result.status == 0


class TestRoleServiceDelete:
    """测试删除角色"""

    @pytest.mark.asyncio
    async def test_delete_role(self, db):
        """测试删除角色"""
        from app.db.models.system import Roles

        # 创建一个新角色用于删除
        role_to_delete = await Roles.create(
            name=f"待删除角色_{uuid.uuid4().hex[:8]}",
            code=f"del_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
        )

        await role_service.delete(role_to_delete.id)

        # 验证角色已删除
        deleted_role = await Roles.get_or_none(id=role_to_delete.id)
        assert deleted_role is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, db):
        """测试删除不存在的角色"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.delete(99999)

        assert "角色不存在" in str(exc_info.value)


class TestRoleServiceBatchDelete:
    """测试批量删除角色"""

    @pytest.mark.asyncio
    async def test_batch_delete_roles(self, db):
        """测试批量删除角色"""
        from app.db.models.system import Roles

        # 创建多个角色
        role_ids = []
        for i in range(3):
            role = await Roles.create(
                name=f"批量角色_{i}_{uuid.uuid4().hex[:8]}",
                code=f"batch_role_{i}_{uuid.uuid4().hex[:8]}",
                status=1,
                sort=i,
            )
            role_ids.append(role.id)

        # 批量删除
        await role_service.batch_delete(role_ids)

        # 验证角色已删除
        for role_id in role_ids:
            deleted_role = await Roles.get_or_none(id=role_id)
            assert deleted_role is None

    @pytest.mark.asyncio
    async def test_batch_delete_empty_list(self, db):
        """测试批量删除空列表"""
        # 应该不抛出异常
        await role_service.batch_delete([])


class TestRoleServiceGetOptions:
    """测试获取角色选项"""

    @pytest.mark.asyncio
    async def test_get_options(self, db, test_role_for_service):
        """测试获取角色下拉选项"""
        result = await role_service.get_options()

        assert isinstance(result, list)
        assert len(result) >= 1

        # 验证格式
        for option in result:
            assert "id" in option
            assert "label" in option

    @pytest.mark.asyncio
    async def test_get_options_only_active(self, db):
        """测试只返回激活状态的角色"""
        from app.db.models.system import Roles

        # 创建一个禁用的角色
        inactive_role = await Roles.create(
            name=f"禁用角色_{uuid.uuid4().hex[:8]}",
            code=f"inactive_role_{uuid.uuid4().hex[:8]}",
            status=0,
            sort=1,
        )

        result = await role_service.get_options()

        # 验证禁用角色不在选项中
        option_ids = [opt["id"] for opt in result]
        assert inactive_role.id not in option_ids


class TestRoleServiceGetMenuIds:
    """测试获取角色菜单ID列表"""

    @pytest.mark.asyncio
    async def test_get_menu_ids(self, db, test_role_for_service, test_permission_for_service):
        """测试获取角色菜单ID列表"""
        # 关联权限
        await test_role_for_service.permissions.add(test_permission_for_service)

        result = await role_service.get_menu_ids(test_role_for_service.id)

        assert isinstance(result, list)
        assert test_permission_for_service.id in result

    @pytest.mark.asyncio
    async def test_get_menu_ids_nonexistent_role(self, db):
        """测试获取不存在角色的菜单ID"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get_menu_ids(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_menu_ids_empty(self, db, test_role_for_service):
        """测试获取无权限角色的菜单ID"""
        result = await role_service.get_menu_ids(test_role_for_service.id)

        assert isinstance(result, list)
        assert len(result) == 0


class TestRoleServiceGetMenus:
    """测试获取角色菜单列表"""

    @pytest.mark.asyncio
    async def test_get_menus(self, db, test_role_for_service):
        """测试获取角色菜单列表"""
        from app.db.models.system import Permissions

        # 创建菜单类型的权限
        menu_perm = await Permissions.create(
            name=f"测试菜单_{uuid.uuid4().hex[:6]}",
            type="MENU",
            route_name=f"TestMenu_{uuid.uuid4().hex[:6]}",
            route_path="/test/menu",
        )

        # 创建按钮类型的权限
        button_perm = await Permissions.create(
            name=f"测试按钮_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"test:button:{uuid.uuid4().hex[:6]}",
        )

        # 关联权限
        await test_role_for_service.permissions.add(menu_perm, button_perm)

        result = await role_service.get_menus(test_role_for_service.id)

        assert isinstance(result, list)
        # 只应该返回菜单类型的权限
        for menu in result:
            assert menu["type"] in ["CATALOG", "MENU"]

    @pytest.mark.asyncio
    async def test_get_menus_nonexistent_role(self, db):
        """测试获取不存在角色的菜单"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get_menus(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_menus_empty(self, db, test_role_for_service):
        """测试获取无菜单角色的菜单列表"""
        result = await role_service.get_menus(test_role_for_service.id)

        assert isinstance(result, list)
        assert len(result) == 0
