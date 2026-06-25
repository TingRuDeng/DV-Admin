"""
字典服务测试共享夹具
"""
import uuid

import pytest_asyncio


@pytest_asyncio.fixture
async def test_dict_data_for_service(db):
    """创建测试字典类型"""
    from app.db.models.system import DictData

    dict_data = await DictData.create(
        name=f"测试字典_{uuid.uuid4().hex[:6]}",
        dict_code=f"test_dict_{uuid.uuid4().hex[:6]}",
        status=1,
        remark="测试字典描述",
    )
    return dict_data


@pytest_asyncio.fixture
async def test_dict_item_for_service(db, test_dict_data_for_service):
    """创建测试字典项"""
    from app.db.models.system import DictItems

    item = await DictItems.create(
        label=f"测试项_{uuid.uuid4().hex[:6]}",
        value=f"test_value_{uuid.uuid4().hex[:6]}",
        status=1,
        dict_data_id=test_dict_data_for_service.id,
    )
    return item
