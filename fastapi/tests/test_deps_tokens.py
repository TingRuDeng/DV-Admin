"""
认证依赖 Token helper 测试。
"""

from unittest.mock import patch

import pytest

from app.api.deps_tokens import (
    extract_bearer_token,
    require_access_token_payload,
    require_token_user_id,
)
from app.core.exceptions import AuthenticationError


def test_extract_bearer_token_prefers_oauth_token():
    """OAuth2 scheme token 应优先于 Authorization 头。"""
    token = extract_bearer_token("oauth-token", "Bearer header-token")

    assert token == "oauth-token"


def test_extract_bearer_token_from_authorization_header():
    """应从标准 Bearer 头提取 token。"""
    token = extract_bearer_token(None, "Bearer header-token")

    assert token == "header-token"


def test_extract_bearer_token_rejects_non_bearer_header():
    """非 Bearer 认证头不应被当成 token。"""
    token = extract_bearer_token(None, "Basic abc")

    assert token is None


def test_require_access_token_payload_returns_access_payload():
    """有效 access token 应返回 payload。"""
    with patch("app.api.deps_tokens.decode_token") as mock_decode, \
         patch("app.api.deps_tokens.verify_token_type") as mock_verify:
        mock_decode.return_value = {"sub": "1", "type": "access"}
        mock_verify.return_value = True

        payload = require_access_token_payload("token")

    assert payload == {"sub": "1", "type": "access"}


def test_require_access_token_payload_rejects_invalid_token():
    """解码失败时应抛认证错误。"""
    with patch("app.api.deps_tokens.decode_token") as mock_decode:
        mock_decode.return_value = None

        with pytest.raises(AuthenticationError, match="无效的认证令牌"):
            require_access_token_payload("token")


def test_require_access_token_payload_rejects_wrong_token_type():
    """非 access token 应抛认证错误。"""
    with patch("app.api.deps_tokens.decode_token") as mock_decode, \
         patch("app.api.deps_tokens.verify_token_type") as mock_verify:
        mock_decode.return_value = {"sub": "1", "type": "refresh"}
        mock_verify.return_value = False

        with pytest.raises(AuthenticationError, match="无效的令牌类型"):
            require_access_token_payload("token")


def test_require_token_user_id_returns_int_id():
    """payload subject 应转换为 int 用户 ID。"""
    with patch("app.api.deps_tokens.get_token_subject") as mock_subject:
        mock_subject.return_value = "123"

        user_id = require_token_user_id({"sub": "123"})

    assert user_id == 123


def test_require_token_user_id_rejects_missing_subject():
    """缺少 subject 时应抛认证错误。"""
    with patch("app.api.deps_tokens.get_token_subject") as mock_subject:
        mock_subject.return_value = None

        with pytest.raises(AuthenticationError, match="无法获取用户信息"):
            require_token_user_id({})
