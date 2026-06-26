"""
日志服务统计聚合 helper
"""

from datetime import datetime, timedelta
from typing import Any

from app.db.models.system import OperationLog
from app.schemas.system import VisitTrendOut


def build_visit_trend(
    logs: list[OperationLog],
    start_date: datetime,
    end_date: datetime,
) -> list[VisitTrendOut]:
    """按日期范围生成访问趋势，缺失日期补 0。"""
    date_count: dict[str, int] = {}
    for log in logs:
        date_str = log.created_at.strftime("%Y-%m-%d")
        date_count[date_str] = date_count.get(date_str, 0) + 1

    result = []
    current_date = start_date.date()
    end_date_only = end_date.date()
    while current_date <= end_date_only:
        date_str = current_date.strftime("%Y-%m-%d")
        result.append(VisitTrendOut(date=date_str, count=date_count.get(date_str, 0)))
        current_date += timedelta(days=1)
    return result


def calculate_avg_execution_time(logs: list[OperationLog]) -> float:
    """计算平均执行耗时，无有效日志时返回 0。"""
    if not logs:
        return 0.0
    total_time = sum(log.execution_time for log in logs)
    return round(total_time / len(logs), 2)


def count_top_users(logs: list[OperationLog], limit: int) -> list[dict[str, Any]]:
    """按用户名统计活跃用户 TOP N。"""
    user_count: dict[str, dict[str, Any]] = {}
    for log in logs:
        if log.username:
            if log.username not in user_count:
                user_count[log.username] = {
                    "username": log.username,
                    "name": log.name,
                    "count": 0,
                }
            user_count[log.username]["count"] += 1

    sorted_users = sorted(user_count.values(), key=lambda x: x["count"], reverse=True)
    return sorted_users[:limit]


def count_top_paths(logs: list[OperationLog], limit: int) -> list[dict[str, Any]]:
    """按路径统计热门访问路径 TOP N。"""
    path_count: dict[str, dict[str, Any]] = {}
    for log in logs:
        if log.path:
            if log.path not in path_count:
                path_count[log.path] = {
                    "path": log.path,
                    "method": log.method,
                    "count": 0,
                }
            path_count[log.path]["count"] += 1

    sorted_paths = sorted(path_count.values(), key=lambda x: x["count"], reverse=True)
    return sorted_paths[:limit]
