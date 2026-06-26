"""
健康检查 readiness 聚合测试

覆盖数据库和 Redis 依赖状态对整体就绪状态的影响。
"""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_readiness_check_all_healthy():
    """所有依赖健康时整体状态应为 ready。"""
    from app.api.health import readiness_check

    with patch("app.api.health.check_database") as mock_db, patch(
        "app.api.health.check_redis"
    ) as mock_redis:
        mock_db.return_value = {
            "status": "healthy",
            "type": "sqlite",
            "message": "数据库连接正常",
        }
        mock_redis.return_value = {
            "status": "healthy",
            "message": "Redis 连接正常",
        }

        result = await readiness_check()

        assert result.status == "ready"
        assert "database" in result.checks
        assert "redis" in result.checks


@pytest.mark.asyncio
async def test_readiness_check_database_unhealthy():
    """数据库不健康时整体状态应为 not_ready。"""
    from app.api.health import readiness_check

    with patch("app.api.health.check_database") as mock_db, patch(
        "app.api.health.check_redis"
    ) as mock_redis:
        mock_db.return_value = {
            "status": "unhealthy",
            "type": "sqlite",
            "message": "数据库连接失败",
        }
        mock_redis.return_value = {
            "status": "healthy",
            "message": "Redis 连接正常",
        }

        result = await readiness_check()

        assert result.status == "not_ready"


@pytest.mark.asyncio
async def test_readiness_check_redis_unhealthy():
    """Redis 明确 unhealthy 时整体状态应为 not_ready。"""
    from app.api.health import readiness_check

    with patch("app.api.health.check_database") as mock_db, patch(
        "app.api.health.check_redis"
    ) as mock_redis:
        mock_db.return_value = {
            "status": "healthy",
            "type": "sqlite",
            "message": "数据库连接正常",
        }
        mock_redis.return_value = {
            "status": "unhealthy",
            "message": "Redis 连接失败",
        }

        result = await readiness_check()

        assert result.status == "not_ready"


@pytest.mark.asyncio
async def test_readiness_check_redis_none():
    """Redis 检查返回 None 时不应写入 checks。"""
    from app.api.health import readiness_check

    with patch("app.api.health.check_database") as mock_db, patch(
        "app.api.health.check_redis"
    ) as mock_redis:
        mock_db.return_value = {
            "status": "healthy",
            "type": "sqlite",
            "message": "数据库连接正常",
        }
        mock_redis.return_value = None

        result = await readiness_check()

        assert result.status == "ready"
        assert "redis" not in result.checks


@pytest.mark.asyncio
async def test_readiness_check_redis_not_configured():
    """Redis 未配置不应影响整体 ready 状态。"""
    from app.api.health import readiness_check

    with patch("app.api.health.check_database") as mock_db, patch(
        "app.api.health.check_redis"
    ) as mock_redis:
        mock_db.return_value = {
            "status": "healthy",
            "type": "sqlite",
            "message": "数据库连接正常",
        }
        mock_redis.return_value = {
            "status": "not_configured",
            "message": "Redis 未配置",
        }

        result = await readiness_check()

        assert result.status == "ready"
