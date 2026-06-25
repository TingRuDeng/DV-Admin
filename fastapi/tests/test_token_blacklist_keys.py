"""
Token 黑名单 key 与 Redis 属性测试。
"""
from unittest.mock import MagicMock, patch

from app.services.token_blacklist import TokenBlacklistService

pytest_plugins = ["token_blacklist_fixtures"]


class TestTokenBlacklistKeys:
    """测试 Token 黑名单 key 和 Redis 属性。"""

    def test_get_blacklist_key(self):
        """测试生成黑名单 Key。"""
        service = TokenBlacklistService()
        key = service._get_blacklist_key("test_token_123")

        assert key.startswith("token_blacklist:")
        assert len(key) == len("token_blacklist:") + 32

    def test_get_user_tokens_key(self):
        """测试生成用户 Token 集合 Key。"""
        service = TokenBlacklistService()
        key = service._get_user_tokens_key(123)

        assert key == "user_tokens:123"

    def test_redis_property(self):
        """测试 Redis 属性获取。"""
        service = TokenBlacklistService()

        with patch("app.services.token_blacklist.redis_manager") as mock_manager:
            mock_client = MagicMock()
            mock_manager.client = mock_client

            redis = service.redis
            assert redis is mock_client
