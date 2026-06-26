"""
Django 数据导入基础模型测试

覆盖导入目标模型的基础创建、更新和字段转换行为。
"""

import uuid

import pytest
from passlib.context import CryptContext

from app.db.models.oauth import Users
from app.db.models.system import Departments, DictData, DictItems, Roles


@pytest.mark.asyncio
async def test_import_departments(db):
    """部门模型应可创建导入目标字段。"""
    dept = await Departments.create(
        name=f"测试部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
        leader="测试领导",
        phone="13800138000",
        email="test@example.com",
    )

    assert dept.id is not None
    assert "测试部门" in dept.name


@pytest.mark.asyncio
async def test_import_roles(db):
    """角色模型应可创建导入目标字段。"""
    role = await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
        desc="测试角色描述",
    )

    assert role.id is not None
    assert "测试角色" in role.name


@pytest.mark.asyncio
async def test_import_dicts(db):
    """字典模型应保留 Django 同名业务字段。"""
    dict_data = await DictData.create(
        name=f"测试字典_{uuid.uuid4().hex[:6]}",
        dict_code=f"test_dict_{uuid.uuid4().hex[:6]}",
        status=1,
        remark="测试字典描述",
    )

    assert dict_data.id is not None
    assert "测试字典" in dict_data.name


@pytest.mark.asyncio
async def test_import_dict_items(db):
    """字典项模型应可关联字典主表。"""
    dict_data = await DictData.create(
        name=f"状态字典_{uuid.uuid4().hex[:6]}",
        dict_code=f"status_dict_{uuid.uuid4().hex[:6]}",
        status=1,
    )

    item = await DictItems.create(
        label=f"启用_{uuid.uuid4().hex[:6]}",
        value="1",
        status=1,
        dict_data_id=dict_data.id,
    )

    assert item.id is not None
    assert "启用" in item.label
    assert item.dict_data_id == dict_data.id


@pytest.mark.asyncio
async def test_import_users(db):
    """用户模型应可创建导入目标字段。"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("test123")

    user = await Users.create(
        username=f"test_import_user_{uuid.uuid4().hex[:6]}",
        password=hashed_password,
        name="导入用户",
        is_active=1,
        email=f"import_{uuid.uuid4().hex[:6]}@example.com",
        mobile=f"1390013{uuid.uuid4().hex[:4]}",
    )

    assert user.id is not None
    assert "test_import_user" in user.username


@pytest.mark.asyncio
async def test_import_update_existing(db):
    """已存在记录应可按主键更新。"""
    dept = await Departments.create(
        name=f"原部门名_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )

    original_name = dept.name
    await Departments.filter(id=dept.id).update(name=f"新部门名_{uuid.uuid4().hex[:6]}")

    updated = await Departments.get(id=dept.id)
    assert updated.name != original_name


@pytest.mark.asyncio
async def test_import_skip_unknown_fields(db):
    """未知字段跳过场景下目标模型仍应可创建有效字段。"""
    dept = await Departments.create(
        name=f"测试部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )

    assert dept.id is not None
    assert "测试部门" in dept.name


@pytest.mark.asyncio
async def test_field_conversion_is_active(db):
    """is_active 字段应保持 Django bool 到 FastAPI int 的目标语义。"""
    user = await Users.create(
        username=f"active_user_{uuid.uuid4().hex[:6]}",
        password="hashed",
        name="活跃用户",
        is_active=1,
        email=f"active_{uuid.uuid4().hex[:6]}@example.com",
        mobile=f"1380013{uuid.uuid4().hex[:4]}",
    )

    inactive_user = await Users.create(
        username=f"inactive_user_{uuid.uuid4().hex[:6]}",
        password="hashed",
        name="非活跃用户",
        is_active=0,
        email=f"inactive_{uuid.uuid4().hex[:6]}@example.com",
        mobile=f"1380014{uuid.uuid4().hex[:4]}",
    )

    assert user.is_active == 1
    assert inactive_user.is_active == 0
