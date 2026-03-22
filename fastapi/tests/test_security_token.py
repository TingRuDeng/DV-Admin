# -*- coding: utf-8 -*-
"""
安全模块扩展测试
测试 security 模块的更多功能
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.core.security import (
    create_access_token,
    decode_token,
    get_token_expiration,
)


class TestSecurityToken:
    """测试令牌功能"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """测试创建带过期时间的令牌"""
        data = {"sub": "test_user", "user_id": 1}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None

    def test_decode_token_invalid(self):
        """测试解码无效令牌"""
        token = "invalid_token_string"
        
        decoded = decode_token(token)
        
        # 无效令牌应该返回 None
        assert decoded is None

    def test_get_token_expiration_missing(self):
        """测试获取缺少过期时间的令牌"""
        data = {"sub": "test_user", "user_id": 1}
        
        expiration = get_token_expiration(data)
        
        # 缺少过期时间应该返回 None
        assert expiration is None
