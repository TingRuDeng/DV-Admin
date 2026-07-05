"""
角色服务写操作测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound, ValidationError
from app.schemas.system import RoleCreate, RoleUpdate
from app.services.system.role_service import role_service

pytest_plugins = ["role_service_fixtures"]


class TestRoleServiceCreate:
    """测试创建角色。"""

    @pytest.mark.asyncio
    async def test_create_role_basic(self, db):
        """测试基本创建角色。"""
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
        """测试创建角色并关联权限。"""
        role_data = RoleCreate(
            name=f"带权限角色_{uuid.uuid4().hex[:8]}",
            code=f"perm_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
            permission_ids=[test_permission_for_service.id],
        )

        result = await role_service.create(role_data)

        assert result.name == role_data.name

        from app.db.models.system import Roles

        role = await Roles.get(id=result.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, db, test_role_for_service):
        """测试创建重复角色名。"""
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
        """测试创建角色包含所有字段。"""
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

    @pytest.mark.asyncio
    async def test_create_role_with_custom_data_scope(self, db):
        """创建角色时应保存自定义数据范围部门。"""
        from app.db.models.system import Departments, Roles

        dept = await Departments.create(name=f"数据权限部门_{uuid.uuid4().hex[:6]}", status=1, sort=1)
        role_data = RoleCreate(
            name=f"数据权限角色_{uuid.uuid4().hex[:8]}",
            code=f"data_scope_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
            data_scope=Roles.DATA_SCOPE_CUSTOM,
            dept_ids=[dept.id],
        )

        result = await role_service.create(role_data)

        assert result.data_scope == Roles.DATA_SCOPE_CUSTOM
        assert result.dept_ids == [dept.id]


class TestRoleServiceUpdate:
    """测试更新角色。"""

    @pytest.mark.asyncio
    async def test_update_role_basic(self, db, test_role_for_service):
        """测试基本更新角色。"""
        update_data = RoleUpdate(
            name="更新后的角色名",
            desc="更新后的描述",
        )

        result = await role_service.update(test_role_for_service.id, update_data)

        assert result.name == "更新后的角色名"
        assert result.desc == "更新后的描述"

    @pytest.mark.asyncio
    async def test_update_role_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试更新角色权限。"""
        update_data = RoleUpdate(permission_ids=[test_permission_for_service.id])

        await role_service.update(test_role_for_service.id, update_data)

        from app.db.models.system import Roles

        role = await Roles.get(id=test_role_for_service.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 1

    @pytest.mark.asyncio
    async def test_update_role_clear_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试清空角色权限。"""
        await test_role_for_service.permissions.add(test_permission_for_service)

        update_data = RoleUpdate(permission_ids=[])
        await role_service.update(test_role_for_service.id, update_data)

        from app.db.models.system import Roles

        role = await Roles.get(id=test_role_for_service.id)
        await role.fetch_related("permissions")
        assert len(role.permissions) == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, db):
        """测试更新不存在的角色。"""
        update_data = RoleUpdate(name="更新名字")

        with pytest.raises(NotFound) as exc_info:
            await role_service.update(99999, update_data)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_role_status(self, db, test_role_for_service):
        """测试更新角色状态。"""
        update_data = RoleUpdate(status=0)

        result = await role_service.update(test_role_for_service.id, update_data)

        assert result.status == 0

    @pytest.mark.asyncio
    async def test_update_role_custom_data_scope(self, db, test_role_for_service):
        """更新角色时应同步自定义部门范围。"""
        from app.db.models.system import Departments, Roles

        dept = await Departments.create(name=f"更新权限部门_{uuid.uuid4().hex[:6]}", status=1, sort=1)
        update_data = RoleUpdate(data_scope=Roles.DATA_SCOPE_CUSTOM, dept_ids=[dept.id])

        result = await role_service.update(test_role_for_service.id, update_data)

        assert result.data_scope == Roles.DATA_SCOPE_CUSTOM
        assert result.dept_ids == [dept.id]
