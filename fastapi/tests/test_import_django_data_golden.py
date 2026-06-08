import json

import pytest

from app.db import import_django_data
from app.db.models.oauth import Users
from app.db.models.system import Departments, DictData, DictItems, Permissions, Roles

GOLDEN_FIXTURE_ROWS = [
    {
        "model": "system.departments",
        "pk": 1,
        "fields": {"name": "总部", "status": 1, "sort": 1, "parent": None},
    },
    {
        "model": "system.departments",
        "pk": 2,
        "fields": {"name": "研发部", "status": 1, "sort": 2, "parent": 1},
    },
    {
        "model": "system.permissions",
        "pk": 10,
        "fields": {
            "name": "系统管理",
            "type": "CATALOG",
            "route_name": "System",
            "route_path": "/system",
            "component": "Layout",
            "sort": 1,
            "visible": 1,
            "parent": None,
            "perm": "system:catalog",
        },
    },
    {
        "model": "system.permissions",
        "pk": 11,
        "fields": {
            "name": "用户管理",
            "type": "MENU",
            "route_name": "UserManagement",
            "route_path": "/system/users",
            "component": "system/users/index",
            "sort": 2,
            "visible": 1,
            "parent": 10,
            "perm": "system:users:query",
        },
    },
    {
        "model": "system.dicts",
        "pk": 30,
        "fields": {"name": "状态", "dict_code": "status", "status": 1, "remark": "状态字典"},
    },
    {
        "model": "system.dictitems",
        "pk": 31,
        "fields": {"label": "启用", "value": "1", "sort": 1, "status": 1, "dict": 30},
    },
    {
        "model": "system.roles",
        "pk": 20,
        "fields": {
            "name": "管理员",
            "code": "admin",
            "status": 1,
            "sort": 1,
            "permissions": [10, 11],
        },
    },
    {
        "model": "system.users",
        "pk": 40,
        "fields": {
            "username": "admin",
            "password": "pbkdf2_sha256$test",
            "name": "管理员",
            "email": "admin@example.com",
            "mobile": "13800138000",
            "is_active": True,
            "dept": 2,
            "roles": [20],
        },
    },
]


def write_fixture(tmp_path, rows: list[dict]) -> None:
    """写入 golden fixture，模拟 Django dumpdata 的最小稳定输出。"""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    (backend_dir / "init_data.json").write_text(json.dumps(rows), encoding="utf-8")


async def assert_department_records() -> None:
    """校验部门自关联导入结果。"""
    assert await Departments.all().count() == 2
    parent = await Departments.get(id=1)
    child = await Departments.get(id=2)
    assert parent.name == "总部"
    assert child.parent_id == parent.id


async def assert_permission_records() -> None:
    """校验权限菜单自关联和组件字段导入结果。"""
    assert await Permissions.all().count() == 2
    catalog = await Permissions.get(id=10)
    menu = await Permissions.get(id=11)
    assert catalog.component == "Layout"
    assert menu.parent_id == catalog.id
    assert menu.component == "system/users/index"


async def assert_dict_records() -> None:
    """校验字典字段映射和字典项外键导入结果。"""
    dict_data = await DictData.get(id=30)
    dict_item = await DictItems.get(id=31)
    assert dict_data.code == "status"
    assert dict_data.desc == "状态字典"
    assert dict_item.dict_data_id == dict_data.id


async def assert_role_and_user_records() -> None:
    """校验角色权限和用户角色 M2M 关系导入结果。"""
    role = await Roles.get(id=20)
    user = await Users.get(id=40)
    role_permissions = await role.permissions.all()
    user_roles = await user.roles.all()
    assert {permission.id for permission in role_permissions} == {10, 11}
    assert {user_role.id for user_role in user_roles} == {20}
    assert user.dept_id == 2
    assert user.is_active == 1


@pytest.mark.asyncio
async def test_import_data_matches_golden_fixture_contract(db, tmp_path, monkeypatch):
    """小型 Django fixture 导入后必须保持字段、外键和 M2M 关系完整。"""
    monkeypatch.setattr(import_django_data, "project_root", str(tmp_path))
    write_fixture(tmp_path, GOLDEN_FIXTURE_ROWS)

    await import_django_data.import_data()

    await assert_department_records()
    await assert_permission_records()
    await assert_dict_records()
    await assert_role_and_user_records()
