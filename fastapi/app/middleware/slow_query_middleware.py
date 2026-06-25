"""
慢查询中间件兼容入口

保留历史导入路径，实际实现位于 `app.middleware.slow_query` 包。
"""

from app.middleware.slow_query import (
    DatabaseQueryMonitor,
    SlowQueryMiddleware,
    db_query_monitor,
)

__all__ = [
    "DatabaseQueryMonitor",
    "SlowQueryMiddleware",
    "db_query_monitor",
]
