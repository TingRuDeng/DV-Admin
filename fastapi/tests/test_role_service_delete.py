"""
角色服务删除测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound
from app.services.system.role_service import role_service


class TestRoleServiceDelete:
    """测试删除角色。"""

    @pytest.mark.asyncio
    async def test_delete_role(self, db):
        """测试删除角色。"""
        from app.db.models.system import Roles

        role_to_delete = await Roles.create(
            name=f"待删除角色_{uuid.uuid4().hex[:8]}",
            code=f"del_role_{uuid.uuid4().hex[:8]}",
            status=1,
            sort=1,
        )

        await role_service.delete(role_to_delete.id)

        deleted_role = await Roles.get_or_none(id=role_to_delete.id)
        assert deleted_role is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, db):
        """测试删除不存在的角色。"""
        with pytest.raises(NotFound) as exc_info:
            await role_service.delete(99999)

        assert "角色不存在" in str(exc_info.value)


class TestRoleServiceBatchDelete:
    """测试批量删除角色。"""

    @pytest.mark.asyncio
    async def test_batch_delete_roles(self, db):
        """测试批量删除角色。"""
        from app.db.models.system import Roles

        role_ids = []
        for i in range(3):
            role = await Roles.create(
                name=f"批量角色_{i}_{uuid.uuid4().hex[:8]}",
                code=f"batch_role_{i}_{uuid.uuid4().hex[:8]}",
                status=1,
                sort=i,
            )
            role_ids.append(role.id)

        await role_service.batch_delete(role_ids)

        for role_id in role_ids:
            deleted_role = await Roles.get_or_none(id=role_id)
            assert deleted_role is None

    @pytest.mark.asyncio
    async def test_batch_delete_empty_list(self, db):
        """测试批量删除空列表。"""
        await role_service.batch_delete([])
