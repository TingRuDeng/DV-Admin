"""
请求日志中间件

记录 HTTP 请求和响应信息，并生成请求 ID 用于链路追踪。
"""

import json
import time
import uuid
from collections.abc import Callable
from typing import TypedDict

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.middleware.request_logging.body import (
    clone_response_with_body,
    decode_body,
    get_request_body,
)
from app.middleware.request_logging.client import get_client_ip, parse_user_agent
from app.middleware.request_logging.constants import EXCLUDED_BODY_PATHS, EXCLUDED_PATHS
from app.utils.logger import clear_request_id, set_request_id

# 只持久化写操作，避免 GET 轮询淹没审计表
PERSISTED_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
SENSITIVE_KEYWORDS = ("password", "token", "secret", "key", "authorization")


def mask_sensitive_body(body: str) -> str:
    """掩码请求体中的敏感字段；非 JSON 或解析失败时返回空串以避免泄露。"""
    if not body:
        return ""
    try:
        parsed = json.loads(body)
    except (ValueError, TypeError):
        return ""

    def _mask(value: object, depth: int = 0) -> object:
        if depth > 10:
            return "***MAX_DEPTH***"
        if isinstance(value, dict):
            return {
                k: ("******" if any(s in k.lower() for s in SENSITIVE_KEYWORDS) else _mask(v, depth + 1))
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [_mask(item, depth + 1) for item in value]
        return value

    return json.dumps(_mask(parsed), ensure_ascii=False)[:4096]


class RequestLogContext(TypedDict):
    """请求日志流程中的共享上下文字段。"""

    request_id: str
    method: str
    path: str
    client_ip: str
    request_log: dict[str, object]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """记录请求和响应的详细信息，并生成请求 ID。"""

    EXCLUDED_PATHS: set[str] = set(EXCLUDED_PATHS)
    EXCLUDED_BODY_PATHS: set[str] = set(EXCLUDED_BODY_PATHS)

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
        exclude_body_paths: list[str] | None = None,
        log_request_body: bool = True,
        log_response_body: bool = False,
        max_body_length: int = 1000,
    ):
        """初始化请求日志中间件配置。"""
        super().__init__(app)
        self.excluded_paths = set(self.EXCLUDED_PATHS)
        self.excluded_body_paths = set(self.EXCLUDED_BODY_PATHS)
        if exclude_paths:
            self.excluded_paths.update(exclude_paths)
        if exclude_body_paths:
            self.excluded_body_paths.update(exclude_body_paths)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length

    def _should_skip_logging(self, path: str) -> bool:
        """判断当前路径是否跳过请求日志。"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    def _should_exclude_body(self, path: str) -> bool:
        """判断当前路径是否跳过请求体记录。"""
        return any(path.startswith(excluded) for excluded in self.excluded_body_paths)

    def _get_client_ip(self, request: Request) -> str:
        """兼容历史私有方法，委托客户端解析 helper。"""
        return get_client_ip(request)

    def _parse_user_agent(self, user_agent: str) -> dict[str, str]:
        """兼容历史私有方法，委托 User-Agent 解析 helper。"""
        return parse_user_agent(user_agent)

    async def _get_request_body(self, request: Request, path: str) -> str:
        """兼容历史私有方法，委托请求体读取 helper。"""
        return await get_request_body(
            request,
            self._should_exclude_body(path),
            self.log_request_body,
            self.max_body_length,
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录请求、响应或异常日志。"""
        if self._should_skip_logging(request.url.path):
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)

        start_time = time.time()
        context = await self._build_request_context(request, request_id)
        logger.bind(**context["request_log"]).info(
            f"请求开始: {context['method']} {context['path']}"
        )

        try:
            response = await call_next(request)
            response = await self._log_response(response, context, start_time)
            response.headers["X-Request-ID"] = request_id
            await self._persist_operation_log(request, response, context, start_time)
            return response
        except Exception as error:
            self._log_error(error, context, start_time)
            raise
        finally:
            clear_request_id()

    async def _persist_operation_log(
        self,
        request: Request,
        response: Response,
        context: RequestLogContext,
        start_time: float,
    ) -> None:
        """将写操作落库到 OperationLog；任何失败都不得影响主请求。"""
        if context["method"] not in PERSISTED_METHODS:
            return
        if not context["path"].startswith("/api/"):
            return
        try:
            from app.services.system.log_service import log_service

            user = getattr(request.state, "user", None)
            request_log = context["request_log"]
            await log_service.create_log(
                user_id=getattr(user, "id", None),
                username=getattr(user, "username", "") or "",
                name=getattr(user, "name", "") or "",
                method=context["method"],
                path=context["path"][:500],
                query_params=str(request_log.get("query_params", ""))[:4096],
                request_body=mask_sensitive_body(str(request_log.get("body", ""))),
                response_status=response.status_code,
                ip=(context["client_ip"] or "")[:50],
                browser=str(request_log.get("browser", ""))[:100],
                os=str(request_log.get("os", ""))[:100],
                execution_time=int((time.time() - start_time) * 1000),
                status=1 if response.status_code < 400 else 0,
            )
        except Exception as error:  # noqa: BLE001  审计落库失败不能影响业务请求
            logger.warning(f"操作日志落库失败: {error}")

    async def _build_request_context(
        self,
        request: Request,
        request_id: str,
    ) -> RequestLogContext:
        """构造请求日志上下文，避免主流程重复提取字段。"""
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        ua_info = self._parse_user_agent(user_agent)
        request_body = await self._get_request_body(request, path)

        request_log: dict[str, object] = {
            "request_id": request_id,
            "type": "request",
            "method": method,
            "path": path,
            "query_params": query_params,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "browser": ua_info["browser"],
            "os": ua_info["os"],
            "device": ua_info["device"],
        }

        if self.log_request_body and not self._should_exclude_body(path):
            request_log["body"] = request_body

        return {
            "request_id": request_id,
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "request_log": request_log,
        }

    async def _log_response(
        self,
        response: Response,
        context: RequestLogContext,
        start_time: float,
    ) -> Response:
        """记录响应日志并在需要时复制响应体。"""
        execution_time = int((time.time() - start_time) * 1000)
        response_log = {
            "request_id": context["request_id"],
            "type": "response",
            "method": context["method"],
            "path": context["path"],
            "status_code": response.status_code,
            "execution_time_ms": execution_time,
            "client_ip": context["client_ip"],
        }

        if self.log_response_body:
            response = await self._attach_response_body(response, response_log)

        self._write_response_log(response, response_log, execution_time, context)
        return response

    async def _attach_response_body(
        self,
        response: Response,
        response_log: dict[str, object],
    ) -> Response:
        """读取响应体用于日志，并返回可继续下发的新响应。"""
        try:
            cloned_response, response_body = await clone_response_with_body(response)
            response_log["body"] = decode_body(response_body, self.max_body_length)
            return cloned_response
        except Exception as error:
            response_log["body_error"] = str(error)
            return response

    def _write_response_log(
        self,
        response: Response,
        response_log: dict[str, object],
        execution_time: int,
        context: RequestLogContext,
    ) -> None:
        """按响应状态码选择日志等级。"""
        message = (
            f"请求完成: {context['method']} {context['path']} - "
            f"{response.status_code} - {execution_time}ms"
        )

        if response.status_code >= 500:
            logger.bind(**response_log).error(message)
            return
        if response.status_code >= 400:
            logger.bind(**response_log).warning(message)
            return
        logger.bind(**response_log).info(message)

    def _log_error(
        self,
        error: Exception,
        context: RequestLogContext,
        start_time: float,
    ) -> None:
        """记录请求处理异常日志。"""
        execution_time = int((time.time() - start_time) * 1000)
        error_log = {
            "request_id": context["request_id"],
            "type": "error",
            "method": context["method"],
            "path": context["path"],
            "execution_time_ms": execution_time,
            "client_ip": context["client_ip"],
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        logger.bind(**error_log).exception(
            f"请求异常: {context['method']} {context['path']} - "
            f"{type(error).__name__}: {str(error)}"
        )
