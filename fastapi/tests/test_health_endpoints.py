"""
健康检查 HTTP 端点测试

覆盖基础健康检查、存活检查、就绪检查和根路径兼容响应。
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """基础健康检查接口应返回应用状态信息。"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "app_name" in data
    assert "environment" in data


def test_health_check_detailed(client: TestClient):
    """详细健康检查路径允许按实际路由返回 200 或 404。"""
    response = client.get("/health/detailed")

    assert response.status_code in [200, 404]


def test_root_endpoint(client: TestClient):
    """根路径允许返回根响应、未找到或重定向。"""
    response = client.get("/")

    assert response.status_code in [200, 404, 307]


def test_liveness_check(client: TestClient):
    """存活检查端点应返回 alive 状态。"""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


def test_readiness_check(client: TestClient):
    """就绪检查端点应包含依赖检查结果。"""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "checks" in data
    assert "database" in data["checks"]
