"""
日志服务测试共享夹具。
"""
import uuid
from datetime import datetime, timedelta

import pytest_asyncio

from app.db.models.oauth import Users
from app.db.models.system import Departments, OperationLog, Roles


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
            request_id=f"service-request-{i}",
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


@pytest_asyncio.fixture
async def scoped_log_context(db):
    """创建部门范围操作人与范围内外日志。"""
    visible_dept = await Departments.create(
        name=f"日志范围内部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    hidden_dept = await Departments.create(
        name=f"日志范围外部门_{uuid.uuid4().hex[:6]}",
        sort=2,
        status=1,
    )
    role = await Roles.create(
        name=f"日志部门范围角色_{uuid.uuid4().hex[:6]}",
        code=f"log_dept_scope_{uuid.uuid4().hex[:6]}",
        status=1,
        data_scope=Roles.DATA_SCOPE_DEPT,
    )
    operator = await Users.create(
        username=f"log_scope_operator_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="日志范围操作人",
        dept_id=visible_dept.id,
        is_active=1,
    )
    await operator.roles.add(role)
    visible_user = await Users.create(
        username=f"log_visible_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="日志范围内用户",
        dept_id=visible_dept.id,
        is_active=1,
    )
    hidden_user = await Users.create(
        username=f"log_hidden_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="日志范围外用户",
        dept_id=hidden_dept.id,
        is_active=1,
    )
    visible_log = await OperationLog.create(
        user_id=visible_user.id,
        username=visible_user.username,
        operation="范围内操作",
        method="POST",
        path="/api/visible",
        status=1,
        execution_time=100,
    )
    hidden_log = await OperationLog.create(
        user_id=hidden_user.id,
        username=hidden_user.username,
        operation="范围外操作",
        method="POST",
        path="/api/hidden",
        status=0,
        execution_time=300,
    )
    return {
        "operator": operator,
        "visible_log": visible_log,
        "hidden_log": hidden_log,
    }
