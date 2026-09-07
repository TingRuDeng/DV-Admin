"""Security storage failures must not masquerade as valid authentication."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, PropertyMock, patch

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from redis.exceptions import RedisError

from app.api import health
from app.core.config import settings
from app.core.exceptions import APIException, api_exception_handler
from app.core.security import create_access_token, create_refresh_token
from app.services.token_blacklist import TokenBlacklistService


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["read_token", "read_user", "write_token", "write_user", "refresh"])
@pytest.mark.parametrize("failure", ["missing", "connection"])
async def test_production_storage_failure_is_unavailable(monkeypatch, operation, failure):
    monkeypatch.setattr(settings, "app_env", "production")
    service = TokenBlacklistService()
    redis = AsyncMock()
    for method in ("get", "exists", "set", "setex"):
        getattr(redis, method).side_effect = RedisError("test storage unavailable")
    service._redis = redis

    async def call():
        if operation == "read_token":
            return await service.is_token_blacklisted(create_access_token("1"))
        if operation == "read_user":
            return await service.is_user_tokens_revoked(1, datetime.now(timezone.utc))
        if operation == "write_token":
            return await service.add_token_to_blacklist(create_access_token("1"), 1)
        if operation == "write_user":
            return await service.revoke_all_user_tokens(1)
        return await service.consume_refresh_token(create_refresh_token("1"), 1)

    with patch.object(TokenBlacklistService, "redis", new_callable=PropertyMock) as client:
        if failure == "missing":
            client.side_effect = RuntimeError("test Redis not initialized")
        else:
            client.return_value = redis
        with pytest.raises(HTTPException) as error:
            await call()
    assert error.value.status_code == 503


@pytest.mark.asyncio
@pytest.mark.parametrize("database,redis", [
    ("unhealthy", "healthy"),
    ("healthy", "unhealthy"),
    ("healthy", "not_configured"),
    ("healthy", "unavailable"),
])
async def test_production_readiness_returns_http_503(monkeypatch, database, redis):
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(health, "check_database", AsyncMock(return_value={"status": database}))
    monkeypatch.setattr(health, "check_redis", AsyncMock(return_value={"status": redis}))
    app = FastAPI()
    app.include_router(health.router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")
        live = await client.get("/health/live")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert live.status_code == 200


@pytest.mark.asyncio
async def test_localhost_redis_url_is_actually_probed(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "redis://localhost:6379/0")
    client = AsyncMock()
    client.ping.return_value = True
    with patch("redis.asyncio.from_url", return_value=client):
        result = await health.check_redis()
    assert result["status"] == "healthy"
    client.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_dependency_error_envelope_and_retry_headers(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    app = FastAPI()
    app.add_exception_handler(APIException, api_exception_handler)
    service = TokenBlacklistService()

    @app.get("/protected")
    async def protected():
        await service.is_token_blacklisted("test-token")

    @app.get("/limited")
    async def limited():
        raise APIException(code=429, status_code=429, message="limited", headers={"Retry-After": "60"})

    with patch.object(TokenBlacklistService, "redis", new_callable=PropertyMock,
                      side_effect=RuntimeError("not initialized")):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/protected")
            limited_response = await client.get("/limited")
    assert response.status_code == response.json()["code"] == 503
    assert response.json()["data"] is None
    assert limited_response.status_code == 429
    assert limited_response.headers["Retry-After"] == "60"
