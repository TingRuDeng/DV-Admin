"""
OAuth 登录接口测试。
"""
from fastapi.testclient import TestClient
from scripts.api_error_codes import ACCESS_TOKEN_INVALID_CODE, ERROR_CODE


class TestOAuthLogin:
    """登录接口测试。"""

    def test_login_success(self, client: TestClient, test_user_with_role):
        """测试登录成功 - 使用 test_user fixture 创建的用户。"""
        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert "accessToken" in data.get("data", {})

    def test_login_invalid_credentials(self, client: TestClient, test_user_with_role):
        """测试登录失败 - 错误密码。"""
        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": "wrongpassword",
            },
        )
        # 错误密码返回 200 但 code 不为成功码，或返回 401。
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_invalid_credentials_uses_general_error_code(
        self,
        client: TestClient,
        test_user_with_role,
    ):
        """登录失败不能复用 Access Token 失效错误码，避免前端误触发刷新流程。"""
        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data.get("code") == ERROR_CODE
        assert data.get("code") != ACCESS_TOKEN_INVALID_CODE

    def test_login_missing_fields(self, client: TestClient):
        """测试登录失败 - 缺少字段。"""
        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": "admin",
            },
        )
        assert response.status_code == 422
