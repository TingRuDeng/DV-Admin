# -*- coding: utf-8 -*-
"""
核心模块

包含配置、安全、异常等核心功能。
"""

from app.core.config import Settings, get_settings, settings
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
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    get_token_expiration,
    get_token_subject,
    verify_password,
    verify_token_type,
)
from app.core.security_validator import SecurityValidator

__all__ = [
    # 配置
    "Settings",
    "get_settings",
    "settings",
    # 安全
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token_type",
    "get_token_subject",
    "get_token_expiration",
    # 安全验证器
    "SecurityValidator",
    # 异常
    "APIException",
    "AuthenticationError",
    "PermissionDenied",
    "NotFound",
    "ValidationError",
    "BusinessError",
    "DuplicateError",
    "RateLimitError",
]
