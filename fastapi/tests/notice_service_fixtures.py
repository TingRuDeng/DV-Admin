"""
通知服务测试共享夹具。
"""
import uuid
from datetime import datetime

import pytest_asyncio

from app.db.models.system import Notices


@pytest_asyncio.fixture
async def test_notices_for_service(db):
    """创建测试通知。"""
    notices = []
    for i in range(3):
        notice = await Notices.create(
            title=f"测试通知_{i}_{uuid.uuid4().hex[:6]}",
            content=f"通知内容_{i}",
            type=0,
            level="L",
            target_type=1,
            publisher_id=1,
            publisher_name="管理员",
            publish_status=0,
        )
        notices.append(notice)
    return notices


@pytest_asyncio.fixture
async def test_published_notice(db):
    """创建已发布的通知。"""
    return await Notices.create(
        title=f"已发布通知_{uuid.uuid4().hex[:6]}",
        content="已发布通知内容",
        type=0,
        level="H",
        target_type=1,
        publisher_id=1,
        publisher_name="管理员",
        publish_status=1,
        publish_time=datetime.now(),
    )
