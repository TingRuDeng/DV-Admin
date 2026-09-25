"""单点登录 state 存储：只用 Redis，任何存储故障都返回 503，没有内存后备。"""

from inspect import isawaitable

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.exceptions import ServiceUnavailable
from app.core.oidc_policy import STATE_TTL_SECONDS, state_key
from app.core.redis import redis_manager

UNAVAILABLE_MESSAGE = "单点登录暂不可用，请稍后重试"


def get_oidc_redis() -> Redis:
    return redis_manager.client


async def save_flow_state(state: str, record: str) -> None:
    """保存发起记录；键是 state 的哈希，值里只有 flowSecret 的哈希。"""
    try:
        pending = get_oidc_redis().set(state_key(state), record, ex=STATE_TTL_SECONDS)
        if isawaitable(pending):
            await pending
    except (RedisError, RuntimeError) as error:
        raise ServiceUnavailable(UNAVAILABLE_MESSAGE) from error


async def pop_flow_state(state: str) -> object:
    """在同一个 MULTI/EXEC 事务里取出并删除记录，保证 state 只能被消费一次。"""
    key = state_key(state)
    try:
        async with get_oidc_redis().pipeline(transaction=True) as pipe:
            pipe.get(key)
            pipe.delete(key)
            raw, _deleted = await pipe.execute()
    except (RedisError, RuntimeError) as error:
        raise ServiceUnavailable(UNAVAILABLE_MESSAGE) from error
    return raw
