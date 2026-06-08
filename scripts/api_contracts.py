from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from scripts.api_endpoint_contracts import (
    CRITICAL_ENDPOINT_CONTRACTS as _CRITICAL_ENDPOINT_CONTRACTS,
    assert_endpoint_contract_catalog as _assert_endpoint_contract_catalog,
    iter_critical_endpoint_contracts as _iter_critical_endpoint_contracts,
)
from scripts.api_error_codes import SUCCESS_CODE, assert_known_api_error_code


DJANGO_BACKEND = "django"
FASTAPI_BACKEND = "fastapi"
CRITICAL_ENDPOINT_CONTRACTS = _CRITICAL_ENDPOINT_CONTRACTS


@dataclass(frozen=True)
class ApiEnvelope:
    """归一化后的 API 响应信封，用于跨后端契约测试。"""

    code: int
    message: str
    data: Any
    errors: Any = None


def iter_critical_endpoint_contracts():
    """返回关键端点契约目录，保留共享契约单一入口。"""
    return _iter_critical_endpoint_contracts()


def assert_endpoint_contract_catalog() -> None:
    """校验关键端点契约目录，供 Django/FastAPI 测试共同调用。"""
    _assert_endpoint_contract_catalog()


def normalize_api_envelope(payload: Mapping[str, Any]) -> ApiEnvelope:
    """把 Django/FastAPI 当前响应字段归一成前端可理解的公共语义。"""
    code = _require_int(payload, "code")
    errors = payload.get("errors")
    message = _normalize_message(errors) or _normalize_message(payload.get("msg"))
    message = message or _normalize_message(payload.get("message")) or ""
    return ApiEnvelope(
        code=code,
        message=message,
        data=payload.get("data"),
        errors=errors,
    )


def assert_success_envelope(payload: Mapping[str, Any], backend: str) -> None:
    """断言成功响应满足当前共享契约。"""
    _assert_backend(backend)
    envelope = normalize_api_envelope(payload)
    assert envelope.code == SUCCESS_CODE
    assert "data" in payload

    if backend == DJANGO_BACKEND:
        assert "msg" in payload
        assert "errors" in payload
    else:
        assert "message" in payload


def assert_error_envelope(payload: Mapping[str, Any], backend: str) -> None:
    """断言错误响应满足当前共享契约。"""
    _assert_backend(backend)
    envelope = normalize_api_envelope(payload)
    assert envelope.code != SUCCESS_CODE
    assert_known_api_error_code(envelope.code)
    assert envelope.message

    if backend == DJANGO_BACKEND:
        assert "errors" in payload
        assert "msg" in payload
    else:
        assert "message" in payload


def assert_page_payload(payload: Mapping[str, Any]) -> None:
    """断言分页载荷满足前端 ProTable/PageResult 读取契约。"""
    assert "list" in payload
    assert "total" in payload
    assert isinstance(payload["list"], list)
    assert isinstance(payload["total"], int)


def _require_int(payload: Mapping[str, Any], key: str) -> int:
    """读取整型字段，避免字符串状态码混入共享契约。"""
    value = payload.get(key)
    assert isinstance(value, int), f"{key} must be int"
    return value


def _assert_backend(backend: str) -> None:
    """限制契约测试只能声明当前仓库已知后端。"""
    assert backend in {DJANGO_BACKEND, FASTAPI_BACKEND}, f"unknown backend: {backend}"


def _normalize_message(value: Any) -> str | None:
    """把错误详情压成可比较文本，保持前端错误展示语义一致。"""
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, Mapping):
        detail = value.get("detail")
        return _normalize_message(detail) or str(value)
    if isinstance(value, list):
        return "；".join(item for item in (_normalize_message(item) for item in value) if item)
    return None
