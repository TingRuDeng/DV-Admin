# -*- coding: utf-8 -*-
"""
健康检查 API 测试
测试 health 模块的功能
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock


class TestHealthAPI:
    """测试健康检查 API"""

    def test_health_check(self, client: TestClient):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "app_name" in data
        assert "environment" in data

    def test_health_check_detailed(self, client: TestClient):
        """测试详细健康检查接口"""
        response = client.get("/health/detailed")
        # 可能返回 200 或其他状态
        assert response.status_code in [200, 404]

    def test_root_endpoint(self, client: TestClient):
        """测试根路径"""
        response = client.get("/")
        # 可能返回 200 或 404
        assert response.status_code in [200, 404, 307]


class TestHealthEndpoints:
    """测试健康检查端点"""

    def test_liveness_check(self, client: TestClient):
        """测试存活检查端点"""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_readiness_check(self, client: TestClient):
        """测试就绪检查端点"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "database" in data["checks"]


class TestCheckDatabase:
    """测试数据库检查函数"""

    @pytest.mark.asyncio
    async def test_check_database_sqlite_success(self):
        """测试 SQLite 数据库检查成功"""
        from app.api.health import check_database

        with patch('app.api.health.Tortoise') as mock_tortoise, \
             patch('app.api.health.settings') as mock_settings:
            mock_settings.is_sqlite = True

            mock_conn = AsyncMock()
            mock_conn.execute_query = AsyncMock(return_value=[[1]])
            mock_tortoise.get_connection.return_value = mock_conn

            result = await check_database()

            assert result["status"] == "healthy"
            assert result["type"] == "sqlite"
            assert "message" in result

    @pytest.mark.asyncio
    async def test_check_database_mysql_success(self):
        """测试 MySQL 数据库检查成功"""
        from app.api.health import check_database

        with patch('app.api.health.Tortoise') as mock_tortoise, \
             patch('app.api.health.settings') as mock_settings:
            mock_settings.is_sqlite = False

            mock_conn = AsyncMock()
            mock_conn.execute_query = AsyncMock(return_value=[[1]])
            mock_tortoise.get_connection.return_value = mock_conn

            result = await check_database()

            assert result["status"] == "healthy"
            assert result["type"] == "mysql"

    @pytest.mark.asyncio
    async def test_check_database_error(self):
        """测试数据库检查失败"""
        from app.api.health import check_database

        with patch('app.api.health.Tortoise') as mock_tortoise, \
             patch('app.api.health.settings') as mock_settings:
            mock_settings.is_sqlite = True

            mock_conn = AsyncMock()
            mock_conn.execute_query = AsyncMock(side_effect=Exception("Connection failed"))
            mock_tortoise.get_connection.return_value = mock_conn

            result = await check_database()

            assert result["status"] == "unhealthy"
            assert "Connection failed" in result["message"]


class TestCheckRedis:
    """测试 Redis 检查函数"""

    @pytest.mark.asyncio
    async def test_check_redis_not_configured(self):
        """测试 Redis 未配置"""
        from app.api.health import check_redis

        with patch('app.api.health.settings') as mock_settings:
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_password = None

            result = await check_redis()

            assert result["status"] == "not_configured"

    @pytest.mark.asyncio
    async def test_check_redis_empty_url(self):
        """测试 Redis URL 为空"""
        from app.api.health import check_redis

        with patch('app.api.health.settings') as mock_settings:
            mock_settings.redis_url = ""
            mock_settings.redis_password = None

            result = await check_redis()

            assert result["status"] == "not_configured"

    @pytest.mark.asyncio
    async def test_check_redis_success(self):
        """测试 Redis 连接成功"""
        from app.api.health import check_redis

        with patch('app.api.health.settings') as mock_settings:
            mock_settings.redis_url = "redis://custom-host:6379/1"
            mock_settings.redis_password = "test_password"

            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_client.close = AsyncMock()

            with patch('redis.asyncio.from_url') as mock_from_url:
                mock_from_url.return_value = mock_client

                result = await check_redis()

                assert result["status"] == "healthy"
                assert result["message"] == "Redis 连接正常"
                mock_client.ping.assert_called_once()
                mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_redis_import_error(self):
        """测试 Redis 库未安装"""
        from app.api.health import check_redis

        with patch('app.api.health.settings') as mock_settings:
            mock_settings.redis_url = "redis://custom-host:6379/1"
            mock_settings.redis_password = None

            with patch('redis.asyncio.from_url', side_effect=ImportError("No module")):
                result = await check_redis()

                assert result["status"] == "unavailable"
                assert "未安装" in result["message"]

    @pytest.mark.asyncio
    async def test_check_redis_connection_error(self):
        """测试 Redis 连接失败"""
        from app.api.health import check_redis

        with patch('app.api.health.settings') as mock_settings:
            mock_settings.redis_url = "redis://custom-host:6379/1"
            mock_settings.redis_password = None

            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))

            with patch('redis.asyncio.from_url') as mock_from_url:
                mock_from_url.return_value = mock_client

                result = await check_redis()

                assert result["status"] == "unhealthy"
                assert "Connection refused" in result["message"]


