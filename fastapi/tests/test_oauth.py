"""
OAuth 认证接口测试
"""
from fastapi.testclient import TestClient


class TestOAuthLogin:
    """登录接口测试"""

    def test_login_success(self, client: TestClient, test_user_with_role):
        """测试登录成功 - 使用 test_user fixture 创建的用户"""
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert "accessToken" in data.get("data", {})

    def test_login_invalid_credentials(self, client: TestClient, test_user_with_role):
        """测试登录失败 - 错误密码"""
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": "wrongpassword"
        })
        # 错误密码返回 200 但 code 不为 0，或返回 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_missing_fields(self, client: TestClient):
        """测试登录失败 - 缺少字段"""
        response = client.post("/api/v1/oauth/login/", json={
            "username": "admin"
        })
        assert response.status_code == 422


class TestOAuthCaptcha:
    """验证码接口测试"""

    def test_captcha_returns_key_and_base64(self, client: TestClient):
        """测试验证码返回正确格式"""
        response = client.get("/api/v1/oauth/captcha/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        result = data.get("data", {})
        assert "captchaKey" in result
        assert "captchaBase64" in result

    def test_captcha_returns_unique_keys(self, client: TestClient):
        """测试验证码每次返回不同的key"""
        response1 = client.get("/api/v1/oauth/captcha/")
        response2 = client.get("/api/v1/oauth/captcha/")
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]
        assert data1["captchaKey"] != data2["captchaKey"]

    def test_captcha_base64_format(self, client: TestClient):
        """测试验证码 base64 格式正确"""
        response = client.get("/api/v1/oauth/captcha/")
        data = response.json()["data"]
        captcha_base64 = data["captchaBase64"]
        assert captcha_base64.startswith("data:image/png;base64,")
        # 验证 base64 内容不为空
        base64_content = captcha_base64.replace("data:image/png;base64,", "")
        assert len(base64_content) > 0


class TestOAuthLoginWithCaptcha:
    """带验证码的登录接口测试"""

    def test_login_with_valid_captcha(self, client: TestClient, test_user_with_role):
        """测试带正确验证码的登录"""
        # 1. 获取验证码
        captcha_response = client.get("/api/v1/oauth/captcha/")
        assert captcha_response.status_code == 200
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]

        # 2. 从服务中获取验证码（测试环境）
        import asyncio

        from app.services.captcha_service import get_captcha_service

        async def get_code():
            service = get_captcha_service()
            return await service._cache.get(captcha_key)

        captcha_code = asyncio.run(get_code())

        # 3. 使用验证码登录
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
            "captcha_key": captcha_key,
            "captcha_code": captcha_code,
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert "accessToken" in data.get("data", {})

    def test_login_with_invalid_captcha(self, client: TestClient, test_user_with_role):
        """测试带错误验证码的登录"""
        # 1. 获取验证码
        captcha_response = client.get("/api/v1/oauth/captcha/")
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]

        # 2. 使用错误的验证码登录
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
            "captcha_key": captcha_key,
            "captcha_code": "0000",  # 错误的验证码
        })
        # 应该返回错误
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_with_expired_captcha(self, client: TestClient, test_user_with_role):
        """测试使用过期验证码登录"""
        # 使用不存在的 key
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
            "captcha_key": "nonexistent-key-12345",
            "captcha_code": "1234",
        })
        # 应该返回错误
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 20000

    def test_login_without_captcha(self, client: TestClient, test_user_with_role):
        """测试不使用验证码的登录（验证码是可选的）"""
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
        })
        # 不提供验证码也应该能登录成功
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000

    def test_login_captcha_one_time_use(self, client: TestClient, test_user_with_role):
        """测试验证码一次性使用"""
        # 1. 获取验证码
        captcha_response = client.get("/api/v1/oauth/captcha/")
        captcha_data = captcha_response.json()["data"]
        captcha_key = captcha_data["captchaKey"]

        # 2. 从服务中获取验证码
        import asyncio

        from app.services.captcha_service import get_captcha_service

        async def get_code():
            service = get_captcha_service()
            return await service._cache.get(captcha_key)

        captcha_code = asyncio.run(get_code())

        # 3. 第一次登录成功
        response1 = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
            "captcha_key": captcha_key,
            "captcha_code": captcha_code,
        })
        assert response1.status_code == 200
        assert response1.json().get("code") == 20000

        # 4. 第二次使用相同验证码应该失败
        response2 = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
            "captcha_key": captcha_key,
            "captcha_code": captcha_code,
        })
        # 验证码已被删除，应该失败
        assert response2.status_code in [200, 401]
        if response2.status_code == 200:
            data = response2.json()
            assert data.get("code") != 20000


class TestOAuthInfo:
    """用户信息接口测试"""

    def test_get_info_unauthorized(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/oauth/info/")
        assert response.status_code == 401

    def test_get_info_authorized(self, auth_client: TestClient):
        """测试获取用户信息"""
        response = auth_client.get("/api/v1/oauth/info/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        result = data.get("data", {})
        assert "username" in result or "id" in result


class TestOAuthMenus:
    """菜单路由接口测试"""

    def test_get_menus_unauthorized(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/oauth/menus/routes/")
        assert response.status_code == 401

    def test_get_menus_authorized(self, auth_client: TestClient):
        """测试获取用户菜单"""
        response = auth_client.get("/api/v1/oauth/menus/routes/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), list)


class TestOAuthLogout:
    """登出接口测试"""

    def test_logout_authorized(self, auth_client: TestClient):
        """测试登出"""
        response = auth_client.post("/api/v1/oauth/logout/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
