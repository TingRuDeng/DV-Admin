# -*- coding: utf-8 -*-

import json
import logging
import re
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from django_redis import get_redis_connection
from django.utils.deprecation import MiddlewareMixin

from drf_admin.apps.oauth.utils import get_request_browser, get_request_os, get_request_ip


SENSITIVE_KEYWORDS = ["password", "token", "secret", "key", "authorization"]
MAX_LOG_LENGTH = 4096


def mask_sensitive_data(data: Any, depth: int = 0) -> Any:
    """
    Recursively mask sensitive fields in data structure.
    """
    if depth > 10:
        return "***MAX_DEPTH***"

    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if any(re.search(keyword, k, re.IGNORECASE) for keyword in SENSITIVE_KEYWORDS):
                masked[k] = "******"
            else:
                masked[k] = mask_sensitive_data(v, depth + 1)
        return masked
    elif isinstance(data, (list, tuple)):
        return [mask_sensitive_data(item, depth + 1) for item in data]
    else:
        return data


class OperationLogMiddleware:
    """
    操作日志记录中间件
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.operation_logger = logging.getLogger("operation")
        self.query_logger = logging.getLogger("query")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_body = self._parse_request_body(request)

        if request.method == "GET":
            request_body.update(dict(request.GET))
            logger = self.query_logger
        else:
            request_body.update(dict(request.POST))
            logger = self.operation_logger

        request_body = mask_sensitive_data(request_body)

        response = self.get_response(request)

        try:
            response_body = self._extract_response_body(response)
            response_body = mask_sensitive_data(response_body)
        except Exception as e:
            logging.error(f"日志敏感信息覆写失败: {e}, 请求URL：{request.path}")
            response_body = {}

        request_ip = get_request_ip(request)

        log_info = (
            f"[{request.user}@{request_ip} "
            f"[Request: {request.method} {request.path} {self._truncate_log(request_body)}] "
            f"[Response: {response.status_code} {response.reason_phrase} "
            f"{self._truncate_log(response_body)}]]"
        )

        if response.status_code >= 500:
            logger.error(log_info)
        elif response.status_code >= 400:
            logger.warning(log_info)
        else:
            logger.info(log_info)

        return response

    def _parse_request_body(self, request: HttpRequest) -> dict:
        """解析请求体"""
        request_body = {}
        content_type = request.META.get("CONTENT_TYPE", "")
        try:
            if "application/json" in content_type and request.body != b"":
                request_body = json.loads(request.body)
                if not isinstance(request_body, dict):
                    request_body = {}
        except Exception as e:
            logging.error(f"JSON解析请求体失败: {e}，请求url：{request.path}")
        return request_body

    def _extract_response_body(self, response: HttpResponse) -> Any:
        """提取响应体"""
        if hasattr(response, "data"):
            return response.data
        return {}

    def _truncate_log(self, data: Any) -> str:
        """截断日志防止过大"""
        log_str = str(data)
        if len(log_str) > MAX_LOG_LENGTH:
            return log_str[:MAX_LOG_LENGTH] + "...***TRUNCATED***"
        return log_str


class ResponseMiddleware(MiddlewareMixin):
    """
    统一响应格式中间件
    """

    def process_request(self, request):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_exception(self, request, exception):
        pass

    def process_response(self, request, response):
        if not isinstance(response, Response):
            return response

        content_type = response.get("content-type", "")
        if "application/json" not in content_type:
            return response

        if response.status_code >= 400:
            msg = _("请求失败")
            code = 40000
            detail = None
            data = {}

            if isinstance(response.data, dict):
                detail = response.data.get("detail")
                error_code = response.data.get("code")
                
                # 检查是否是 token 无效错误，使用 40001 错误码
                if error_code == "token_not_valid":
                    code = 40001
                else:
                    code = error_code or 40000
            elif isinstance(response.data, (str, list)):
                detail = str(response.data)

        elif response.status_code in [200, 201]:
            data = response.data

            if isinstance(data, dict) and set(data.keys()) == {"code", "msg", "errors", "data"}:
                return response

            code = 20000
            msg = _("成功")
            detail = None
        else:
            return response

        response.data = {"msg": msg, "errors": detail, "code": code, "data": data}
        response.content = response.rendered_content
        return response


class IpBlackListMiddleware(MiddlewareMixin):
    """
    IP黑名单校验中间件
    """

    def process_request(self, request):
        request_ip = get_request_ip(request)
        from django.core.cache import cache
        from django.conf import settings

        redis_host = getattr(settings, "REDIS_HOST", None)
        redis_port = getattr(settings, "REDIS_PORT", None)

        if redis_host and redis_port:
            conn = get_redis_connection("user_info")
            if conn.sismember("ip_black_list", request_ip):
                return HttpResponse(
                    _("IP已被拉入黑名单, 请联系管理员"), status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if cache.get(f"ip_black_list:{request_ip}"):
                return HttpResponse(
                    _("IP已被拉入黑名单, 请联系管理员"), status=status.HTTP_400_BAD_REQUEST
                )
