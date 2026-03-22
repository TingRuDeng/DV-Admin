# -*- coding: utf-8 -*-
"""
请求日志中间件

记录所有 HTTP 请求的详细信息，包括：
- 请求方法、路径、参数
- 响应状态、执行时间
- 请求 IP 和 User-Agent
"""

import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import clear_request_id, set_request_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录请求和响应的详细信息，并生成请求 ID 用于追踪。
    """

    # 不记录日志的路径（前缀匹配）
    EXCLUDED_PATHS: Set[str] = {
        "/api/swagger",
        "/api/redoc",
        "/api/openapi.json",
        "/health",
        "/favicon.ico",
        "/media",
    }

    # 不记录请求体的路径（可能包含敏感信息或文件）
    EXCLUDED_BODY_PATHS: Set[str] = {
        "/api/v1/auth/login",
        "/api/v1/auth/password",
        "/api/v1/files",
        "/api/v1/profile/avatar",
    }

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
        exclude_body_paths: Optional[List[str]] = None,
        log_request_body: bool = True,
        log_response_body: bool = False,
        max_body_length: int = 1000,
    ):
        """
        初始化请求日志中间件

        Args:
            app: ASGI 应用
            exclude_paths: 排除的路径列表
            exclude_body_paths: 不记录请求体的路径列表
            log_request_body: 是否记录请求体
            log_response_body: 是否记录响应体
            max_body_length: 最大记录的 body 长度
        """
        super().__init__(app)
        if exclude_paths:
            self.EXCLUDED_PATHS.update(exclude_paths)
        if exclude_body_paths:
            self.EXCLUDED_BODY_PATHS.update(exclude_body_paths)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length

    def _should_skip_logging(self, path: str) -> bool:
        """判断是否应该跳过日志记录"""
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        return False

    def _should_exclude_body(self, path: str) -> bool:
        """判断是否应该排除请求体记录"""
        for excluded in self.EXCLUDED_BODY_PATHS:
            if path.startswith(excluded):
                return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP 地址"""
        # 优先从代理头获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个 IP（最原始的客户端 IP）
            return forwarded_for.split(",")[0].strip()

        # 从其他代理头获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接连接的客户端 IP
        if request.client:
            return request.client.host

        return "unknown"

    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """解析 User-Agent 字符串"""
        result = {
            "browser": "Unknown",
            "os": "Unknown",
            "device": "Unknown",
        }

        if not user_agent:
            return result

        user_agent_lower = user_agent.lower()

        # 解析浏览器
        if "edg/" in user_agent_lower:
            result["browser"] = "Edge"
        elif "chrome/" in user_agent_lower:
            result["browser"] = "Chrome"
        elif "firefox/" in user_agent_lower:
            result["browser"] = "Firefox"
        elif "safari/" in user_agent_lower and "chrome/" not in user_agent_lower:
            result["browser"] = "Safari"
        elif "opera/" in user_agent_lower or "opr/" in user_agent_lower:
            result["browser"] = "Opera"
        elif "msie" in user_agent_lower or "trident/" in user_agent_lower:
            result["browser"] = "IE"

        # 解析操作系统
        if "windows" in user_agent_lower:
            result["os"] = "Windows"
        elif "mac" in user_agent_lower:
            result["os"] = "MacOS"
        elif "linux" in user_agent_lower:
            result["os"] = "Linux"
        elif "android" in user_agent_lower:
            result["os"] = "Android"
        elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            result["os"] = "iOS"

        # 解析设备类型
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            result["device"] = "Mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            result["device"] = "Tablet"
        else:
            result["device"] = "Desktop"

        return result

    async def _get_request_body(self, request: Request, path: str) -> str:
        """获取请求体内容"""
        if not self.log_request_body or self._should_exclude_body(path):
            return "[EXCLUDED]"

        try:
            body = await request.body()
            if not body:
                return ""

            # 尝试解码为文本
            try:
                body_str = body.decode("utf-8")
                # 截断过长的内容
                if len(body_str) > self.max_body_length:
                    return body_str[:self.max_body_length] + "...[TRUNCATED]"
                return body_str
            except UnicodeDecodeError:
                return "[BINARY DATA]"
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            响应对象
        """
        # 检查是否跳过日志
        if self._should_skip_logging(request.url.path):
            return await call_next(request)

        # 生成请求 ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)

        # 记录开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        ua_info = self._parse_user_agent(user_agent)

        # 获取请求体（需要在调用 call_next 之前）
        request_body = await self._get_request_body(request, path)

        # 记录请求日志
        request_log = {
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

        logger.bind(**request_log).info(f"请求开始: {method} {path}")

        try:
            # 调用下一个处理器
            response = await call_next(request)

            # 计算执行时间
            execution_time = int((time.time() - start_time) * 1000)

            # 记录响应日志
            response_log = {
                "request_id": request_id,
                "type": "response",
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "execution_time_ms": execution_time,
                "client_ip": client_ip,
            }

            # 记录响应体（可选）
            if self.log_response_body:
                try:
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk

                    # 重新设置响应体
                    from fastapi.responses import Response as FastAPIResponse
                    new_response = FastAPIResponse(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )

                    # 尝试解码响应体
                    try:
                        body_str = response_body.decode("utf-8")
                        if len(body_str) > self.max_body_length:
                            body_str = body_str[:self.max_body_length] + "...[TRUNCATED]"
                        response_log["body"] = body_str
                    except UnicodeDecodeError:
                        response_log["body"] = "[BINARY DATA]"

                    response = new_response
                except Exception as e:
                    response_log["body_error"] = str(e)

            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.bind(**response_log).error(
                    f"请求完成: {method} {path} - {response.status_code} - {execution_time}ms"
                )
            elif response.status_code >= 400:
                logger.bind(**response_log).warning(
                    f"请求完成: {method} {path} - {response.status_code} - {execution_time}ms"
                )
            else:
                logger.bind(**response_log).info(
                    f"请求完成: {method} {path} - {response.status_code} - {execution_time}ms"
                )

            # 添加请求 ID 到响应头
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 计算执行时间
            execution_time = int((time.time() - start_time) * 1000)

            # 记录异常日志
            error_log = {
                "request_id": request_id,
                "type": "error",
                "method": method,
                "path": path,
                "execution_time_ms": execution_time,
                "client_ip": client_ip,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }

            logger.bind(**error_log).exception(
                f"请求异常: {method} {path} - {type(e).__name__}: {str(e)}"
            )

            # 重新抛出异常
            raise

        finally:
            # 清除请求 ID
            clear_request_id()
