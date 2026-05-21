# -*- coding: utf-8 -*-

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from drf_admin.utils.request_id import get_request_id

STATUS_OK = 200
STATUS_UNAVAILABLE = 503


def _base_payload(status: str) -> dict:
    """生成健康检查基础响应，便于日志按 request id 串联。"""
    payload = {"status": status}
    request_id = get_request_id()
    if request_id:
        payload["request_id"] = request_id
    return payload


@require_GET
def liveness_check(request):
    """只验证进程可响应，不依赖数据库等外部资源。"""
    return JsonResponse(_base_payload("alive"), status=STATUS_OK)


@require_GET
def readiness_check(request):
    """验证当前实例是否具备接流量的基础依赖。"""
    payload = _base_payload("ready")
    try:
        connection.ensure_connection()
        payload["checks"] = {"database": "ok"}
        return JsonResponse(payload, status=STATUS_OK)
    except Exception as exc:
        payload["status"] = "unavailable"
        payload["checks"] = {"database": "error"}
        payload["error"] = str(exc)
        return JsonResponse(payload, status=STATUS_UNAVAILABLE)


@require_GET
def health_check(request):
    """聚合基础健康状态，作为 CI 和部署探针的默认入口。"""
    payload = _base_payload("ok")
    payload["checks"] = {"liveness": "ok", "readiness": "ok"}
    return JsonResponse(payload, status=STATUS_OK)
