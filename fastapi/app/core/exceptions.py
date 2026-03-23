"""
自定义异常模块

定义应用中使用的自定义异常类，用于统一错误处理。
"""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIException(HTTPException):
    """
    API 异常基类

    所有自定义 API 异常的基类，提供统一的错误响应格式。
    """

    def __init__(
        self,
        code: int = 500,
        message: str = "服务器内部错误",
        status_code: int = status.HTTP_200_OK,
        headers: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        super().__init__(status_code=status_code, detail=message, headers=headers)


class AuthenticationError(APIException):
    """认证错误"""

    def __init__(self, message: str = "认证失败", code: int = 40001):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class PermissionDenied(APIException):
    """权限不足"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            code=403,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFound(APIException):
    """资源不存在"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(
            code=404,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationError(APIException):
    """数据验证错误"""

    def __init__(self, message: str = "数据验证失败"):
        super().__init__(
            code=400,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class BusinessError(APIException):
    """业务逻辑错误"""

    def __init__(self, message: str = "业务处理失败"):
        super().__init__(
            code=400,
            message=message,
            status_code=status.HTTP_200_OK,
        )


class DuplicateError(APIException):
    """数据重复错误"""

    def __init__(self, message: str = "数据已存在"):
        super().__init__(
            code=409,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitError(APIException):
    """请求频率限制"""

    def __init__(self, message: str = "请求过于频繁，请稍后重试"):
        super().__init__(
            code=429,
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# 异常处理函数
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """处理 API 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理验证异常"""
    errors: list[dict[str, str]] = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {"errors": errors},
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理 HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    import traceback

    # 记录错误日志
    from loguru import logger

    error_detail = traceback.format_exc()
    logger.error(error_detail)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误，请联系管理员",
            "data": None,
        },
    )
