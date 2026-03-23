"""
异常处理测试
测试 exceptions 模块的功能
"""
from fastapi import HTTPException

from app.core.exceptions import (
    APIException,
    AuthenticationError,
    BusinessError,
    DuplicateError,
    NotFound,
    PermissionDenied,
    RateLimitError,
    ValidationError,
)


class TestExceptions:
    """测试异常类"""

    def test_api_exception(self):
        """测试 APIException 异常"""
        exc = APIException(code=500, message="服务器错误")
        assert exc.message == "服务器错误"
        assert exc.code == 500

    def test_not_found_exception(self):
        """测试 NotFound 异常"""
        exc = NotFound("资源不存在")
        assert exc.message == "资源不存在"
        assert exc.code == 404

    def test_validation_error_exception(self):
        """测试 ValidationError 异常"""
        exc = ValidationError("验证失败")
        assert exc.message == "验证失败"
        assert exc.code == 400

    def test_business_error_exception(self):
        """测试 BusinessError 异常"""
        exc = BusinessError("业务错误")
        assert exc.message == "业务错误"
        assert exc.code == 400

    def test_authentication_error_exception(self):
        """测试 AuthenticationError 异常"""
        exc = AuthenticationError("认证失败")
        assert exc.message == "认证失败"
        assert exc.code == 40001

    def test_permission_denied_exception(self):
        """测试 PermissionDenied 异常"""
        exc = PermissionDenied("禁止访问")
        assert exc.message == "禁止访问"
        assert exc.code == 403

    def test_duplicate_error_exception(self):
        """测试 DuplicateError 异常"""
        exc = DuplicateError("数据已存在")
        assert exc.message == "数据已存在"
        assert exc.code == 409

    def test_rate_limit_error_exception(self):
        """测试 RateLimitError 异常"""
        exc = RateLimitError("请求过于频繁")
        assert exc.message == "请求过于频繁"
        assert exc.code == 429

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        assert issubclass(APIException, HTTPException)
        assert issubclass(NotFound, APIException)
        assert issubclass(ValidationError, APIException)
        assert issubclass(BusinessError, APIException)
        assert issubclass(AuthenticationError, APIException)
        assert issubclass(PermissionDenied, APIException)

    def test_exception_with_default_message(self):
        """测试异常默认消息"""
        exc = NotFound()
        assert exc.message == "资源不存在"

        exc2 = ValidationError()
        assert exc2.message == "数据验证失败"

        exc3 = BusinessError()
        assert exc3.message == "业务处理失败"
