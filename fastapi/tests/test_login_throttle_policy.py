"""Boundary and concurrency tests for the policy packaged by both backends."""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from redis import Redis

from app.core import login_throttle_policy
from app.core.login_throttle_policy import (
    LOGIN_SCRIPT,
    rate_limit_keys,
    retry_seconds,
    script_arguments,
    trusted_client_ip,
)
from scripts.redis_test_server import RedisTestServer


def test_backends_ship_identical_login_policy():
    root = Path(__file__).resolve().parents[2]
    assert (root / "fastapi/app/core/login_throttle_policy.py").read_bytes() == (
        root / "backend/drf_admin/apps/oauth/login_throttle_policy.py"
    ).read_bytes()


@pytest.mark.parametrize("peer,forwarded,networks,expected", [
    ("192.0.2.4", "198.51.100.8", "", "192.0.2.4"),
    ("192.0.2.4", "198.51.100.8", "10.0.0.0/8", "192.0.2.4"),
    ("10.0.0.1", "198.51.100.8, 10.0.0.2", "10.0.0.0/8", "198.51.100.8"),
    ("10.0.0.1", "1.1.1.1, 198.51.100.8", "10.0.0.0/8", "198.51.100.8"),
    ("10.0.0.1", "spoofed", "10.0.0.0/8", "10.0.0.1"),
    ("::1", "2001:db8::3", "::1/128", "2001:db8::3"),
])
def test_only_trusted_proxy_chain_is_used(peer, forwarded, networks, expected):
    assert trusted_client_ip(peer, forwarded, networks) == expected


def test_account_aliases_share_key_and_retry_rounds_up():
    assert rate_limit_keys(" ADMIN ", "127.0.0.1") == rate_limit_keys("admin", "127.0.0.1")
    assert retry_seconds(1001) == 2


def evaluate(redis, action, username="account", ip="192.0.2.1"):
    return int(redis.eval(LOGIN_SCRIPT, 3, *rate_limit_keys(username, ip), *script_arguments(action)))


def test_cooldown_window_success_reset_and_ip_window():
    with RedisTestServer() as server, Redis.from_url(server.url) as redis:
        failures, cooldown, ip_key = rate_limit_keys("account", "192.0.2.1")
        for _ in range(4):
            assert evaluate(redis, "check") == 0
            assert evaluate(redis, "failure") == 0
        assert evaluate(redis, "success") == 0
        assert not redis.exists(failures)
        assert redis.zcard(ip_key) == 4
        for _ in range(4):
            assert evaluate(redis, "failure") == 0
        assert 299_000 <= evaluate(redis, "failure") <= 300_000
        redis.pexpire(cooldown, 90_000)
        assert 0 < evaluate(redis, "check", ip="192.0.2.2") <= 90_000
        assert 0 < evaluate(redis, "failure") <= 90_000
        assert redis.pttl(cooldown) <= 90_000
        redis.pexpire(cooldown, 0)
        assert evaluate(redis, "check") == 0
        assert evaluate(redis, "failure") == 0
        redis.pexpire(failures, 0)
        assert evaluate(redis, "failure") == 0
        assert redis.zcard(failures) == 1

        seconds, micros = redis.time()
        earlier = seconds * 1000 + micros // 1000 - 30_000
        redis.delete(ip_key)
        redis.zadd(ip_key, {str(index): earlier for index in range(60)})
        redis.pexpire(ip_key, 30_000)
        assert 0 < evaluate(redis, "check", username="another") <= 30_000
        assert redis.zcard(ip_key) == 60
        assert redis.pttl(ip_key) <= 30_000
        redis.pexpire(ip_key, 0)
        assert evaluate(redis, "check", username="another") == 0


def test_ip_limit_is_atomic_across_connections():
    with RedisTestServer() as server, Redis.from_url(server.url) as first, Redis.from_url(server.url) as second:
        def attempt(index):
            client = first if index % 2 else second
            return evaluate(client, "check", username=f"account-{index}")

        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(attempt, range(80)))
        assert results.count(0) == 60
        assert all(0 < value <= 60_000 for value in results if value)


def test_failures_spanning_window_boundary_still_count(monkeypatch):
    monkeypatch.setattr(login_throttle_policy, "ACCOUNT_WINDOW_MS", 1000)
    with RedisTestServer() as server, Redis.from_url(server.url) as redis:
        assert evaluate(redis, "failure") == 0
        time.sleep(0.65)
        for _ in range(3):
            assert evaluate(redis, "failure") == 0
        time.sleep(0.45)
        assert evaluate(redis, "failure") == 0
        assert evaluate(redis, "failure") > 0
