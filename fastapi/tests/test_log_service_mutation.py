"""
日志服务删除与创建测试。
"""
from datetime import datetime, timedelta

import pytest

from app.db.models.system import OperationLog
from app.services.system.log_service import log_service

pytest_plugins = ["log_service_fixtures"]


class TestLogServiceDelete:
    """测试日志删除。"""

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, db, test_logs):
        """测试批量删除日志。"""
        log_ids = [log.id for log in test_logs[:3]]
        deleted_count = await log_service.delete_by_ids(log_ids)
        assert deleted_count == 3
        for log_id in log_ids:
            exists = await OperationLog.filter(id=log_id).exists()
            assert not exists

    @pytest.mark.asyncio
    async def test_delete_by_ids_empty(self, db):
        """测试空 ID 列表删除。"""
        deleted_count = await log_service.delete_by_ids([])
        assert deleted_count == 0

    @pytest.mark.asyncio
    async def test_delete_by_ids_nonexistent(self, db):
        """测试删除不存在的日志。"""
        deleted_count = await log_service.delete_by_ids([99999, 99998])
        assert deleted_count == 0

    @pytest.mark.asyncio
    async def test_clear_old_logs(self, db):
        """测试清理历史日志。"""
        new_log = await OperationLog.create(
            username="new_user",
            operation="新操作",
            method="GET",
            path="/api/new",
            status=1,
        )
        old_date = datetime.now() - timedelta(days=31)
        old_log = await OperationLog.create(
            username="old_user",
            operation="旧操作",
            method="GET",
            path="/api/old",
            status=1,
            created_at=old_date,
        )

        deleted_count = await log_service.clear_old_logs(days=30)

        assert deleted_count >= 1
        new_exists = await OperationLog.filter(id=new_log.id).exists()
        assert new_exists
        old_exists = await OperationLog.filter(id=old_log.id).exists()
        assert not old_exists


class TestLogServiceCreate:
    """测试创建日志。"""

    @pytest.mark.asyncio
    async def test_create_log_basic(self, db):
        """测试基本创建日志。"""
        log = await log_service.create_log(
            user_id=1,
            username="create_user",
            name="创建用户",
            operation="创建操作",
            method="POST",
            path="/api/create",
            query_params='{"test": 1}',
            request_body='{"data": "test"}',
            response_status=200,
            response_body='{"code": 20000}',
            ip="192.168.1.1",
            browser="Firefox",
            os="Linux",
            execution_time=150,
            status=1,
            error_msg="",
        )
        assert log.id is not None
        assert log.username == "create_user"
        assert log.operation == "创建操作"

    @pytest.mark.asyncio
    async def test_create_log_minimal(self, db):
        """测试最小参数创建日志。"""
        log = await log_service.create_log(username="minimal_user", operation="最小操作")
        assert log.id is not None
        assert log.username == "minimal_user"
        assert log.status == 1

    @pytest.mark.asyncio
    async def test_create_log_with_error(self, db):
        """测试创建错误日志。"""
        log = await log_service.create_log(
            username="error_user",
            operation="错误操作",
            status=0,
            error_msg="操作失败：参数错误",
        )
        assert log.status == 0
        assert log.error_msg == "操作失败：参数错误"
