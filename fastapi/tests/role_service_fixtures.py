"""
角色服务测试共享夹具。
"""
import uuid

import pytest_asyncio


@pytest_asyncio.fixture
async def test_permission_for_service(db):
    """创建测试权限。"""
    from app.db.models.system import Permissions

    return await Permissions.create(
        name=f"测试权限_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm:{uuid.uuid4().hex[:6]}",
    )


@pytest_asyncio.fixture
async def test_role_for_service(db):
    """创建测试角色。"""
    from app.db.models.system import Roles

    return await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
    )
