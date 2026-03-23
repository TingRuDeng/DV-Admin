"""
日志服务层测试
测试 LogService 的所有方法，包括分页查询、访问趋势、访问统计、删除等操作
"""
import uuid
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.db.models.system import OperationLog
from app.services.system.log_service import log_service


@pytest_asyncio.fixture
async def test_logs(db):
    """创建测试日志数据"""
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
            request_body='{}',
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
    """创建带不同日期的测试日志"""
    logs = []
    now = datetime.now()
    for i in range(7):
        log = await OperationLog.create(
            user_id=1,
            username=f"user_day_{i}",
            name=f"用户{i}",
            operation=f"操作{i}",
            method="GET",
            path=f"/api/v1/day/{i}",
            status=1,
            execution_time=50,
            created_at=now - timedelta(days=i),
        )
        logs.append(log)
    return logs


class TestLogServiceGetPage:
    """测试日志分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_logs):
        """测试基本分页查询"""
        result = await log_service.get_page(page=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_username(self, db, test_logs):
        """测试按用户名过滤"""
        result = await log_service.get_page(page=1, page_size=10, username="test_user_0")
        assert result.total >= 1
        for log in result.list:
            assert "test_user_0" in log.username

    @pytest.mark.asyncio
    async def test_get_page_with_operation(self, db, test_logs):
        """测试按操作描述过滤"""
        result = await log_service.get_page(page=1, page_size=10, operation="测试操作")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_method(self, db, test_logs):
        """测试按请求方法过滤"""
        result = await log_service.get_page(page=1, page_size=10, method="GET")
        assert result.total >= 1
        for log in result.list:
            assert log.method == "GET"

    @pytest.mark.asyncio
    async def test_get_page_with_method_lowercase(self, db, test_logs):
        """测试请求方法小写转换"""
        result = await log_service.get_page(page=1, page_size=10, method="get")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_status(self, db, test_logs):
        """测试按状态过滤"""
        result = await log_service.get_page(page=1, page_size=10, status=1)
        assert result.total >= 1
        for log in result.list:
            assert log.status == 1

    @pytest.mark.asyncio
    async def test_get_page_with_time_range(self, db, test_logs):
        """测试按时间范围过滤"""
        now = datetime.now()
        result = await log_service.get_page(
            page=1, page_size=10,
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=1),
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果"""
        result = await log_service.get_page(page=1, page_size=10, username="nonexistent_user_xyz")
        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_pagination(self, db):
        """测试分页功能"""
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


class TestLogServiceGetVisitTrend:
    """测试访问趋势统计"""

    @pytest.mark.asyncio
    async def test_get_visit_trend_basic(self, db, test_logs_with_dates):
        """测试基本访问趋势"""
        result = await log_service.get_visit_trend()
        # 默认查询最近7天，包含今天
        assert len(result) >= 7
        for item in result:
            assert hasattr(item, 'date')
            assert hasattr(item, 'count')

    @pytest.mark.asyncio
    async def test_get_visit_trend_with_date_range(self, db, test_logs_with_dates):
        """测试指定日期范围的访问趋势"""
        now = datetime.now()
        result = await log_service.get_visit_trend(
            start_date=now - timedelta(days=3),
            end_date=now,
        )
        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_get_visit_trend_empty(self, db):
        """测试无数据时的访问趋势"""
        # 先清理所有日志
        await OperationLog.all().delete()
        now = datetime.now()
        result = await log_service.get_visit_trend(
            start_date=now - timedelta(days=2),
            end_date=now,
        )
        assert len(result) == 3
        for item in result:
            assert item.count == 0


class TestLogServiceGetVisitStats:
    """测试访问统计"""

    @pytest.mark.asyncio
    async def test_get_visit_stats_basic(self, db, test_logs):
        """测试基本访问统计"""
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
        """测试统计数据准确性"""
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
    async def test_get_visit_stats_empty(self, db):
        """测试无数据时的访问统计"""
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


class TestLogServiceDelete:
    """测试日志删除"""

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, db, test_logs):
        """测试批量删除日志"""
        log_ids = [log.id for log in test_logs[:3]]
        deleted_count = await log_service.delete_by_ids(log_ids)
        assert deleted_count == 3
        for log_id in log_ids:
            exists = await OperationLog.filter(id=log_id).exists()
            assert not exists

    @pytest.mark.asyncio
    async def test_delete_by_ids_empty(self, db):
        """测试空ID列表删除"""
        deleted_count = await log_service.delete_by_ids([])
        assert deleted_count == 0

    @pytest.mark.asyncio
    async def test_delete_by_ids_nonexistent(self, db):
        """测试删除不存在的日志"""
        deleted_count = await log_service.delete_by_ids([99999, 99998])
        assert deleted_count == 0

    @pytest.mark.asyncio
    async def test_clear_old_logs(self, db):
        """测试清理历史日志"""
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
    """测试创建日志"""

    @pytest.mark.asyncio
    async def test_create_log_basic(self, db):
        """测试基本创建日志"""
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
        """测试最小参数创建日志"""
        log = await log_service.create_log(username="minimal_user", operation="最小操作")
        assert log.id is not None
        assert log.username == "minimal_user"
        assert log.status == 1

    @pytest.mark.asyncio
    async def test_create_log_with_error(self, db):
        """测试创建错误日志"""
        log = await log_service.create_log(
            username="error_user",
            operation="错误操作",
            status=0,
            error_msg="操作失败：参数错误",
        )
        assert log.status == 0
        assert log.error_msg == "操作失败：参数错误"
