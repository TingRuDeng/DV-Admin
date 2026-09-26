"""Redis-backed login limits. Storage failures never permit unmetered login."""

from inspect import isawaitable

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.exceptions import RateLimitError, ServiceUnavailable
from app.core.login_throttle_policy import (
    LOGIN_SCRIPT,
    rate_limit_keys,
    retry_seconds,
    script_arguments,
)
from app.core.redis import redis_manager

# 单点登录只按 IP 限速；密码登录从不写这两个账号键，所以脚本里只有 IP 桶生效。
OIDC_ACCOUNT_KEYS = ("login:oidc:failures", "login:oidc:cooldown")


def get_login_redis() -> Redis:
    return redis_manager.client


async def _run_login_script(keys: tuple[str, str, str], action: str) -> None:
    try:
        pending = get_login_redis().eval(LOGIN_SCRIPT, 3, *keys, *script_arguments(action))
        result = await pending if isawaitable(pending) else pending
    except (RedisError, RuntimeError) as error:
        raise ServiceUnavailable("登录保护暂不可用，请稍后重试") from error
    if int(result) > 0:
        raise RateLimitError(retry_after=retry_seconds(int(result)))


async def enforce_login_limit(action: str, username: str, client_ip: str) -> None:
    await _run_login_script(rate_limit_keys(username, client_ip), action)


async def enforce_ip_limit(client_ip: str) -> None:
    """单点登录端点的每 IP 限速，与密码登录共用同一 IP 桶。"""
    await _run_login_script((*OIDC_ACCOUNT_KEYS, rate_limit_keys("", client_ip)[2]), "check")
