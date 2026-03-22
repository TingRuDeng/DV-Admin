# -*- coding: utf-8 -*-
"""
日志管理 API 测试
测试日志管理相关的 API 端点
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.db.models.system import OperationLog, Permissions


@pytest_asyncio.fixture
async def test_log_permissions(db):
    """创建日志相关权限"""
    # 创建日志菜单
    log_menu = await Permissions.create(
        name="日志管理",
        type="MENU",
        route_name="LogManagement",
        route_path="/system/logs",
        component="system/logs/index",
        sort=8,
        perm="system:logs:query",
    )
    
    log_delete = await Permissions.create(
        name="日志删除",
        type="BUTTON",
        parent=log_menu,
        perm="system:logs:delete",
    )
    
    return {
        "log_menu": log_menu,
        "log_delete": log_delete,
    }


@pytest_asyncio.fixture
async def test_logs_for_api(db):
    """创建测试日志数据"""
    logs = []
    for i in range(5):
        log = await OperationLog.create(
            user_id=1,
            username=f"api_user_{i}",
            name=f"API用户{i}",
            operation=f"API操作{i}",
            method="GET" if i % 2 == 0 else "POST",
            path=f"/api/v1/test/{i}",
            status=1 if i % 2 == 0 else 0,
            execution_time=100 + i * 10,
        )
        logs.append(log)
    return logs


class TestLogList:
    """测试日志列表接口"""

    def test_get_logs_unauthorized(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/system/logs/page")
        assert response.status_code == 401

    def test_get_logs_authorized(
        self, client: TestClient, auth_headers: dict, test_logs_for_api
    ):
        """测试授权访问日志列表"""
        response = client.get(
            "/api/v1/system/logs/page",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000
        assert "results" in data["data"]
        assert "count" in data["data"]

    def test_get_logs_with_filters(
        self, client: TestClient, auth_headers: dict, test_logs_for_api
    ):
        """测试带过滤条件的日志列表"""
        response = client.get(
            "/api/v1/system/logs/page",
            params={
                "username": "api_user_0",
                "method": "GET",
                "status": 1,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000


class TestVisitTrend:
    """测试访问趋势接口"""

    def test_get_visit_trend_unauthorized(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/system/logs/visit-trend")
        assert response.status_code == 401

    def test_get_visit_trend_authorized(
        self, client: TestClient, auth_headers: dict, test_logs_for_api
    ):
        """测试授权访问访问趋势"""
        response = client.get(
            "/api/v1/system/logs/visit-trend",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000
        assert isinstance(data["data"], list)


class TestVisitStats:
    """测试访问统计接口"""

    def test_get_visit_stats_unauthorized(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/system/logs/visit-stats")
        assert response.status_code == 401

    def test_get_visit_stats_authorized(
        self, client: TestClient, auth_headers: dict, test_logs_for_api
    ):
        """测试授权访问访问统计"""
        response = client.get(
            "/api/v1/system/logs/visit-stats",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000
        # API 返回 camelCase 格式
        assert "totalCount" in data["data"]
        assert "todayCount" in data["data"]
        assert "weekCount" in data["data"]
        assert "monthCount" in data["data"]


class TestLogDelete:
    """测试日志删除接口"""

    def test_delete_logs_unauthorized(self, client: TestClient):
        """测试未授权删除"""
        response = client.delete("/api/v1/system/logs/1,2,3")
        assert response.status_code == 401

    def test_delete_logs_authorized(
        self, client: TestClient, auth_headers: dict, test_logs_for_api
    ):
        """测试授权删除日志"""
        log_ids = ",".join([str(log.id) for log in test_logs_for_api[:2]])
        response = client.delete(
            f"/api/v1/system/logs/{log_ids}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000


class TestClearOldLogs:
    """测试清理历史日志接口"""

    def test_clear_old_logs_unauthorized(self, client: TestClient):
        """测试未授权清理"""
        response = client.delete("/api/v1/system/logs/clear/30")
        assert response.status_code == 401

    def test_clear_old_logs_authorized(
        self, client: TestClient, auth_headers: dict
    ):
        """测试授权清理历史日志"""
        response = client.delete(
            "/api/v1/system/logs/clear/30",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 20000
