"""
角色服务查询测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound
from app.services.system.role_service import role_service

pytest_plugins = ["role_service_fixtures"]


class TestRoleServiceGetPage:
    """测试角色分页查询。"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_role_for_service):
        """测试基本分页查询。"""
        result = await role_service.get_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_page_includes_permissions(self, db, test_role_for_service, test_permission_for_service):
        """角色分页输出必须包含权限 ID 列表。"""
        await test_role_for_service.permissions.add(test_permission_for_service)

        result = await role_service.get_page(
            page=1,
            page_size=10,
            search=test_role_for_service.name,
        )

        page_role = next(item for item in result.list if item.id == test_role_for_service.id)
        assert page_role.permissions == [test_permission_for_service.id]

    @pytest.mark.asyncio
    async def test_get_page_with_search(self, db, test_role_for_service):
        """测试带搜索条件的分页查询。"""
        result = await role_service.get_page(
            page=1,
            page_size=10,
            search=test_role_for_service.name[:10],
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果。"""
        result = await role_service.get_page(
            page=1,
            page_size=10,
            search="nonexistent_role_12345",
        )

        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_pagination(self, db):
        """测试分页功能。"""
        from app.db.models.system import Roles

        for i in range(15):
            await Roles.create(
                name=f"分页角色_{i}_{uuid.uuid4().hex[:6]}",
                code=f"page_role_{i}_{uuid.uuid4().hex[:6]}",
                status=1,
                sort=i,
            )

        result1 = await role_service.get_page(page=1, page_size=10)
        assert len(result1.results) == 10

        result2 = await role_service.get_page(page=2, page_size=10)
        assert len(result2.results) >= 5


class TestRoleServiceGet:
    """测试获取角色详情。"""

    @pytest.mark.asyncio
    async def test_get_existing_role(self, db, test_role_for_service):
        """测试获取存在的角色。"""
        result = await role_service.get(test_role_for_service.id)

        assert result.id == test_role_for_service.id
        assert result.name == test_role_for_service.name
        assert result.code == test_role_for_service.code

    @pytest.mark.asyncio
    async def test_get_nonexistent_role(self, db):
        """测试获取不存在的角色。"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.get(99999)

        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_role_with_permissions(self, db, test_role_for_service, test_permission_for_service):
        """测试获取带权限的角色。"""
        await test_role_for_service.permissions.add(test_permission_for_service)

        result = await role_service.get(test_role_for_service.id)

        assert result.id == test_role_for_service.id
        assert hasattr(result, "permissions")
        assert test_permission_for_service.id in result.permissions


class TestRoleServiceGetOptions:
    """测试获取角色选项。"""

    @pytest.mark.asyncio
    async def test_get_options(self, db, test_role_for_service):
        """测试获取角色下拉选项。"""
        result = await role_service.get_options()

        assert isinstance(result, list)
        assert len(result) >= 1

        for option in result:
            assert "id" in option
            assert "label" in option

    @pytest.mark.asyncio
    async def test_get_options_only_active(self, db):
        """测试只返回激活状态的角色。"""
        from app.db.models.system import Roles

        inactive_role = await Roles.create(
            name=f"禁用角色_{uuid.uuid4().hex[:8]}",
            code=f"inactive_role_{uuid.uuid4().hex[:8]}",
            status=0,
            sort=1,
        )

        result = await role_service.get_options()

        option_ids = [opt["id"] for opt in result]
        assert inactive_role.id not in option_ids
