"""
个人中心接口测试
"""
from io import BytesIO

from fastapi.testclient import TestClient


class TestProfile:
    """个人信息测试"""

    def test_get_profile_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/information/profile/")
        assert response.status_code == 401

    def test_get_profile_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/information/profile/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestProfileUpdate:
    """个人信息更新测试"""

    def test_update_profile(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/information/profile/", json={
            "name": "测试用户"
        })
        assert response.status_code == 200


class TestPassword:
    """密码修改测试"""

    def test_change_password(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/information/password", json={
            "old_password": "admin123",
            "new_password": "admin123",
            "confirm_password": "admin123"
        })
        assert response.status_code == 200


class TestAvatar:
    """头像修改测试"""

    def test_change_avatar(self, auth_client: TestClient):
        files = {"file": ("test.png", BytesIO(b"fake image"), "image/png")}
        response = auth_client.post("/api/v1/information/change-avatar/", files=files)
        assert response.status_code == 200
