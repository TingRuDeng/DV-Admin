"""用户服务测试共享夹具。"""
import uuid

import pytest_asyncio


@pytest_asyncio.fixture
async def test_dept_for_service(db):
    """创建测试部门"""
    from app.db.models.system import Departments

    dept = await Departments.create(
        name=f"测试部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    return dept


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


@pytest_asyncio.fixture
async def test_user_for_service(db, test_dept_for_service):
    """创建测试用户"""
    from app.core.security import get_password_hash
    from app.db.models.oauth import Users

    user = await Users.create(
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        password=get_password_hash("test123"),
        name="测试用户",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        mobile=f"138{uuid.uuid4().hex[:8]}",
        is_active=1,
        dept_id=test_dept_for_service.id,
    )
    return user
