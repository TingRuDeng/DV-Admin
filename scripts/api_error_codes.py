from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

SUCCESS_CODE = 20000
ERROR_CODE = 40000
ACCESS_TOKEN_INVALID_CODE = 40001
REFRESH_TOKEN_INVALID_CODE = 40002


@dataclass(frozen=True)
class ApiErrorCode:
    """共享错误码契约项，描述前端与双后端共同依赖的错误语义。"""

    key: str
    value: int
    description: str


API_ERROR_CODES: tuple[ApiErrorCode, ...] = (
    ApiErrorCode("SUCCESS", SUCCESS_CODE, "成功"),
    ApiErrorCode("ERROR", ERROR_CODE, "通用业务错误"),
    ApiErrorCode("ACCESS_TOKEN_INVALID", ACCESS_TOKEN_INVALID_CODE, "Access Token 无效或过期"),
    ApiErrorCode("REFRESH_TOKEN_INVALID", REFRESH_TOKEN_INVALID_CODE, "Refresh Token 无效或过期"),
)

API_ERROR_CODE_VALUES: Mapping[str, int] = MappingProxyType(
    {code.key: code.value for code in API_ERROR_CODES}
)
API_ERROR_CODE_BY_VALUE: Mapping[int, ApiErrorCode] = MappingProxyType(
    {code.value: code for code in API_ERROR_CODES}
)


def iter_api_error_codes() -> tuple[ApiErrorCode, ...]:
    """返回只读错误码目录，供校验脚本和双后端测试复用。"""
    return API_ERROR_CODES


def assert_api_error_code_catalog() -> None:
    """校验共享错误码目录自身完整，避免重复值或关键语义缺失。"""
    keys = {code.key for code in API_ERROR_CODES}
    values = {code.value for code in API_ERROR_CODES}

    assert len(keys) == len(API_ERROR_CODES)
    assert len(values) == len(API_ERROR_CODES)
    assert API_ERROR_CODE_VALUES["SUCCESS"] == SUCCESS_CODE
    assert API_ERROR_CODE_VALUES["ERROR"] == ERROR_CODE
    assert API_ERROR_CODE_VALUES["ACCESS_TOKEN_INVALID"] == ACCESS_TOKEN_INVALID_CODE
    assert API_ERROR_CODE_VALUES["REFRESH_TOKEN_INVALID"] == REFRESH_TOKEN_INVALID_CODE
    assert ERROR_CODE != ACCESS_TOKEN_INVALID_CODE
    assert ERROR_CODE != REFRESH_TOKEN_INVALID_CODE


def assert_known_api_error_code(code: int) -> None:
    """断言错误码属于当前共享目录。"""
    assert code in API_ERROR_CODE_BY_VALUE, f"unknown API error code: {code}"
