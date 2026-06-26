"""
健康检查数据库依赖测试

覆盖 SQLite、MySQL 和异常状态的数据库探针。
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_check_database_sqlite_success():
    """SQLite 数据库检查成功时应返回 healthy。"""
    from app.api.health import check_database

    with patch("app.api.health.Tortoise") as mock_tortoise, patch(
        "app.api.health.settings"
    ) as mock_settings:
        mock_settings.is_sqlite = True

        mock_conn = AsyncMock()
        mock_conn.execute_query = AsyncMock(return_value=[[1]])
        mock_tortoise.get_connection.return_value = mock_conn

        result = await check_database()

        assert result["status"] == "healthy"
        assert result["type"] == "sqlite"
        assert "message" in result


@pytest.mark.asyncio
async def test_check_database_mysql_success():
    """MySQL 数据库检查成功时应返回 healthy。"""
    from app.api.health import check_database

    with patch("app.api.health.Tortoise") as mock_tortoise, patch(
        "app.api.health.settings"
    ) as mock_settings:
        mock_settings.is_sqlite = False

        mock_conn = AsyncMock()
        mock_conn.execute_query = AsyncMock(return_value=[[1]])
        mock_tortoise.get_connection.return_value = mock_conn

        result = await check_database()

        assert result["status"] == "healthy"
        assert result["type"] == "mysql"


@pytest.mark.asyncio
async def test_check_database_error():
    """数据库检查异常时应返回 unhealthy 并带错误信息。"""
    from app.api.health import check_database

    with patch("app.api.health.Tortoise") as mock_tortoise, patch(
        "app.api.health.settings"
    ) as mock_settings:
        mock_settings.is_sqlite = True

        mock_conn = AsyncMock()
        mock_conn.execute_query = AsyncMock(side_effect=Exception("Connection failed"))
        mock_tortoise.get_connection.return_value = mock_conn

        result = await check_database()

        assert result["status"] == "unhealthy"
        assert "Connection failed" in result["message"]
