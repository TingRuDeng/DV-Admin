"""
慢查询日志中间件

记录执行时间超过阈值的请求和数据库查询。
"""

import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import get_request_id


class SlowQueryMiddleware(BaseHTTPMiddleware):
    """
    慢查询日志中间件

    记录执行时间超过阈值的请求，用于性能监控和优化。
    """

    # 默认慢查询阈值（毫秒）
    DEFAULT_SLOW_THRESHOLD_MS = 1000

    # 默认非常慢查询阈值（毫秒）
    DEFAULT_VERY_SLOW_THRESHOLD_MS = 5000

    # 不记录的路径（前缀匹配）
    EXCLUDED_PATHS: set[str] = {
        "/api/swagger",
        "/api/redoc",
        "/api/openapi.json",
        "/health",
        "/favicon.ico",
        "/media",
    }

    def __init__(
        self,
        app: ASGIApp,
        slow_threshold_ms: int = DEFAULT_SLOW_THRESHOLD_MS,
        very_slow_threshold_ms: int = DEFAULT_VERY_SLOW_THRESHOLD_MS,
        exclude_paths: list[str] | None = None,
        enable_db_monitoring: bool = True,
    ):
        """
        初始化慢查询中间件

        Args:
            app: ASGI 应用
            slow_threshold_ms: 慢查询阈值（毫秒）
            very_slow_threshold_ms: 非常慢查询阈值（毫秒）
            exclude_paths: 排除的路径列表
            enable_db_monitoring: 是否启用数据库查询监控
        """
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.very_slow_threshold_ms = very_slow_threshold_ms
        self.enable_db_monitoring = enable_db_monitoring

        if exclude_paths:
            self.EXCLUDED_PATHS.update(exclude_paths)

        # 统计信息
        self._request_count = 0
        self._slow_request_count = 0
        self._very_slow_request_count = 0

    def _should_skip(self, path: str) -> bool:
        """判断是否应该跳过"""
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP 地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            响应对象
        """
        # 检查是否跳过
        if self._should_skip(request.url.path):
            return await call_next(request)

        # 记录开始时间
        start_time = time.time()

        try:
            # 调用下一个处理器
            response = await call_next(request)

            # 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)

            # 更新统计
            self._request_count += 1

            # 检查是否为慢查询
            if execution_time_ms >= self.very_slow_threshold_ms:
                self._very_slow_request_count += 1
                self._log_very_slow_query(request, response, execution_time_ms)
            elif execution_time_ms >= self.slow_threshold_ms:
                self._slow_request_count += 1
                self._log_slow_query(request, response, execution_time_ms)

            return response

        except Exception as e:
            # 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)

            # 记录异常慢查询
            if execution_time_ms >= self.slow_threshold_ms:
                self._log_error_slow_query(request, e, execution_time_ms)

            raise

    def _log_slow_query(
        self,
        request: Request,
        response: Response,
        execution_time_ms: int,
    ) -> None:
        """记录慢查询"""
        request_id = get_request_id()
        client_ip = self._get_client_ip(request)

        log_data = {
            "request_id": request_id,
            "type": "slow_query",
            "level": "slow",
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else "",
            "status_code": response.status_code,
            "execution_time_ms": execution_time_ms,
            "threshold_ms": self.slow_threshold_ms,
            "client_ip": client_ip,
        }

        logger.bind(**log_data).warning(
            f"慢查询警告: {request.method} {request.url.path} - "
            f"{execution_time_ms}ms (阈值: {self.slow_threshold_ms}ms)"
        )

    def _log_very_slow_query(
        self,
        request: Request,
        response: Response,
        execution_time_ms: int,
    ) -> None:
        """记录非常慢查询"""
        request_id = get_request_id()
        client_ip = self._get_client_ip(request)

        log_data = {
            "request_id": request_id,
            "type": "slow_query",
            "level": "very_slow",
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else "",
            "status_code": response.status_code,
            "execution_time_ms": execution_time_ms,
            "threshold_ms": self.very_slow_threshold_ms,
            "client_ip": client_ip,
        }

        logger.bind(**log_data).error(
            f"严重慢查询: {request.method} {request.url.path} - "
            f"{execution_time_ms}ms (阈值: {self.very_slow_threshold_ms}ms)"
        )

    def _log_error_slow_query(
        self,
        request: Request,
        error: Exception,
        execution_time_ms: int,
    ) -> None:
        """记录异常慢查询"""
        request_id = get_request_id()
        client_ip = self._get_client_ip(request)

        log_data = {
            "request_id": request_id,
            "type": "slow_query",
            "level": "error",
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else "",
            "execution_time_ms": execution_time_ms,
            "threshold_ms": self.slow_threshold_ms,
            "client_ip": client_ip,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        logger.bind(**log_data).error(
            f"异常慢查询: {request.method} {request.url.path} - "
            f"{execution_time_ms}ms - {type(error).__name__}: {str(error)}"
        )

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "total_requests": self._request_count,
            "slow_requests": self._slow_request_count,
            "very_slow_requests": self._very_slow_request_count,
            "slow_threshold_ms": self.slow_threshold_ms,
            "very_slow_threshold_ms": self.very_slow_threshold_ms,
            "slow_rate": (
                self._slow_request_count / self._request_count * 100
                if self._request_count > 0
                else 0
            ),
        }


class DatabaseQueryMonitor:
    """
    数据库查询监控器

    用于监控和记录慢数据库查询。
    注意：这是一个辅助类，需要与具体的 ORM 集成。
    """

    def __init__(
        self,
        slow_query_threshold_ms: int = 500,
        very_slow_query_threshold_ms: int = 2000,
    ):
        """
        初始化数据库查询监控器

        Args:
            slow_query_threshold_ms: 慢查询阈值（毫秒）
            very_slow_query_threshold_ms: 非常慢查询阈值（毫秒）
        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.very_slow_query_threshold_ms = very_slow_query_threshold_ms

        # 统计信息
        self._query_count = 0
        self._slow_query_count = 0
        self._very_slow_query_count = 0
        self._total_query_time_ms = 0

    def log_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        execution_time_ms: int = 0,
    ) -> None:
        """
        记录数据库查询

        Args:
            sql: SQL 语句
            params: 查询参数
            execution_time_ms: 执行时间（毫秒）
        """
        self._query_count += 1
        self._total_query_time_ms += execution_time_ms

        request_id = get_request_id()

        if execution_time_ms >= self.very_slow_query_threshold_ms:
            self._very_slow_query_count += 1
            log_data = {
                "request_id": request_id,
                "type": "slow_db_query",
                "level": "very_slow",
                "sql": sql[:500] if len(sql) > 500 else sql,
                "params": str(params)[:200] if params else None,
                "execution_time_ms": execution_time_ms,
                "threshold_ms": self.very_slow_query_threshold_ms,
            }
            logger.bind(**log_data).error(
                f"严重慢数据库查询: {execution_time_ms}ms"
            )

        elif execution_time_ms >= self.slow_query_threshold_ms:
            self._slow_query_count += 1
            log_data = {
                "request_id": request_id,
                "type": "slow_db_query",
                "level": "slow",
                "sql": sql[:500] if len(sql) > 500 else sql,
                "params": str(params)[:200] if params else None,
                "execution_time_ms": execution_time_ms,
                "threshold_ms": self.slow_query_threshold_ms,
            }
            logger.bind(**log_data).warning(
                f"慢数据库查询: {execution_time_ms}ms"
            )

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "total_queries": self._query_count,
            "slow_queries": self._slow_query_count,
            "very_slow_queries": self._very_slow_query_count,
            "total_query_time_ms": self._total_query_time_ms,
            "avg_query_time_ms": (
                self._total_query_time_ms / self._query_count
                if self._query_count > 0
                else 0
            ),
            "slow_query_rate": (
                self._slow_query_count / self._query_count * 100
                if self._query_count > 0
                else 0
            ),
        }

    def reset_stats(self) -> None:
        """重置统计信息"""
        self._query_count = 0
        self._slow_query_count = 0
        self._very_slow_query_count = 0
        self._total_query_time_ms = 0


# 全局数据库查询监控器实例
db_query_monitor = DatabaseQueryMonitor()
