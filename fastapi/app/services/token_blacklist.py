# -*- coding: utf-8 -*-
"""
Token 黑名单服务

管理 JWT Token 的黑名单，用于登出和令牌撤销。
"""

from datetime import datetime, timezone
from typing import Dict, Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_manager
from app.core.security import decode_token, get_token_expiration
from loguru import logger


class TokenBlacklistService:
    """
    Token 黑名单服务

    使用 Redis 存储被撤销的 Token。
    黑名单的 Key 格式: token_blacklist:{token_jti}
    """

    # 黑名单 Key 前缀
    BLACKLIST_PREFIX = "token_blacklist"
    # 用户 Token 集合 Key 前缀
    USER_TOKENS_PREFIX = "user_tokens"

    def __init__(self):
        """初始化服务"""
        self._redis: Optional[Redis] = None

    @property
    def redis(self) -> Redis:
        """
        获取 Redis 客户端

        Returns:
            Redis 客户端实例
        """
        if self._redis is None:
            self._redis = redis_manager.client
        return self._redis

    def _get_blacklist_key(self, token: str) -> str:
        """
        生成黑名单 Key

        Args:
            token: JWT Token

        Returns:
            黑名单 Key
        """
        # 使用 token 的哈希值作为 key，避免 token 过长
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
        return f"{self.BLACKLIST_PREFIX}:{token_hash}"

    def _get_user_tokens_key(self, user_id: int) -> str:
        """
        生成用户 Token 集合 Key

        Args:
            user_id: 用户 ID

        Returns:
            用户 Token 集合 Key
        """
        return f"{self.USER_TOKENS_PREFIX}:{user_id}"

    async def add_token_to_blacklist(
        self,
        token: str,
        user_id: Optional[int] = None,
        reason: str = "logout",
    ) -> bool:
        """
        将 Token 加入黑名单

        Args:
            token: JWT Token
            user_id: 用户 ID（可选）
            reason: 加入黑名单的原因

        Returns:
            是否成功
        """
        try:
            # 解码 Token 获取过期时间
            payload = decode_token(token)
            if not payload:
                logger.warning("无法解码 Token，跳过黑名单添加")
                return False

            # 计算剩余过期时间
            expiration = get_token_expiration(payload)
            if not expiration:
                logger.warning("无法获取 Token 过期时间，跳过黑名单添加")
                return False

            now = datetime.now(timezone.utc)
            ttl = int((expiration - now).total_seconds())

            # 如果 Token 已过期，不需要加入黑名单
            if ttl <= 0:
                logger.debug("Token 已过期，无需加入黑名单")
                return True

            # 存储到黑名单
            key = self._get_blacklist_key(token)
            value = {
                "user_id": user_id,
                "reason": reason,
                "revoked_at": now.isoformat(),
            }

            # 使用 Redis 的 setex 命令设置带过期时间的 key
            await self.redis.setex(
                key,
                ttl,
                str(value),
            )

            logger.info(f"Token 已加入黑名单，TTL: {ttl}秒，原因: {reason}")
            return True

        except RedisError as e:
            logger.error(f"添加 Token 到黑名单失败: {e}")
            return False
        except Exception as e:
            logger.error(f"添加 Token 到黑名单时发生错误: {e}")
            return False

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        检查 Token 是否在黑名单中

        Args:
            token: JWT Token

        Returns:
            是否在黑名单中
        """
        try:
            key = self._get_blacklist_key(token)
            exists = await self.redis.exists(key)
            return exists > 0
        except RedisError as e:
            logger.error(f"检查 Token 黑名单失败: {e}")
            # Redis 出错时，为了安全起见，不阻止访问
            return False
        except Exception as e:
            logger.error(f"检查 Token 黑名单时发生错误: {e}")
            return False

    async def revoke_all_user_tokens(self, user_id: int, reason: str = "force_logout") -> bool:
        """
        撤销用户的所有 Token

        通过在 Redis 中存储用户的登出时间戳来实现。
        所有在此时间之前签发的 Token 都将被视为无效。

        Args:
            user_id: 用户 ID
            reason: 撤销原因

        Returns:
            是否成功
        """
        try:
            key = f"{self.BLACKLIST_PREFIX}:user:{user_id}"
            now = datetime.now(timezone.utc)

            # 存储用户的强制登出时间
            # 使用 refresh_token 的过期时间作为 TTL
            ttl = settings.refresh_token_expire_days * 24 * 60 * 60

            await self.redis.setex(
                key,
                ttl,
                now.isoformat(),
            )

            logger.info(f"已撤销用户 {user_id} 的所有 Token，原因: {reason}")
            return True

        except RedisError as e:
            logger.error(f"撤销用户所有 Token 失败: {e}")
            return False

    async def is_user_tokens_revoked(self, user_id: int, token_issued_at: datetime) -> bool:
        """
        检查用户的 Token 是否已被批量撤销

        Args:
            user_id: 用户 ID
            token_issued_at: Token 的签发时间

        Returns:
            是否已被撤销
        """
        try:
            key = f"{self.BLACKLIST_PREFIX}:user:{user_id}"
            revoked_at_str = await self.redis.get(key)

            if not revoked_at_str:
                return False

            revoked_at = datetime.fromisoformat(revoked_at_str)
            # 如果 Token 的签发时间早于撤销时间，则视为已撤销
            return token_issued_at < revoked_at

        except RedisError as e:
            logger.error(f"检查用户 Token 撤销状态失败: {e}")
            return False
        except Exception as e:
            logger.error(f"检查用户 Token 撤销状态时发生错误: {e}")
            return False

    async def remove_token_from_blacklist(self, token: str) -> bool:
        """
        从黑名单中移除 Token（仅用于测试或特殊场景）

        Args:
            token: JWT Token

        Returns:
            是否成功
        """
        try:
            key = self._get_blacklist_key(token)
            await self.redis.delete(key)
            logger.info("Token 已从黑名单移除")
            return True
        except RedisError as e:
            logger.error(f"从黑名单移除 Token 失败: {e}")
            return False

    async def clear_user_revocation(self, user_id: int) -> bool:
        """
        清除用户的 Token 撤销标记（仅用于测试或特殊场景）

        Args:
            user_id: 用户 ID

        Returns:
            是否成功
        """
        try:
            key = f"{self.BLACKLIST_PREFIX}:user:{user_id}"
            await self.redis.delete(key)
            logger.info(f"已清除用户 {user_id} 的 Token 撤销标记")
            return True
        except RedisError as e:
            logger.error(f"清除用户 Token 撤销标记失败: {e}")
            return False


# 全局 Token 黑名单服务实例
token_blacklist_service = TokenBlacklistService()
