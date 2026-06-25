"""
日志服务测试共享夹具。
"""
import uuid
from datetime import datetime, timedelta

import pytest_asyncio

from app.db.models.system import OperationLog


@pytest_asyncio.fixture
async def test_logs(db):
    """创建测试日志数据。"""
    logs = []
    for i in range(5):
        log = await OperationLog.create(
            user_id=1,
            username=f"test_user_{i}",
            name=f"测试用户{i}",
            operation=f"测试操作{i}",
            method="GET" if i % 2 == 0 else "POST",
            path=f"/api/v1/test/{i}",
            query_params='{"page": 1}',
            request_body="{}",
            response_status=200,
            response_body='{"code": 20000}',
            ip="127.0.0.1",
            browser="Chrome",
            os="Windows",
            execution_time=100 + i * 10,
            status=1 if i % 2 == 0 else 0,
            error_msg="" if i % 2 == 0 else "测试错误",
        )
        logs.append(log)
    return logs


@pytest_asyncio.fixture
async def test_logs_with_dates(db):
    """创建带不同日期的测试日志。"""
    logs = []
    now = datetime.now()
    for i in range(7):
        log = await OperationLog.create(
            user_id=1,
            username=f"user_day_{i}",
            name=f"用户{i}",
            operation=f"操作{i}",
            method="GET",
            path=f"/api/v1/day/{i}_{uuid.uuid4().hex[:6]}",
            status=1,
            execution_time=50,
            created_at=now - timedelta(days=i),
        )
        logs.append(log)
    return logs
