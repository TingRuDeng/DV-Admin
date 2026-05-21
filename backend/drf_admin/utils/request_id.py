# -*- coding: utf-8 -*-

from contextvars import ContextVar
from uuid import uuid4

from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_META_KEY = "HTTP_X_REQUEST_ID"

_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """获取当前请求链路的 request id。"""
    return _request_id_var.get()


def set_request_id(request_id: str) -> None:
    """写入当前请求链路的 request id。"""
    _request_id_var.set(request_id)


def clear_request_id() -> None:
    """清理请求上下文，避免线程复用时串请求。"""
    _request_id_var.set(None)


def _resolve_request_id(request: HttpRequest) -> str:
    """优先复用客户端传入的 request id，缺失时生成新的链路标识。"""
    request_id = request.META.get(REQUEST_ID_META_KEY)
    return str(request_id).strip() if request_id else uuid4().hex


class RequestIdMiddleware:
    """为每个 Django 请求注入 request id，并回写响应头。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = _resolve_request_id(request)
        request.request_id = request_id
        set_request_id(request_id)

        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_id()
