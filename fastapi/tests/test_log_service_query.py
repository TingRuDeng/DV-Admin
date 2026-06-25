"""
日志服务分页查询测试。
"""
import uuid
import warnings
from datetime import datetime, timedelta

import pytest

from app.db.models.system import OperationLog
from app.services.system.log_service import log_service

pytest_plugins = ["log_service_fixtures"]


class TestLogServiceGetPage:
    """测试日志分页查询。"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_logs):
        """测试基本分页查询。"""
        result = await log_service.get_page(page=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_username(self, db, test_logs):
        """测试按用户名过滤。"""
        result = await log_service.get_page(page=1, page_size=10, username="test_user_0")
        assert result.total >= 1
        for log in result.list:
            assert "test_user_0" in log.username

    @pytest.mark.asyncio
    async def test_get_page_with_operation(self, db, test_logs):
        """测试按操作描述过滤。"""
        result = await log_service.get_page(page=1, page_size=10, operation="测试操作")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_method(self, db, test_logs):
        """测试按请求方法过滤。"""
        result = await log_service.get_page(page=1, page_size=10, method="GET")
        assert result.total >= 1
        for log in result.list:
            assert log.method == "GET"

    @pytest.mark.asyncio
    async def test_get_page_with_method_lowercase(self, db, test_logs):
        """测试请求方法小写转换。"""
        result = await log_service.get_page(page=1, page_size=10, method="get")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_status(self, db, test_logs):
        """测试按状态过滤。"""
        result = await log_service.get_page(page=1, page_size=10, status=1)
        assert result.total >= 1
        for log in result.list:
            assert log.status == 1

    @pytest.mark.asyncio
    async def test_get_page_with_time_range(self, db, test_logs):
        """测试按时间范围过滤。"""
        now = datetime.now()
        with warnings.catch_warnings():
            warnings.filterwarnings("error", message=".*naive datetime.*")
            result = await log_service.get_page(
                page=1,
                page_size=10,
                start_time=now - timedelta(days=1),
                end_time=now + timedelta(days=1),
            )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果。"""
        result = await log_service.get_page(page=1, page_size=10, username="nonexistent_user_xyz")
        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_pagination(self, db):
        """测试分页功能。"""
        for i in range(15):
            await OperationLog.create(
                username=f"page_user_{i}_{uuid.uuid4().hex[:6]}",
                operation=f"分页操作{i}",
                method="GET",
                path=f"/api/page/{i}",
                status=1,
            )

        result1 = await log_service.get_page(page=1, page_size=10)
        assert len(result1.results) == 10

        result2 = await log_service.get_page(page=2, page_size=10)
        assert len(result2.results) >= 5
