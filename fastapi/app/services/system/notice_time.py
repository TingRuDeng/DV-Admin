"""
通知服务时间辅助函数
"""

from datetime import datetime
from zoneinfo import ZoneInfo

LOCAL_TIMEZONE = ZoneInfo("Asia/Shanghai")


def local_now() -> datetime:
    """生成与 Tortoise 本地时区配置兼容的上海时间。"""
    return datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)
