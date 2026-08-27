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


@pytest_asyncio.fixture
async def scoped_user_context(db):
    """创建部门数据范围操作人与可见/不可见用户。"""
    from app.db.models.oauth import Users
    from app.db.models.system import Departments, Roles

    visible_dept = await Departments.create(
        name=f"范围内部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    hidden_dept = await Departments.create(
        name=f"范围外部门_{uuid.uuid4().hex[:6]}",
        sort=2,
        status=1,
    )
    role = await Roles.create(
        name=f"部门范围角色_{uuid.uuid4().hex[:6]}",
        code=f"dept_scope_{uuid.uuid4().hex[:6]}",
        status=1,
        data_scope=Roles.DATA_SCOPE_DEPT,
    )
    operator = await Users.create(
        username=f"scope_operator_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="范围操作人",
        dept_id=visible_dept.id,
        is_active=1,
    )
    await operator.roles.add(role)
    visible_user = await Users.create(
        username=f"visible_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="范围内用户",
        dept_id=visible_dept.id,
        is_active=1,
    )
    hidden_user = await Users.create(
        username=f"hidden_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="范围外用户",
        dept_id=hidden_dept.id,
        is_active=1,
    )
    return {
        "operator": operator,
        "visible_dept": visible_dept,
        "hidden_dept": hidden_dept,
        "visible_user": visible_user,
        "hidden_user": hidden_user,
    }
