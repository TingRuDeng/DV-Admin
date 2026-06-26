"""
请求日志中间件兼容入口

保留历史导入路径，实际实现位于 `app.middleware.request_logging` 包。
"""

from app.middleware.request_logging import RequestLoggingMiddleware

__all__ = ["RequestLoggingMiddleware"]
