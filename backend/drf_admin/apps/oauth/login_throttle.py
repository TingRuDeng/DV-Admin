"""登录必须通过 Redis 原子限速，不退回进程内缓存。"""

from django_redis import get_redis_connection
from redis.exceptions import RedisError
from rest_framework.exceptions import APIException, Throttled

from drf_admin.apps.oauth.login_throttle_policy import (
    LOGIN_SCRIPT,
    rate_limit_keys,
    retry_seconds,
    script_arguments,
)


class LoginProtectionUnavailable(APIException):
    status_code = 503
    default_detail = "登录保护暂不可用，请稍后重试"


def get_login_redis():
    return get_redis_connection("default")


def enforce_login_limit(action, username, client_ip):
    try:
        result = get_login_redis().eval(
            LOGIN_SCRIPT, 3, *rate_limit_keys(username, client_ip), *script_arguments(action)
        )
    except (RedisError, NotImplementedError, ConnectionError) as error:
        raise LoginProtectionUnavailable() from error
    if int(result) > 0:
        raise Throttled(wait=retry_seconds(int(result)), detail="请求过于频繁，请稍后重试")
