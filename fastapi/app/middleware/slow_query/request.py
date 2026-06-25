"""
HTTP 慢请求中间件

记录超过阈值的请求耗时，用于定位接口性能问题。
"""

import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.middleware.slow_query.constants import (
    DEFAULT_SLOW_THRESHOLD_MS,
    DEFAULT_VERY_SLOW_THRESHOLD_MS,
    EXCLUDED_PATHS,
)
from app.utils.logger import get_request_id


class SlowQueryMiddleware(BaseHTTPMiddleware):
    """记录执行时间超过阈值的 HTTP 请求。"""

    DEFAULT_SLOW_THRESHOLD_MS = DEFAULT_SLOW_THRESHOLD_MS
    DEFAULT_VERY_SLOW_THRESHOLD_MS = DEFAULT_VERY_SLOW_THRESHOLD_MS
    EXCLUDED_PATHS: set[str] = set(EXCLUDED_PATHS)

    def __init__(
        self,
        app: ASGIApp,
        slow_threshold_ms: int = DEFAULT_SLOW_THRESHOLD_MS,
        very_slow_threshold_ms: int = DEFAULT_VERY_SLOW_THRESHOLD_MS,
        exclude_paths: list[str] | None = None,
        enable_db_monitoring: bool = True,
    ):
        """初始化慢请求中间件并保存阈值配置。"""
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.very_slow_threshold_ms = very_slow_threshold_ms
        self.enable_db_monitoring = enable_db_monitoring
        self.excluded_paths = set(self.EXCLUDED_PATHS)

        if exclude_paths:
            self.excluded_paths.update(exclude_paths)

        self._request_count = 0
        self._slow_request_count = 0
        self._very_slow_request_count = 0

    def _should_skip(self, path: str) -> bool:
        """按路径前缀判断是否跳过慢请求统计。"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    def _get_client_ip(self, request: Request) -> str:
        """按代理头优先级获取客户端 IP。"""
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
        """处理请求并在耗时超过阈值时记录日志。"""
        if self._should_skip(request.url.path):
            return await call_next(request)

        start_time = time.time()

        try:
            response = await call_next(request)
            execution_time_ms = int((time.time() - start_time) * 1000)
            self._record_request(request, response, execution_time_ms)
            return response
        except Exception as error:
            execution_time_ms = int((time.time() - start_time) * 1000)
            if execution_time_ms >= self.slow_threshold_ms:
                self._log_error_slow_query(request, error, execution_time_ms)
            raise

    def _record_request(
        self,
        request: Request,
        response: Response,
        execution_time_ms: int,
    ) -> None:
        """更新请求统计并按慢请求等级写日志。"""
        self._request_count += 1

        if execution_time_ms >= self.very_slow_threshold_ms:
            self._very_slow_request_count += 1
            self._log_very_slow_query(request, response, execution_time_ms)
            return

        if execution_time_ms >= self.slow_threshold_ms:
            self._slow_request_count += 1
            self._log_slow_query(request, response, execution_time_ms)

    def _base_log_data(self, request: Request, execution_time_ms: int) -> dict[str, Any]:
        """生成慢请求日志公共字段。"""
        return {
            "request_id": get_request_id(),
            "type": "slow_query",
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else "",
            "execution_time_ms": execution_time_ms,
            "client_ip": self._get_client_ip(request),
        }

    def _log_slow_query(
        self,
        request: Request,
        response: Response,
        execution_time_ms: int,
    ) -> None:
        """记录慢请求日志。"""
        log_data = {
            **self._base_log_data(request, execution_time_ms),
            "level": "slow",
            "status_code": response.status_code,
            "threshold_ms": self.slow_threshold_ms,
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
        """记录非常慢请求日志。"""
        log_data = {
            **self._base_log_data(request, execution_time_ms),
            "level": "very_slow",
            "status_code": response.status_code,
            "threshold_ms": self.very_slow_threshold_ms,
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
        """记录抛出异常的慢请求日志。"""
        log_data = {
            **self._base_log_data(request, execution_time_ms),
            "level": "error",
            "threshold_ms": self.slow_threshold_ms,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        logger.bind(**log_data).error(
            f"异常慢查询: {request.method} {request.url.path} - "
            f"{execution_time_ms}ms - {type(error).__name__}: {str(error)}"
        )

    def get_stats(self) -> dict[str, Any]:
        """获取慢请求统计信息。"""
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
