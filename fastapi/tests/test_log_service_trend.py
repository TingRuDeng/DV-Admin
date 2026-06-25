"""
日志服务访问趋势测试。
"""
from datetime import datetime, timedelta

import pytest

from app.db.models.system import OperationLog
from app.services.system.log_service import log_service

pytest_plugins = ["log_service_fixtures"]


class TestLogServiceGetVisitTrend:
    """测试访问趋势统计。"""

    @pytest.mark.asyncio
    async def test_get_visit_trend_basic(self, db, test_logs_with_dates):
        """测试基本访问趋势。"""
        result = await log_service.get_visit_trend()

        assert len(result) >= 7
        for item in result:
            assert hasattr(item, "date")
            assert hasattr(item, "count")

    @pytest.mark.asyncio
    async def test_get_visit_trend_with_date_range(self, db, test_logs_with_dates):
        """测试指定日期范围的访问趋势。"""
        now = datetime.now()
        result = await log_service.get_visit_trend(
            start_date=now - timedelta(days=3),
            end_date=now,
        )
        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_get_visit_trend_empty(self, db):
        """测试无数据时的访问趋势。"""
        await OperationLog.all().delete()
        now = datetime.now()
        result = await log_service.get_visit_trend(
            start_date=now - timedelta(days=2),
            end_date=now,
        )
        assert len(result) == 3
        for item in result:
            assert item.count == 0
