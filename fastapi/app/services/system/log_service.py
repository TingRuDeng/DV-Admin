# -*- coding: utf-8 -*-
"""
操作日志 Service
"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.db.models.system import OperationLog
from app.schemas.system import (
    OperationLogOut,
    OperationLogPageResult,
    VisitStatsOut,
    VisitTrendOut,
)


class LogService:
    """操作日志服务"""

    async def get_page(
        self,
        page: int,
        page_size: int,
        username: Optional[str] = None,
        operation: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
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
            query = query.filter(created_at__gte=start_time)
        if end_time:
            query = query.filter(created_at__lte=end_time)

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
        results = [
            OperationLogOut(
                id=log.id,
                user_id=log.user_id,
                username=log.username,
                name=log.name,
                operation=log.operation,
                method=log.method,
                path=log.path,
                query_params=log.query_params,
                request_body=log.request_body,
                response_status=log.response_status,
                response_body=log.response_body,
                ip=log.ip,
                browser=log.browser,
                os=log.os,
                execution_time=log.execution_time,
                status=log.status,
                error_msg=log.error_msg,
                created_at=log.created_at,
                updated_at=log.updated_at,
            )
            for log in logs
        ]

        return OperationLogPageResult(results=results, count=total)

    async def get_visit_trend(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[VisitTrendOut]:
        """获取访问趋势统计"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        # 按日期分组统计
        logs = await OperationLog.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).all()

        # 按日期统计
        date_count: Dict[str, int] = {}
        for log in logs:
            date_str = log.created_at.strftime("%Y-%m-%d")
            date_count[date_str] = date_count.get(date_str, 0) + 1

        # 生成日期范围内的所有日期
        result = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        while current_date <= end_date_only:
            date_str = current_date.strftime("%Y-%m-%d")
            result.append(
                VisitTrendOut(
                    date=date_str,
                    count=date_count.get(date_str, 0),
                )
            )
            current_date += timedelta(days=1)

        return result

    async def get_visit_stats(self) -> VisitStatsOut:
        """获取访问统计"""
        now = datetime.now()
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
        avg_execution_time = 0.0
        if logs:
            total_time = sum(log.execution_time for log in logs)
            avg_execution_time = round(total_time / len(logs), 2)

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

    async def _get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取活跃用户 TOP N"""
        logs = await OperationLog.all().order_by("-created_at").limit(1000).all()

        # 统计用户访问次数
        user_count: Dict[str, Dict[str, Any]] = {}
        for log in logs:
            if log.username:
                if log.username not in user_count:
                    user_count[log.username] = {
                        "username": log.username,
                        "name": log.name,
                        "count": 0,
                    }
                user_count[log.username]["count"] += 1

        # 排序并取前 N 个
        sorted_users = sorted(
            user_count.values(), key=lambda x: x["count"], reverse=True
        )
        return sorted_users[:limit]

    async def _get_top_paths(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门路径 TOP N"""
        logs = await OperationLog.all().order_by("-created_at").limit(1000).all()

        # 统计路径访问次数
        path_count: Dict[str, Dict[str, Any]] = {}
        for log in logs:
            if log.path:
                if log.path not in path_count:
                    path_count[log.path] = {
                        "path": log.path,
                        "method": log.method,
                        "count": 0,
                    }
                path_count[log.path]["count"] += 1

        # 排序并取前 N 个
        sorted_paths = sorted(
            path_count.values(), key=lambda x: x["count"], reverse=True
        )
        return sorted_paths[:limit]

    async def delete_by_ids(self, ids: List[int]) -> int:
        """批量删除日志"""
        deleted_count = await OperationLog.filter(id__in=ids).delete()
        return deleted_count

    async def clear_old_logs(self, days: int = 30) -> int:
        """清理指定天数之前的日志"""
        threshold = datetime.now() - timedelta(days=days)
        deleted_count = await OperationLog.filter(created_at__lt=threshold).delete()
        return deleted_count

    async def create_log(
        self,
        user_id: Optional[int] = None,
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
