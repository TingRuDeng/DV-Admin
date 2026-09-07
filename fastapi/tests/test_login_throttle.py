"""Login limits must exercise the real Redis protocol and both HTTP entries."""

from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import FastAPI
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from app.api.v1.oauth.routes import login
from app.core.exceptions import APIException, api_exception_handler
from app.core.login_throttle_policy import rate_limit_keys
from app.core.redis import redis_manager
from app.services import login_throttle
from scripts.redis_test_server import RedisTestServer


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/login/", "/token/"])
async def test_five_failures_cool_account_with_retry_after(monkeypatch, path):
    monkeypatch.setattr(login.Users, "get_or_none", AsyncMock(return_value=None))
    with RedisTestServer() as server:
        redis = Redis.from_url(server.url, decode_responses=True)
        monkeypatch.setattr(redis_manager, "_client", redis)
        monkeypatch.setattr(login_throttle, "get_login_redis", lambda: redis)
        app = FastAPI()
        app.add_exception_handler(APIException, api_exception_handler)
        app.include_router(login.router)
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                responses = []
                for _ in range(6):
                    credentials = {"username": "missing-user", "password": "invalid"}
                    kwargs = {"json" if path == "/login/" else "data": credentials}
                    responses.append(await client.post(path, **kwargs))
                assert all(response.status_code == 401 for response in responses[:4])
                assert responses[4].status_code == responses[5].status_code == 429
                assert 1 <= int(responses[5].headers["Retry-After"]) <= 300
        finally:
            await redis.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/login/", "/token/"])
async def test_login_store_outage_returns_503(monkeypatch, path):
    redis = AsyncMock()
    redis.eval.side_effect = ConnectionError("unavailable")
    monkeypatch.setattr(login_throttle, "get_login_redis", lambda: redis)
    users = AsyncMock()
    monkeypatch.setattr(login.Users, "get_or_none", users)
    app = FastAPI()
    app.include_router(login.router)
    app.add_exception_handler(APIException, api_exception_handler)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        kwargs = {"json" if path == "/login/" else "data": {"username": "account", "password": "old"}}
        response = await client.post(path, **kwargs)
    assert response.status_code == response.json()["code"] == 503
    users.assert_not_called()


@pytest.mark.asyncio
async def test_success_clears_only_account_failures(test_user, isolated_login_counters):
    app = FastAPI()
    app.include_router(login.router)
    app.add_exception_handler(APIException, api_exception_handler)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        for _ in range(4):
            response = await client.post("/login/", json={"username": test_user["username"], "password": "wrong"})
            assert response.status_code == 401
        response = await client.post("/login/", json={"username": test_user["username"], "password": test_user["password"]})
        assert response.status_code == 200
    failures, cooldown, ip_key = rate_limit_keys(test_user["username"], "127.0.0.1")
    assert not await isolated_login_counters.exists(failures, cooldown)
    assert await isolated_login_counters.zcard(ip_key) == 5
