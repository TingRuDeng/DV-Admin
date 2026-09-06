"""
安全模块扩展测试
测试 security 模块的更多功能
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiration,
    get_token_issued_at,
)
from app.services.token_blacklist_records import is_token_revoked_by_time


class TestSecurityToken:
    """测试令牌功能"""

    def test_same_second_tokens_preserve_revocation_order(self):
        revoked_at = datetime(2026, 1, 1, microsecond=500000, tzinfo=timezone.utc)
        for create_token in (create_access_token, create_refresh_token):
            for delta, expected in ((-100000, True), (100000, False)):
                issued_at = revoked_at + timedelta(microseconds=delta)
                with patch("app.core.security.datetime") as clock:
                    clock.now.return_value = issued_at
                    payload = decode_token(create_token("1", expires_delta=timedelta(days=3650)))
                assert payload is not None
                decoded_time = get_token_issued_at(payload)
                assert decoded_time == issued_at
                assert is_token_revoked_by_time(decoded_time, revoked_at.isoformat()) is expected

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

    def test_refresh_tokens_have_unique_ids(self):
        """同一用户连续签发的刷新令牌也必须保持唯一。"""
        first = create_refresh_token("1")
        second = create_refresh_token("1")

        first_payload = decode_token(first)
        second_payload = decode_token(second)

        assert first != second
        assert first_payload is not None
        assert second_payload is not None
        assert first_payload["jti"] != second_payload["jti"]
