"""
日志服务统计聚合 helper
"""

from datetime import datetime, timedelta

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
