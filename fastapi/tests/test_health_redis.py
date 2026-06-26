"""
健康检查 Redis 依赖测试

覆盖 Redis 未配置、连接成功、库不可用和连接失败场景。
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_check_redis_not_configured():
    """默认 Redis URL 且无密码时应视为未配置。"""
    from app.api.health import check_redis

    with patch("app.api.health.settings") as mock_settings:
        mock_settings.redis_url = "redis://localhost:6379/0"
        mock_settings.redis_password = None

        result = await check_redis()

        assert result["status"] == "not_configured"


@pytest.mark.asyncio
async def test_check_redis_empty_url():
    """空 Redis URL 应视为未配置。"""
    from app.api.health import check_redis

    with patch("app.api.health.settings") as mock_settings:
        mock_settings.redis_url = ""
        mock_settings.redis_password = None

        result = await check_redis()

        assert result["status"] == "not_configured"


@pytest.mark.asyncio
async def test_check_redis_success():
    """Redis ping 成功时应返回 healthy 并关闭客户端。"""
    from app.api.health import check_redis

    with patch("app.api.health.settings") as mock_settings:
        mock_settings.redis_url = "redis://custom-host:6379/1"
        mock_settings.redis_password = "test_password"

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_client.close = AsyncMock()

        with patch("redis.asyncio.from_url") as mock_from_url:
            mock_from_url.return_value = mock_client

            result = await check_redis()

            assert result["status"] == "healthy"
            assert result["message"] == "Redis 连接正常"
            mock_client.ping.assert_called_once()
            mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_redis_import_error():
    """Redis 客户端库不可用时应返回 unavailable。"""
    from app.api.health import check_redis

    with patch("app.api.health.settings") as mock_settings:
        mock_settings.redis_url = "redis://custom-host:6379/1"
        mock_settings.redis_password = None

        with patch("redis.asyncio.from_url", side_effect=ImportError("No module")):
            result = await check_redis()

            assert result["status"] == "unavailable"
            assert "未安装" in result["message"]


@pytest.mark.asyncio
async def test_check_redis_connection_error():
    """Redis 连接失败时应返回 unhealthy 并带错误信息。"""
    from app.api.health import check_redis

    with patch("app.api.health.settings") as mock_settings:
        mock_settings.redis_url = "redis://custom-host:6379/1"
        mock_settings.redis_password = None

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))

        with patch("redis.asyncio.from_url") as mock_from_url:
            mock_from_url.return_value = mock_client

            result = await check_redis()

            assert result["status"] == "unhealthy"
            assert "Connection refused" in result["message"]
