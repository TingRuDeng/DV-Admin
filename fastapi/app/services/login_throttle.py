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


def get_login_redis() -> Redis:
    return redis_manager.client


async def enforce_login_limit(action: str, username: str, client_ip: str) -> None:
    try:
        pending = get_login_redis().eval(
            LOGIN_SCRIPT, 3, *rate_limit_keys(username, client_ip), *script_arguments(action),
        )
        result = await pending if isawaitable(pending) else pending
    except (RedisError, RuntimeError) as error:
        raise ServiceUnavailable("登录保护暂不可用，请稍后重试") from error
    if int(result) > 0:
        raise RateLimitError(retry_after=retry_seconds(int(result)))
