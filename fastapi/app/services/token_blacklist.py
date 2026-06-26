"""
Token 黑名单服务

管理 JWT Token 的黑名单，用于登出和令牌撤销。
"""

from datetime import datetime, timezone

from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_manager
from app.core.security import decode_token, get_token_expiration
from app.services.token_blacklist_compat import TokenBlacklistCompatibilityMixin
from app.services.token_blacklist_keys import (
    BLACKLIST_PREFIX,
    USER_TOKENS_PREFIX,
    get_blacklist_key,
    get_user_revocation_key,
    get_user_tokens_key,
)
from app.services.token_blacklist_memory import TokenBlacklistMemoryStore
from app.services.token_blacklist_records import (
    build_token_blacklist_record,
    build_user_revocation_record,
    is_token_revoked_by_time,
)


class TokenBlacklistService(TokenBlacklistCompatibilityMixin):
    """Token 黑名单服务，优先使用 Redis，Redis 不可用时降级到内存。"""

    BLACKLIST_PREFIX = BLACKLIST_PREFIX
    USER_TOKENS_PREFIX = USER_TOKENS_PREFIX

    def __init__(self):
        self._redis: Redis | None = None
        self._memory_store = TokenBlacklistMemoryStore()

    @property
    def redis(self) -> Redis:
        """获取 Redis 客户端。"""
        if self._redis is None:
            self._redis = redis_manager.client
        return self._redis

    def _get_redis_or_none(self) -> Redis | None:
        try:
            return self.redis
        except RuntimeError as exc:
            logger.warning(f"Redis 不可用，Token 黑名单降级到内存模式: {exc}")
            return None

    def _get_blacklist_key(self, token: str) -> str:
        """生成黑名单 Key。"""
        return get_blacklist_key(token)

    def _get_user_tokens_key(self, user_id: int) -> str:
        """生成用户 Token 集合 Key。"""
        return get_user_tokens_key(user_id)

    async def add_token_to_blacklist(
        self,
        token: str,
        user_id: int | None = None,
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

            expiration = get_token_expiration(payload)
            if not expiration:
                logger.warning("无法获取 Token 过期时间，跳过黑名单添加")
                return False

            now = datetime.now(timezone.utc)
            record = build_token_blacklist_record(
                token=token,
                user_id=user_id,
                reason=reason,
                expires_at=expiration,
                revoked_at=now,
            )
            if record is None:
                logger.debug("Token 已过期，无需加入黑名单")
                return True

            redis = self._get_redis_or_none()
            if redis is None:
                self._memory_store.add_token(record.key, record.expires_at)
                return True

            await redis.setex(
                record.key,
                record.ttl,
                str(record.value),
            )

            logger.info(f"Token 已加入黑名单，TTL: {record.ttl}秒，原因: {reason}")
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
            redis = self._get_redis_or_none()
            if redis is None:
                return self._memory_store.has_token(key)

            exists = await redis.exists(key)
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
            now = datetime.now(timezone.utc)
            record = build_user_revocation_record(
                user_id=user_id,
                refresh_token_expire_days=settings.refresh_token_expire_days,
                revoked_at=now,
            )
            redis = self._get_redis_or_none()
            if redis is None:
                self._memory_store.revoke_user(user_id, record.revoked_at)
                return True

            await redis.setex(
                record.key,
                record.ttl,
                record.revoked_at.isoformat(),
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
            key = get_user_revocation_key(user_id)
            redis = self._get_redis_or_none()
            if redis is None:
                return self._memory_store.is_user_revoked(user_id, token_issued_at)

            revoked_at_str = await redis.get(key)

            if not revoked_at_str:
                return False

            return is_token_revoked_by_time(token_issued_at, revoked_at_str)

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
            redis = self._get_redis_or_none()
            if redis is None:
                self._memory_store.remove_token(key)
                return True

            await redis.delete(key)
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
            key = get_user_revocation_key(user_id)
            redis = self._get_redis_or_none()
            if redis is None:
                self._memory_store.clear_user_revocation(user_id)
                return True

            await redis.delete(key)
            logger.info(f"已清除用户 {user_id} 的 Token 撤销标记")
            return True
        except RedisError as e:
            logger.error(f"清除用户 Token 撤销标记失败: {e}")
            return False


# 全局 Token 黑名单服务实例
token_blacklist_service = TokenBlacklistService()
