"""运行时分页契约测试夹具。"""

from __future__ import annotations

import uuid

import pytest_asyncio

from app.db.models.oauth import Users
from app.db.models.system import DictData, DictItems, Notices


@pytest_asyncio.fixture
async def runtime_contract_page_samples(db):
    """创建分页行为测试样本，用唯一搜索条件隔离本轮数据。"""
    suffix = uuid.uuid4().hex[:6]
    dict_suffix = uuid.uuid4().hex[:6]
    users = []
    for index in range(2):
        user = await Users.create(
            username=f"runtime_page_user_{index}_{suffix}",
            password="runtime-password",
            name=f"运行时分页用户{index}_{suffix}",
            is_active=1,
            email=f"runtime_page_user_{index}_{suffix}@example.com",
            mobile=f"139{uuid.uuid4().hex[:8]}",
        )
        users.append(user)

    dicts = []
    for index in range(2):
        dict_data = await DictData.create(
            name=f"运行时分页字典{index}_{dict_suffix}",
            dict_code=f"runtime_page_dict_{index}_{dict_suffix}",
            status=1,
        )
        dicts.append(dict_data)

    dict_items = []
    item_dict = await DictData.create(
        name=f"运行时分页字典项_{suffix}",
        dict_code=f"runtime_page_items_{suffix}",
        status=1,
    )
    for index in range(2):
        item = await DictItems.create(
            label=f"运行时分页字典项{index}_{suffix}",
            value=f"runtime_page_item_{index}_{suffix}",
            status=1,
            dict_data_id=item_dict.id,
        )
        dict_items.append(item)

    notices = []
    notice_suffix = uuid.uuid4().hex[:6]
    for index in range(2):
        notice = await Notices.create(
            title=f"运行时分页通知{index}_{notice_suffix}",
            content=f"运行时分页通知内容{index}",
            type=1,
            level="L",
            target_type=1,
            publisher_id=1,
            publisher_name="运行时管理员",
        )
        notices.append(notice)

    return {
        "suffix": suffix,
        "dict_suffix": dict_suffix,
        "notice_suffix": notice_suffix,
        "users": users,
        "dicts": dicts,
        "dict_items": dict_items,
        "notices": notices,
        "item_dict_code": item_dict.dict_code,
    }
