"""
日志服务访问趋势测试。
"""
from datetime import datetime, timedelta

import pytest
from tortoise.queryset import QuerySet

from app.core.exceptions import ValidationError
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

    @pytest.mark.asyncio
    async def test_get_visit_trend_filters_by_data_scope(self, db, scoped_log_context):
        """趋势计数不得包含范围外日志。"""
        await OperationLog.exclude(
            id__in=[
                scoped_log_context["visible_log"].id,
                scoped_log_context["hidden_log"].id,
            ]
        ).delete()

        result = await log_service.get_visit_trend(
            current_user=scoped_log_context["operator"],
        )

        assert sum(item.count for item in result) == 1

    @pytest.mark.asyncio
    async def test_get_visit_trend_does_not_materialize_log_rows(
        self,
        db,
        test_logs_with_dates,
        monkeypatch,
    ):
        """趋势统计必须使用聚合查询，禁止回退到 QuerySet.all() 拉取日志实体。"""
        def fail_on_all(queryset):
            raise AssertionError("访问趋势不应拉取完整 OperationLog 行")

        monkeypatch.setattr(QuerySet, "all", fail_on_all)

        result = await log_service.get_visit_trend()

        assert result

    @pytest.mark.asyncio
    async def test_get_visit_trend_rejects_reversed_range(self, db):
        with pytest.raises(ValidationError):
            await log_service.get_visit_trend(
                start_date=datetime(2026, 1, 2),
                end_date=datetime(2026, 1, 1),
            )

    @pytest.mark.asyncio
    async def test_get_visit_trend_rejects_range_over_366_days(self, db):
        with pytest.raises(ValidationError):
            await log_service.get_visit_trend(
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2026, 1, 2),
            )

    @pytest.mark.asyncio
    async def test_get_visit_trend_accepts_exactly_366_days(self, db):
        result = await log_service.get_visit_trend(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2026, 1, 1),
        )

        assert len(result) == 366
