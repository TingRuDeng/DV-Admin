"""
操作日志 Service
"""
from datetime import datetime, timedelta
from typing import Any

from app.db.models.system import OperationLog
from app.schemas.system import OperationLogPageResult, VisitStatsOut, VisitTrendOut
from app.services.system.log_serializers import operation_log_to_out
from app.services.system.log_stats_helpers import (
    build_visit_trend,
    calculate_avg_execution_time,
    count_top_paths,
    count_top_users,
)
from app.services.system.log_time import local_now, normalize_local_time


class LogService:
    """操作日志服务"""

    async def get_page(
        self,
        page: int,
        page_size: int,
        username: str | None = None,
        operation: str | None = None,
        method: str | None = None,
        status: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> OperationLogPageResult:
        """获取操作日志分页列表"""
        query = OperationLog.all()

        # 构建过滤条件
        if username:
            query = query.filter(username__icontains=username)
        if operation:
            query = query.filter(operation__icontains=operation)
        if method:
            query = query.filter(method=method.upper())
        if status is not None:
            query = query.filter(status=status)
        if start_time:
            query = query.filter(created_at__gte=normalize_local_time(start_time))
        if end_time:
            query = query.filter(created_at__lte=normalize_local_time(end_time))

        # 查询总数
        total = await query.count()

        # 分页查询
        logs = (
            await query.order_by("-created_at")
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # 转换为输出模型
        results = [operation_log_to_out(log) for log in logs]

        return OperationLogPageResult(list=results, total=total)

    async def get_visit_trend(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[VisitTrendOut]:
        """获取访问趋势统计"""
        if not start_date:
            start_date = local_now() - timedelta(days=7)
        else:
            start_date = normalize_local_time(start_date)
        if not end_date:
            end_date = local_now()
        else:
            end_date = normalize_local_time(end_date)

        # 按日期分组统计
        logs = await OperationLog.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).all()

        return build_visit_trend(logs, start_date, end_date)

    async def get_visit_stats(self) -> VisitStatsOut:
        """获取访问统计"""
        now = local_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        # 总访问次数
        total_count = await OperationLog.all().count()

        # 今日访问次数
        today_count = await OperationLog.filter(
            created_at__gte=today_start
        ).count()

        # 本周访问次数
        week_count = await OperationLog.filter(
            created_at__gte=week_start
        ).count()

        # 本月访问次数
        month_count = await OperationLog.filter(
            created_at__gte=month_start
        ).count()

        # 成功/失败次数
        success_count = await OperationLog.filter(status=1).count()
        fail_count = await OperationLog.filter(status=0).count()

        # 平均执行时间
        logs = await OperationLog.filter(execution_time__gt=0).all()
        avg_execution_time = calculate_avg_execution_time(logs)

        # 活跃用户 TOP10
        top_users_data = await self._get_top_users(limit=10)

        # 热门路径 TOP10
        top_paths_data = await self._get_top_paths(limit=10)

        return VisitStatsOut(
            total_count=total_count,
            today_count=today_count,
            week_count=week_count,
            month_count=month_count,
            success_count=success_count,
            fail_count=fail_count,
            avg_execution_time=avg_execution_time,
            top_users=top_users_data,
            top_paths=top_paths_data,
        )

    async def _get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取活跃用户 TOP N"""
        logs = await OperationLog.all().order_by("-created_at").limit(1000).all()

        # 统计用户访问次数
        return count_top_users(logs, limit)

    async def _get_top_paths(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取热门路径 TOP N"""
        logs = await OperationLog.all().order_by("-created_at").limit(1000).all()

        # 统计路径访问次数
        return count_top_paths(logs, limit)

    async def delete_by_ids(self, ids: list[int]) -> int:
        """批量删除日志"""
        deleted_count = await OperationLog.filter(id__in=ids).delete()
        return deleted_count

    async def clear_old_logs(self, days: int = 30) -> int:
        """清理指定天数之前的日志"""
        threshold = local_now() - timedelta(days=days)
        deleted_count = await OperationLog.filter(created_at__lt=threshold).delete()
        return deleted_count

    async def create_log(
        self,
        user_id: int | None = None,
        username: str = "",
        name: str = "",
        operation: str = "",
        method: str = "",
        path: str = "",
        query_params: str = "",
        request_body: str = "",
        response_status: int = 0,
        response_body: str = "",
        ip: str = "",
        browser: str = "",
        os: str = "",
        execution_time: int = 0,
        status: int = 1,
        error_msg: str = "",
    ) -> OperationLog:
        """创建操作日志"""
        return await OperationLog.create(
            user_id=user_id,
            username=username,
            name=name,
            operation=operation,
            method=method,
            path=path,
            query_params=query_params,
            request_body=request_body,
            response_status=response_status,
            response_body=response_body,
            ip=ip,
            browser=browser,
            os=os,
            execution_time=execution_time,
            status=status,
            error_msg=error_msg,
        )


log_service = LogService()
