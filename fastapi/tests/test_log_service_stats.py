"""
日志服务访问统计测试。
"""
import pytest

from app.db.models.system import OperationLog
from app.services.system.log_service import log_service

pytest_plugins = ["log_service_fixtures"]


class TestLogServiceGetVisitStats:
    """测试访问统计。"""

    @pytest.mark.asyncio
    async def test_get_visit_stats_basic(self, db, test_logs):
        """测试基本访问统计。"""
        result = await log_service.get_visit_stats()
        assert result.total_count >= 5
        assert result.today_count >= 0
        assert result.week_count >= 0
        assert result.month_count >= 0
        assert result.success_count >= 0
        assert result.fail_count >= 0
        assert result.avg_execution_time >= 0
        assert isinstance(result.top_users, list)
        assert isinstance(result.top_paths, list)

    @pytest.mark.asyncio
    async def test_get_visit_stats_counts(self, db):
        """测试统计数据准确性。"""
        await OperationLog.all().delete()
        for i in range(3):
            await OperationLog.create(
                username=f"stats_user_{i}",
                operation=f"统计操作{i}",
                method="GET",
                path=f"/api/stats/{i}",
                status=1,
                execution_time=100,
            )
        for i in range(2):
            await OperationLog.create(
                username=f"stats_user_fail_{i}",
                operation=f"失败操作{i}",
                method="POST",
                path=f"/api/stats/fail/{i}",
                status=0,
                execution_time=50,
            )

        result = await log_service.get_visit_stats()

        assert result.total_count == 5
        assert result.success_count == 3
        assert result.fail_count == 2

    @pytest.mark.asyncio
    async def test_get_visit_stats_top_users_and_paths_cover_all_logs(self, db):
        """Top 统计应覆盖全量日志，不能只统计最近 1000 条。"""
        await OperationLog.all().delete()

        for _ in range(20):
            await OperationLog.create(
                username="历史高频用户",
                operation="历史操作",
                method="GET",
                path="/api/history/hot",
                status=1,
                execution_time=20,
            )
        for i in range(1000):
            await OperationLog.create(
                username=f"recent_user_{i}",
                operation="近期操作",
                method="GET",
                path=f"/api/recent/{i}",
                status=1,
                execution_time=10,
            )

        result = await log_service.get_visit_stats()

        assert result.total_count == 1020
        assert result.top_users[0]["username"] == "历史高频用户"
        assert result.top_users[0]["count"] == 20
        assert result.top_paths[0]["path"] == "/api/history/hot"
        assert result.top_paths[0]["count"] == 20

    @pytest.mark.asyncio
    async def test_get_visit_stats_empty(self, db):
        """测试无数据时的访问统计。"""
        await OperationLog.all().delete()
        result = await log_service.get_visit_stats()
        assert result.total_count == 0
        assert result.today_count == 0
        assert result.week_count == 0
        assert result.month_count == 0
        assert result.success_count == 0
        assert result.fail_count == 0
        assert result.avg_execution_time == 0.0
        assert result.top_users == []
        assert result.top_paths == []
