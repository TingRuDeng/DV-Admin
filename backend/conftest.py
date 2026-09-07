import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_admin.settings_test")


@pytest.fixture(scope="session")
def login_redis_server():
    from scripts.redis_test_server import RedisTestServer

    with RedisTestServer() as server:
        yield server


@pytest.fixture(autouse=True)
def isolated_login_counters(monkeypatch, login_redis_server):
    from redis import Redis

    from drf_admin.apps.oauth import login_throttle

    client = Redis.from_url(login_redis_server.url, decode_responses=True)
    client.flushdb()
    monkeypatch.setattr(login_throttle, "get_login_redis", lambda: client)
    try:
        yield client
    finally:
        client.close()
