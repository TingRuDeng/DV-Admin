"""
部门服务层测试
测试 DeptService 的所有方法
"""
import uuid

import pytest
import pytest_asyncio

from app.core.exceptions import BusinessError, NotFound
from app.db.models.system import Departments
from app.schemas.system import DeptCreate, DeptUpdate
from app.services.system.dept_service import dept_service


@pytest_asyncio.fixture
async def test_depts_for_service(db):
    """创建测试部门"""
    # 创建父部门
    parent = await Departments.create(
        name=f"父部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )

    # 创建子部门
    children = []
    for i in range(3):
        child = await Departments.create(
            name=f"子部门_{i}_{uuid.uuid4().hex[:6]}",
            sort=i + 1,
            status=1,
            parent_id=parent.id,
        )
        children.append(child)

    return {"parent": parent, "children": children}


class TestDeptServiceGetTree:
    """测试获取部门树"""

    @pytest.mark.asyncio
    async def test_get_tree_basic(self, db, test_depts_for_service):
        """测试基本获取部门树"""
        result = await dept_service.get_tree()
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_tree_empty(self, db):
        """测试空部门树"""
        await Departments.all().delete()
        result = await dept_service.get_tree()
        assert len(result) == 0


class TestDeptServiceGetOptions:
    """测试获取部门选项"""

    @pytest.mark.asyncio
    async def test_get_options_basic(self, db, test_depts_for_service):
        """测试基本获取部门选项"""
        result = await dept_service.get_options()
        assert len(result) >= 1


class TestDeptServiceGet:
    """测试获取部门详情"""

    @pytest.mark.asyncio
    async def test_get_existing(self, db, test_depts_for_service):
        """测试获取存在的部门"""
        parent = test_depts_for_service["parent"]
        result = await dept_service.get(parent.id)
        assert result.id == parent.id
        assert result.name == parent.name

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db):
        """测试获取不存在的部门"""
        with pytest.raises(NotFound):
            await dept_service.get(99999)


class TestDeptServiceCreate:
    """测试创建部门"""

    @pytest.mark.asyncio
    async def test_create_basic(self, db):
        """测试基本创建部门"""
        dept_in = DeptCreate(
            name=f"新部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
        )
        result = await dept_service.create(dept_in)
        assert result.id is not None
        assert result.name == dept_in.name

    @pytest.mark.asyncio
    async def test_create_with_parent(self, db, test_depts_for_service):
        """测试创建子部门"""
        parent = test_depts_for_service["parent"]
        dept_in = DeptCreate(
            name=f"子部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
            parent_id=parent.id,
        )
        result = await dept_service.create(dept_in)
        assert result.parent_id == parent.id


class TestDeptServiceUpdate:
    """测试更新部门"""

    @pytest.mark.asyncio
    async def test_update_basic(self, db, test_depts_for_service):
        """测试基本更新部门"""
        parent = test_depts_for_service["parent"]
        dept_in = DeptUpdate(name=f"更新部门_{uuid.uuid4().hex[:6]}")
        result = await dept_service.update(parent.id, dept_in)
        assert result.name == dept_in.name

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db):
        """测试更新不存在的部门"""
        dept_in = DeptUpdate(name="更新部门")
        with pytest.raises(NotFound):
            await dept_service.update(99999, dept_in)

    @pytest.mark.asyncio
    async def test_update_self_parent(self, db, test_depts_for_service):
        """测试将部门设为自己的父部门"""
        parent = test_depts_for_service["parent"]
        dept_in = DeptUpdate(parent_id=parent.id)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await dept_service.update(parent.id, dept_in)


class TestDeptServiceDelete:
    """测试删除部门"""

    @pytest.mark.asyncio
    async def test_delete_basic(self, db):
        """测试删除部门"""
        dept = await Departments.create(
            name=f"待删除部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
        )
        await dept_service.delete(dept.id)
        exists = await Departments.filter(id=dept.id).exists()
        assert not exists

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db):
        """测试删除不存在的部门"""
        with pytest.raises(NotFound):
            await dept_service.delete(99999)

    @pytest.mark.asyncio
    async def test_delete_with_children(self, db, test_depts_for_service):
        """测试删除有子部门的部门"""
        parent = test_depts_for_service["parent"]
        with pytest.raises(BusinessError):
            await dept_service.delete(parent.id)


class TestDeptServiceBulkDelete:
    """测试批量删除部门"""

    @pytest.mark.asyncio
    async def test_bulk_delete(self, db):
        """测试批量删除部门"""
        depts = []
        for i in range(3):
            dept = await Departments.create(
                name=f"批量删除部门_{i}_{uuid.uuid4().hex[:6]}",
                sort=i,
                status=1,
            )
            depts.append(dept)

        ids = [d.id for d in depts]
        await dept_service.bulk_delete(ids)

        for dept_id in ids:
            exists = await Departments.filter(id=dept_id).exists()
            assert not exists
