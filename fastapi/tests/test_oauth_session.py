"""
OAuth 用户信息、菜单和登出接口测试。
"""
from fastapi.testclient import TestClient


class TestOAuthInfo:
    """用户信息接口测试。"""

    def test_get_info_unauthorized(self, client: TestClient):
        """测试未授权访问。"""
        response = client.get("/api/v1/oauth/info/")
        assert response.status_code == 401

    def test_get_info_authorized(self, auth_client: TestClient):
        """测试获取用户信息。"""
        response = auth_client.get("/api/v1/oauth/info/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        result = data.get("data", {})
        assert "username" in result or "id" in result


class TestOAuthMenus:
    """菜单路由接口测试。"""

    def test_get_menus_unauthorized(self, client: TestClient):
        """测试未授权访问。"""
        response = client.get("/api/v1/oauth/menus/routes/")
        assert response.status_code == 401

    def test_get_menus_authorized(self, auth_client: TestClient):
        """测试获取用户菜单。"""
        response = auth_client.get("/api/v1/oauth/menus/routes/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), list)


class TestOAuthLogout:
    """登出接口测试。"""

    def test_logout_authorized(self, auth_client: TestClient):
        """测试登出。"""
        response = auth_client.post("/api/v1/oauth/logout/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
