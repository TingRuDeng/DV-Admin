"""
Token 黑名单服务测试
测试 app/services/token_blacklist.py 的功能
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.token_blacklist import TokenBlacklistService, token_blacklist_service


class TestTokenBlacklistService:
    """测试 Token 黑名单服务"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置服务的 redis 客户端
        token_blacklist_service._redis = None

    def test_get_blacklist_key(self):
        """测试生成黑名单 Key"""
        service = TokenBlacklistService()
        token = "test_token_123"
        key = service._get_blacklist_key(token)

        assert key.startswith("token_blacklist:")
        # 应该是 token 哈希值的前 32 位
        assert len(key) == len("token_blacklist:") + 32

    def test_get_user_tokens_key(self):
        """测试生成用户 Token 集合 Key"""
        service = TokenBlacklistService()
        user_id = 123
        key = service._get_user_tokens_key(user_id)

        assert key == "user_tokens:123"

    def test_redis_property(self):
        """测试 Redis 属性获取"""
        service = TokenBlacklistService()

        with patch('app.services.token_blacklist.redis_manager') as mock_manager:
            mock_client = MagicMock()
            mock_manager.client = mock_client

            redis = service.redis
            assert redis is mock_client

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_success(self):
        """测试添加 Token 到黑名单成功"""
        service = TokenBlacklistService()

        # 创建 mock redis
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        service._redis = mock_redis

        # 创建有效的 token payload
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(hours=1)

        with patch('app.services.token_blacklist.decode_token') as mock_decode, \
             patch('app.services.token_blacklist.get_token_expiration') as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist(
                "test_token",
                user_id=1,
                reason="logout"
            )

            assert result is True
            mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_decode_failed(self):
        """测试添加 Token 到黑名单（解码失败）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        with patch('app.services.token_blacklist.decode_token') as mock_decode:
            mock_decode.return_value = None

            result = await service.add_token_to_blacklist("invalid_token")

            assert result is False
            mock_redis.setex.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_no_expiration(self):
        """测试添加 Token 到黑名单（无过期时间）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        with patch('app.services.token_blacklist.decode_token') as mock_decode, \
             patch('app.services.token_blacklist.get_token_expiration') as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = None

            result = await service.add_token_to_blacklist("test_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_expired(self):
        """测试添加已过期的 Token 到黑名单"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        service._redis = mock_redis

        # 创建已过期的 token
        now = datetime.now(timezone.utc)
        expiration = now - timedelta(hours=1)  # 已过期

        with patch('app.services.token_blacklist.decode_token') as mock_decode, \
             patch('app.services.token_blacklist.get_token_expiration') as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist("expired_token")

            # 已过期的 token 不需要加入黑名单
            assert result is True
            mock_redis.setex.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist_redis_error(self):
        """测试添加 Token 到黑名单（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.setex = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        now = datetime.now(timezone.utc)
        expiration = now + timedelta(hours=1)

        with patch('app.services.token_blacklist.decode_token') as mock_decode, \
             patch('app.services.token_blacklist.get_token_expiration') as mock_expiration:
            mock_decode.return_value = {"sub": "user123"}
            mock_expiration.return_value = expiration

            result = await service.add_token_to_blacklist("test_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_true(self):
        """测试检查 Token 是否在黑名单中（存在）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.is_token_blacklisted("blacklisted_token")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_false(self):
        """测试检查 Token 是否在黑名单中（不存在）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        service._redis = mock_redis

        result = await service.is_token_blacklisted("valid_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_redis_error(self):
        """测试检查 Token 黑名单（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.exists = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.is_token_blacklisted("test_token")

        # Redis 出错时返回 False，不阻止访问
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_success(self):
        """测试撤销用户所有 Token 成功"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        service._redis = mock_redis

        result = await service.revoke_all_user_tokens(123, "force_logout")

        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_redis_error(self):
        """测试撤销用户所有 Token（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.setex = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.revoke_all_user_tokens(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_true(self):
        """测试检查用户 Token 是否被批量撤销（已撤销）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        now = datetime.now(timezone.utc)
        revoked_time = now - timedelta(hours=1)
        mock_redis.get = AsyncMock(return_value=revoked_time.isoformat())
        service._redis = mock_redis

        # Token 签发时间早于撤销时间
        token_issued_at = now - timedelta(hours=2)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_false_not_revoked(self):
        """测试检查用户 Token 是否被批量撤销（未撤销）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        service._redis = mock_redis

        token_issued_at = datetime.now(timezone.utc) - timedelta(hours=1)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_false_after_revoked(self):
        """测试检查用户 Token 是否被批量撤销（签发时间晚于撤销时间）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        now = datetime.now(timezone.utc)
        revoked_time = now - timedelta(hours=2)
        mock_redis.get = AsyncMock(return_value=revoked_time.isoformat())
        service._redis = mock_redis

        # Token 签发时间晚于撤销时间
        token_issued_at = now - timedelta(hours=1)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_tokens_revoked_redis_error(self):
        """测试检查用户 Token 撤销状态（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        token_issued_at = datetime.now(timezone.utc)

        result = await service.is_user_tokens_revoked(123, token_issued_at)

        assert result is False

    @pytest.mark.asyncio
    async def test_remove_token_from_blacklist_success(self):
        """测试从黑名单移除 Token 成功"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.remove_token_from_blacklist("test_token")

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_token_from_blacklist_redis_error(self):
        """测试从黑名单移除 Token（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.delete = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.remove_token_from_blacklist("test_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_user_revocation_success(self):
        """测试清除用户 Token 撤销标记成功"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        service._redis = mock_redis

        result = await service.clear_user_revocation(123)

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_user_revocation_redis_error(self):
        """测试清除用户 Token 撤销标记（Redis 错误）"""
        service = TokenBlacklistService()

        mock_redis = AsyncMock()
        from redis.exceptions import RedisError
        mock_redis.delete = AsyncMock(side_effect=RedisError("Connection lost"))
        service._redis = mock_redis

        result = await service.clear_user_revocation(123)

        assert result is False
