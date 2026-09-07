"""Authentication state against real, isolated Redis and separate clients."""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.v1.oauth.routes import session
from app.core.config import settings
from app.core.exceptions import APIException, ServiceUnavailable, api_exception_handler
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_session_started_at,
)
from app.services.token_blacklist import TokenBlacklistService
from scripts.redis_test_server import RedisTestServer


@pytest.mark.asyncio
async def test_revocation_rotation_and_recovery_across_instances(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    with RedisTestServer() as server:
        clients = [Redis.from_url(server.url, decode_responses=True, socket_connect_timeout=0.1,
                                  socket_timeout=0.1) for _ in range(2)]
        first, second = TokenBlacklistService(), TokenBlacklistService()
        first._redis, second._redis = clients
        try:
            access = create_access_token("87654")
            assert await first.add_token_to_blacklist(access, 87654)
            assert await second.is_token_blacklisted(access)

            refresh = create_refresh_token("87654")
            outcomes = await asyncio.gather(
                first.consume_refresh_token(refresh, 87654),
                second.consume_refresh_token(refresh, 87654),
            )
            assert sorted(outcomes) == [False, True]

            unconsumed = create_refresh_token("87654")
            issued_at = datetime.now(timezone.utc) - timedelta(seconds=1)
            assert await first.revoke_all_user_tokens(87654)
            assert await second.is_user_tokens_revoked(87654, issued_at)
            assert not await second.consume_refresh_token(unconsumed, 87654)

            server.stop()
            with pytest.raises(ServiceUnavailable):
                await second.is_token_blacklisted(access)
            server.start()
            assert await second.is_token_blacklisted(access)
            assert await second.is_user_tokens_revoked(87654, issued_at)
        finally:
            for client in clients:
                await client.aclose()


@pytest.mark.asyncio
async def test_refresh_preserves_session_age_for_later_revocation(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    started = datetime.now(timezone.utc) - timedelta(minutes=5)
    refresh = create_refresh_token("87655", session_started_at=started)
    user = SimpleNamespace(id=87655, is_active=True, username="test", name="test")
    monkeypatch.setattr(session.Users, "get_or_none", AsyncMock(return_value=user))
    with RedisTestServer() as server:
        store = TokenBlacklistService()
        redis = Redis.from_url(server.url, decode_responses=True)
        store._redis = redis
        monkeypatch.setattr(session, "token_blacklist_service", store)
        app = FastAPI()
        app.include_router(session.router)
        app.add_exception_handler(APIException, api_exception_handler)
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/refresh-token/", json={"refreshToken": refresh})
                assert response.status_code == 200
                tokens = response.json()["data"]
                for value in (tokens["accessToken"], tokens["refreshToken"]):
                    assert get_token_session_started_at(decode_token(value)) == started
                assert await store.revoke_all_user_tokens(user.id)
                denied = await client.post("/refresh-token/", json={"refreshToken": tokens["refreshToken"]})
                assert denied.status_code == 401
                assert denied.json()["code"] == 40002
                assert await store.is_user_tokens_revoked(user.id, started)
        finally:
            await redis.aclose()
