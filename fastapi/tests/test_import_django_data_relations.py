"""
Django 数据导入关系测试

覆盖导入目标模型的外键、多对多和自引用关系。
"""

import uuid

import pytest

from app.db.models.system import Departments, Permissions, Roles


@pytest.mark.asyncio
async def test_import_permissions(db):
    """权限模型应支持菜单父子关系。"""
    catalog = await Permissions.create(
        name=f"系统管理_{uuid.uuid4().hex[:6]}",
        type="CATALOG",
        sort=1,
    )
    menu = await Permissions.create(
        name=f"用户管理_{uuid.uuid4().hex[:6]}",
        type="MENU",
        route_name="UserManagement",
        route_path="/system/users",
        component="system/user/index",
        sort=1,
        parent_id=catalog.id,
        perm="system:users:query",
    )

    assert catalog.id is not None
    assert menu.id is not None
    assert menu.parent_id == catalog.id


@pytest.mark.asyncio
async def test_import_with_m2m_relationships(db):
    """角色权限多对多关系应可写入并读取。"""
    perm1 = await Permissions.create(
        name=f"权限1_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm1_{uuid.uuid4().hex[:6]}",
    )
    perm2 = await Permissions.create(
        name=f"权限2_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm2_{uuid.uuid4().hex[:6]}",
    )
    role = await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
    )

    await role.permissions.add(perm1, perm2)

    role_perms = await role.permissions.all()
    assert len(role_perms) == 2


@pytest.mark.asyncio
async def test_import_with_fk_relationships(db):
    """部门父子外键关系应可写入。"""
    parent_dept = await Departments.create(
        name=f"父部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    child_dept = await Departments.create(
        name=f"子部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
        parent_id=parent_dept.id,
    )

    assert child_dept.parent_id == parent_dept.id


@pytest.mark.asyncio
async def test_import_self_referencing_fk(db):
    """权限自引用父子关系应可写入。"""
    parent_perm = await Permissions.create(
        name=f"父权限_{uuid.uuid4().hex[:6]}",
        type="MENU",
        sort=1,
    )
    child_perm = await Permissions.create(
        name=f"子权限_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        parent_id=parent_perm.id,
        perm=f"test:child_{uuid.uuid4().hex[:6]}",
    )

    assert child_perm.parent_id == parent_perm.id
