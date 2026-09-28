"""运行时分页契约测试夹具。"""

from __future__ import annotations

import uuid

import pytest_asyncio

from app.db.models.oauth import Users
from app.db.models.system import Notices


@pytest_asyncio.fixture
async def runtime_contract_page_samples(db):
    """创建分页行为测试样本，用唯一搜索条件隔离本轮数据。"""
    suffix = uuid.uuid4().hex[:6]
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
        "notice_suffix": notice_suffix,
        "users": users,
        "notices": notices,
    }
