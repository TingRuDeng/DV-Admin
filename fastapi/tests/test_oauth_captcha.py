"""
OAuth 验证码与验证码登录测试。
"""
import asyncio

from fastapi.testclient import TestClient

from app.services.captcha_service import get_captcha_service


async def _get_captcha_code(captcha_key: str):
    """从测试环境验证码缓存中读取验证码文本。"""
    service = get_captcha_service()
    return await service._cache.get(captcha_key)


class TestOAuthCaptcha:
    """验证码接口测试。"""

    def test_captcha_returns_key_and_base64(self, client: TestClient):
        """测试验证码返回正确格式。"""
        response = client.get("/api/v1/oauth/captcha/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        result = data.get("data", {})
        assert "captchaKey" in result
        assert "captchaBase64" in result

    def test_captcha_returns_unique_keys(self, client: TestClient):
        """测试验证码每次返回不同的 key。"""
        response1 = client.get("/api/v1/oauth/captcha/")
        response2 = client.get("/api/v1/oauth/captcha/")
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]
        assert data1["captchaKey"] != data2["captchaKey"]

    def test_captcha_base64_format(self, client: TestClient):
        """测试验证码 base64 格式正确。"""
        response = client.get("/api/v1/oauth/captcha/")
        data = response.json()["data"]
        captcha_base64 = data["captchaBase64"]
        assert captcha_base64.startswith("data:image/png;base64,")
        base64_content = captcha_base64.replace("data:image/png;base64,", "")
        assert len(base64_content) > 0


class TestOAuthLoginWithCaptcha:
    """带验证码的登录接口测试。"""

    def test_login_with_valid_captcha(self, client: TestClient, test_user_with_role):
        """测试带正确验证码的登录。"""
        captcha_response = client.get("/api/v1/oauth/captcha/")
        assert captcha_response.status_code == 200
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]
        captcha_code = asyncio.run(_get_captcha_code(captcha_key))

        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
                "captcha_key": captcha_key,
                "captcha_code": captcha_code,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert "accessToken" in data.get("data", {})

    def test_login_with_invalid_captcha(self, client: TestClient, test_user_with_role):
        """测试带错误验证码的登录。"""
        captcha_response = client.get("/api/v1/oauth/captcha/")
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]

        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
                "captcha_key": captcha_key,
                "captcha_code": "0000",
            },
        )
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_with_expired_captcha(self, client: TestClient, test_user_with_role):
        """测试使用过期验证码登录。"""
        response = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
                "captcha_key": "nonexistent-key-12345",
                "captcha_code": "1234",
            },
        )
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_without_captcha(self, client: TestClient, test_user_with_role):
        """测试不使用验证码的登录。"""
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

    def test_login_captcha_one_time_use(self, client: TestClient, test_user_with_role):
        """测试验证码一次性使用。"""
        captcha_response = client.get("/api/v1/oauth/captcha/")
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]
        captcha_code = asyncio.run(_get_captcha_code(captcha_key))

        response1 = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
                "captcha_key": captcha_key,
                "captcha_code": captcha_code,
            },
        )
        assert response1.status_code == 200
        assert response1.json().get("code") == 20000

        response2 = client.post(
            "/api/v1/oauth/login/",
            json={
                "username": test_user_with_role["username"],
                "password": test_user_with_role["password"],
                "captcha_key": captcha_key,
                "captcha_code": captcha_code,
            },
        )
        assert response2.status_code in [200, 401]
        if response2.status_code == 200:
            data = response2.json()
            assert data.get("code") != 20000
