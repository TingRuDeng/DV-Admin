"""Shared login policy; keep the two packaged backend copies byte-identical."""

import hashlib
import ipaddress
import math
import unicodedata
import uuid

ACCOUNT_FAILURE_LIMIT = 5
ACCOUNT_WINDOW_MS = 300_000
ACCOUNT_COOLDOWN_MS = 300_000
IP_ATTEMPT_LIMIT = 60
IP_WINDOW_MS = 60_000

LOGIN_SCRIPT = """
local action = ARGV[1]
local clock = redis.call('TIME')
local now = tonumber(clock[1]) * 1000 + math.floor(tonumber(clock[2]) / 1000)
local function count_recent(key, window)
    redis.call('ZREMRANGEBYSCORE', key, '-inf', now - tonumber(window))
    return redis.call('ZCARD', key)
end
if action == 'check' then
    local attempts = count_recent(KEYS[3], ARGV[6])
    if attempts >= tonumber(ARGV[5]) then
        local oldest = redis.call('ZRANGE', KEYS[3], 0, 0, 'WITHSCORES')
        return math.max(1, tonumber(oldest[2]) + tonumber(ARGV[6]) - now)
    end
    redis.call('ZADD', KEYS[3], now, ARGV[7])
    redis.call('PEXPIRE', KEYS[3], ARGV[6])
    return math.max(0, redis.call('PTTL', KEYS[2]))
elseif action == 'failure' then
    local cooldown = redis.call('PTTL', KEYS[2])
    if cooldown > 0 then return cooldown end
    local failures = count_recent(KEYS[1], ARGV[3]) + 1
    redis.call('ZADD', KEYS[1], now, ARGV[7])
    redis.call('PEXPIRE', KEYS[1], ARGV[3])
    if failures >= tonumber(ARGV[2]) then
        redis.call('SET', KEYS[2], '1', 'PX', ARGV[4], 'NX')
        redis.call('DEL', KEYS[1])
        return redis.call('PTTL', KEYS[2])
    end
elseif action == 'success' then
    redis.call('DEL', KEYS[1])
end
return 0
"""


def rate_limit_keys(username: str, client_ip: str) -> tuple[str, str, str]:
    account = unicodedata.normalize("NFKC", username).strip().casefold()
    account_hash = hashlib.sha256(account.encode("utf-8")).hexdigest()
    ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
    return (
        f"login:failures:{account_hash}",
        f"login:cooldown:{account_hash}",
        f"login:ip:{ip_hash}",
    )


def script_arguments(action: str) -> tuple:
    return (action, ACCOUNT_FAILURE_LIMIT, ACCOUNT_WINDOW_MS, ACCOUNT_COOLDOWN_MS,
            IP_ATTEMPT_LIMIT, IP_WINDOW_MS, uuid.uuid4().hex)


def retry_seconds(milliseconds: int) -> int:
    return max(1, math.ceil(milliseconds / 1000))


def trusted_client_ip(peer: str, forwarded: str, trusted_proxies: str) -> str:
    """Walk X-Forwarded-For from the trusted peer towards the first untrusted hop."""
    try:
        address = ipaddress.ip_address(peer)
    except ValueError:
        return "unknown"
    networks = [
        ipaddress.ip_network(item.strip(), strict=False)
        for item in trusted_proxies.split(",") if item.strip()
    ]
    if not any(address in network for network in networks) or not forwarded:
        return str(address)
    try:
        hops = [ipaddress.ip_address(item.strip()) for item in forwarded.split(",")]
    except ValueError:
        return str(address)
    for hop in reversed(hops):
        address = hop
        if not any(hop in network for network in networks):
            break
    return str(address)
