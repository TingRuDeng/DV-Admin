"""用户服务查询测试。"""

import pytest

from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Departments, Permissions, Roles
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]

class TestUserServiceGetPage:
    """测试用户分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_user_for_service):
        """测试基本分页查询"""
        result = await user_service.get_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_page_includes_role_ids_and_names(self, db, test_user_for_service, test_role_for_service):
        """用户分页输出必须同时包含角色 ID 和角色名称。"""
        await test_user_for_service.roles.add(test_role_for_service)

        result = await user_service.get_page(
            page=1,
            page_size=10,
            search=test_user_for_service.username,
        )

        page_user = next(item for item in result.list if item.id == test_user_for_service.id)
        assert page_user.roles == [test_role_for_service.id]
        assert page_user.role_names == test_role_for_service.name

    @pytest.mark.asyncio
    async def test_get_page_with_search(self, db, test_user_for_service):
        """测试带搜索条件的分页查询"""
        # 按用户名搜索
        result = await user_service.get_page(
            page=1,
            page_size=10,
            search=test_user_for_service.username[:10]
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_status_filter(self, db, test_user_for_service):
        """测试按状态过滤"""
        result = await user_service.get_page(page=1, page_size=10, is_active=1)

        for user in result.list:
            assert user.is_active == 1

    @pytest.mark.asyncio
    async def test_get_page_with_dept_filter(self, db, test_user_for_service, test_dept_for_service):
        """测试按部门过滤"""
        result = await user_service.get_page(
            page=1,
            page_size=10,
            dept_id=test_dept_for_service.id
        )

        for user in result.list:
            assert user.dept_id == test_dept_for_service.id

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果"""
        result = await user_service.get_page(
            page=1,
            page_size=10,
            search="nonexistent_user_12345"
        )

        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_filters_by_current_user_dept_scope(self, db):
        """部门数据范围用户只能看到本部门用户。"""
        visible_dept = await Departments.create(name="可见部门", status=1, sort=1)
        hidden_dept = await Departments.create(name="隐藏部门", status=1, sort=2)
        permission = await Permissions.create(name="system:users:query", type="BUTTON", perm="system:users:query")
        role = await Roles.create(
            name="用户数据范围角色",
            code="user_scope_role",
            status=1,
            data_scope=Roles.DATA_SCOPE_DEPT,
        )
        await role.permissions.add(permission)
        scoped_user = await Users.create(
            username="scoped_user",
            password="admin123",
            name="范围用户",
            dept_id=visible_dept.id,
            is_active=1,
        )
        await scoped_user.roles.add(role)
        visible_user = await Users.create(
            username="visible_scope_user",
            password="admin123",
            name="可见用户",
            dept_id=visible_dept.id,
            is_active=1,
        )
        hidden_user = await Users.create(
            username="hidden_scope_user",
            password="admin123",
            name="隐藏用户",
            dept_id=hidden_dept.id,
            is_active=1,
        )

        result = await user_service.get_page(
            page=1,
            page_size=20,
            current_user=scoped_user,
        )

        usernames = {user.username for user in result.list}
        assert visible_user.username in usernames
        assert hidden_user.username not in usernames


class TestUserServiceGet:
    """测试获取用户详情"""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, db, test_user_for_service):
        """测试获取存在的用户"""
        result = await user_service.get(test_user_for_service.id)

        assert result.id == test_user_for_service.id
        assert result.username == test_user_for_service.username
        assert result.name == test_user_for_service.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db):
        """测试获取不存在的用户"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.get(99999)

        assert "用户不存在" in str(exc_info.value)


class TestUserServiceGetForm:
    """测试获取用户表单详情"""

    @pytest.mark.asyncio
    async def test_get_form_existing_user(self, db, test_user_for_service):
        """测试获取存在的用户表单"""
        result = await user_service.get_form(test_user_for_service.id)

        assert result.id == test_user_for_service.id
        assert result.username == test_user_for_service.username
        assert hasattr(result, 'roles')

    @pytest.mark.asyncio
    async def test_get_form_includes_role_ids_and_names(self, db, test_user_for_service, test_role_for_service):
        """用户表单输出必须同时包含角色 ID 和角色名称。"""
        await test_user_for_service.roles.add(test_role_for_service)

        result = await user_service.get_form(test_user_for_service.id)

        assert result.roles == [test_role_for_service.id]
        assert result.role_names == test_role_for_service.name

    @pytest.mark.asyncio
    async def test_get_form_nonexistent_user(self, db):
        """测试获取不存在的用户表单"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.get_form(99999)

        assert "用户不存在" in str(exc_info.value)