class TestReadinessCheck:
    """测试就绪检查"""

    @pytest.mark.asyncio
    async def test_readiness_check_all_healthy(self):
        """测试就绪检查（所有服务健康）"""
        from app.api.health import readiness_check

        with patch('app.api.health.check_database') as mock_db, \
             patch('app.api.health.check_redis') as mock_redis:
            mock_db.return_value = {
                "status": "healthy",
                "type": "sqlite",
                "message": "数据库连接正常"
            }
            mock_redis.return_value = {
                "status": "healthy",
                "message": "Redis 连接正常"
            }

            result = await readiness_check()

            assert result.status == "ready"
            assert "database" in result.checks
            assert "redis" in result.checks

    @pytest.mark.asyncio
    async def test_readiness_check_database_unhealthy(self):
        """测试就绪检查（数据库不健康）"""
        from app.api.health import readiness_check

        with patch('app.api.health.check_database') as mock_db, \
             patch('app.api.health.check_redis') as mock_redis:
            mock_db.return_value = {
                "status": "unhealthy",
                "type": "sqlite",
                "message": "数据库连接失败"
            }
            mock_redis.return_value = {
                "status": "healthy",
                "message": "Redis 连接正常"
            }

            result = await readiness_check()

            assert result.status == "not_ready"

    @pytest.mark.asyncio
    async def test_readiness_check_redis_unhealthy(self):
        """测试就绪检查（Redis 不健康）"""
        from app.api.health import readiness_check

        with patch('app.api.health.check_database') as mock_db, \
             patch('app.api.health.check_redis') as mock_redis:
            mock_db.return_value = {
                "status": "healthy",
                "type": "sqlite",
                "message": "数据库连接正常"
            }
            mock_redis.return_value = {
                "status": "unhealthy",
                "message": "Redis 连接失败"
            }

            result = await readiness_check()

            assert result.status == "not_ready"

    @pytest.mark.asyncio
    async def test_readiness_check_redis_none(self):
        """测试就绪检查（Redis 返回 None）"""
        from app.api.health import readiness_check

        with patch('app.api.health.check_database') as mock_db, \
             patch('app.api.health.check_redis') as mock_redis:
            mock_db.return_value = {
                "status": "healthy",
                "type": "sqlite",
                "message": "数据库连接正常"
            }
            mock_redis.return_value = None

            result = await readiness_check()

            assert result.status == "ready"
            assert "redis" not in result.checks

    @pytest.mark.asyncio
    async def test_readiness_check_redis_not_configured(self):
        """测试就绪检查（Redis 未配置）"""
        from app.api.health import readiness_check

        with patch('app.api.health.check_database') as mock_db, \
             patch('app.api.health.check_redis') as mock_redis:
            mock_db.return_value = {
                "status": "healthy",
                "type": "sqlite",
                "message": "数据库连接正常"
            }
            mock_redis.return_value = {
                "status": "not_configured",
                "message": "Redis 未配置"
            }

            result = await readiness_check()

            # Redis 未配置不影响整体状态
            assert result.status == "ready"
