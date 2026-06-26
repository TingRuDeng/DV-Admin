"""
日志服务时间辅助函数
"""

from datetime import datetime
from zoneinfo import ZoneInfo

LOCAL_TIMEZONE = ZoneInfo("Asia/Shanghai")


def local_now() -> datetime:
    """生成与 Tortoise 本地时区配置兼容的上海时间。"""
    return datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)


def normalize_local_time(value: datetime) -> datetime:
    """将外部时间统一为上海本地 naive 时间，保持接口展示不偏移。"""
    if value.tzinfo is None:
        return value
    return value.astimezone(LOCAL_TIMEZONE).replace(tzinfo=None)
