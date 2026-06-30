"""Pytest 配置和领域数据 fixtures。"""

import sys
import uuid
from pathlib import Path

import pytest
import pytest_asyncio

ROOT_DIR = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

pytest_plugins = [
    "fixtures.database",
    "fixtures.client",
    "runtime_api_contracts.pagination_fixtures",
]


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def test_permissions(db):
    """创建测试权限/菜单"""
    from fixtures.permissions import create_test_permissions

    return await create_test_permissions()


@pytest_asyncio.fixture(scope="function")
async def test_role(db, test_permissions):
    """创建测试角色（带权限）"""
    import uuid

    from app.db.models.system import Roles
    role_name = f"超级管理员_{uuid.uuid4().hex[:6]}"

    role = await Roles.create(
        name=role_name,
        code="admin",
        status=1,
        sort=1,
        remark="测试角色",
    )

    from fixtures.permissions import role_permission_instances

    # 角色绑定顺序由权限夹具统一维护，避免新增权限时遗漏。
    permissions = role_permission_instances(test_permissions)
    await role.permissions.add(*permissions)

    return {"id": role.id, "name": role.name, "code": role.code}


@pytest_asyncio.fixture(scope="function")
async def test_dept(db):
    """创建测试部门"""
    from app.db.models.system import Departments

    dept = await Departments.create(
        name="测试公司",
        sort=1,
        status=1,
        leader="管理员",
        phone="13800138000",
    )
    return {"id": dept.id, "name": dept.name}


@pytest_asyncio.fixture(scope="function")
async def test_user_with_role(db, test_role, test_dept):
    """创建测试用户（带角色和部门）"""
    from passlib.context import CryptContext

    from app.db.models.oauth import Users
    from app.db.models.system import Roles

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("admin123")

    # 使用唯一手机号
    unique_mobile = f"1380013{str(uuid.uuid4())[:4]}"

    user = await Users.create(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password=hashed_password,
        name="管理员",
        is_active=1,
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        mobile=unique_mobile,
        dept_id=test_dept["id"],
    )

    # 关联角色 - 需要传递角色实例
    role = await Roles.get(id=test_role["id"])
    await user.roles.add(role)

    return {
        "id": user.id,
        "username": user.username,
        "password": "admin123",
        "name": user.name,
    }


@pytest_asyncio.fixture(scope="function")
async def test_user(db) -> dict:
    """创建测试用户（每个测试使用唯一的手机号）"""
    from passlib.context import CryptContext

    from app.db.models.oauth import Users

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("admin123")

    # 使用唯一手机号
    unique_mobile = f"1380013{str(uuid.uuid4())[:4]}"

    user = await Users.create(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password=hashed_password,
        name="管理员",
        is_active=1,
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        mobile=unique_mobile,
    )

    return {
        "id": user.id,
        "username": user.username,
        "password": "admin123",
        "name": user.name,
    }
