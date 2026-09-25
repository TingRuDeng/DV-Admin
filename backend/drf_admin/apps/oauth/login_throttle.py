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

# 本地缓存后端没有 Redis 客户端时 django_redis 抛 NotImplementedError
REDIS_ERRORS = (RedisError, NotImplementedError, ConnectionError)
# 单点登录只按 IP 限速；这两个账号键不会被密码登录写入，检查时恒为空
OIDC_ACCOUNT_KEYS = ("login:oidc:failures", "login:oidc:cooldown")


class LoginProtectionUnavailable(APIException):
    status_code = 503
    default_detail = "登录保护暂不可用，请稍后重试"


def get_login_redis():
    return get_redis_connection("default")


def _run_login_script(keys, action):
    try:
        result = get_login_redis().eval(LOGIN_SCRIPT, 3, *keys, *script_arguments(action))
    except REDIS_ERRORS as error:
        raise LoginProtectionUnavailable() from error
    if int(result) > 0:
        raise Throttled(wait=retry_seconds(int(result)), detail="请求过于频繁，请稍后重试")


def enforce_login_limit(action, username, client_ip):
    _run_login_script(rate_limit_keys(username, client_ip), action)


def enforce_ip_limit(client_ip):
    _run_login_script((*OIDC_ACCOUNT_KEYS, rate_limit_keys("", client_ip)[2]), "check")
