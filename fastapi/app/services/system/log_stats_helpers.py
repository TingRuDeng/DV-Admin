"""
日志服务统计聚合 helper
"""

from datetime import date, datetime, timedelta
from typing import Any

from app.core.exceptions import ValidationError
from app.schemas.system import VisitTrendOut

MAX_VISIT_TREND_DAYS = 366


def validate_visit_trend_range(start_date: datetime, end_date: datetime) -> None:
    """拒绝反向或超长趋势查询范围。"""
    if start_date > end_date:
        raise ValidationError("startDate 不能晚于 endDate")
    range_days = (end_date.date() - start_date.date()).days + 1
    if range_days > MAX_VISIT_TREND_DAYS:
        raise ValidationError(f"访问趋势查询范围不能超过 {MAX_VISIT_TREND_DAYS} 天")


def _date_key(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def build_visit_trend_from_counts(
    rows: list[dict[str, Any]],
    start_date: datetime,
    end_date: datetime,
) -> list[VisitTrendOut]:
    """按日期范围生成访问趋势，缺失日期补 0。"""
    date_count = {
        _date_key(row["visit_date"]): int(row["visit_count"])
        for row in rows
    }

    result = []
    current_date = start_date.date()
    end_date_only = end_date.date()
    while current_date <= end_date_only:
        date_str = current_date.strftime("%Y-%m-%d")
        result.append(VisitTrendOut(date=date_str, count=date_count.get(date_str, 0)))
        current_date += timedelta(days=1)
    return result
