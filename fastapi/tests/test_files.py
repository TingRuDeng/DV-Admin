"""
文件上传接口测试
"""
from io import BytesIO

from fastapi.testclient import TestClient


def login_headers(client: TestClient, user: dict) -> dict[str, str]:
    """登录指定用户，返回可直接用于请求的认证头。"""
    response = client.post(
        "/api/v1/oauth/login/",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["data"]["accessToken"]
    return {"Authorization": f"Bearer {token}"}


class TestFileUpload:
    """文件上传测试"""

    def test_upload_file_unauthorized(self, client: TestClient):
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = client.post("/api/v1/files/", files=files)
        assert response.status_code == 401

    def test_upload_file_authorized(self, auth_client: TestClient, test_user_with_role):
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 200
        payload = response.json()
        data = payload["data"]
        assert payload.get("code") == 20000
        assert data["name"] == "test.txt"
        assert data["path"].startswith(f"files/{test_user_with_role['id']}/")
        assert data["url"].endswith(f"/media/{data['path']}")

    def test_upload_rejects_unsupported_file_type(self, auth_client: TestClient):
        files = {"file": ("payload.exe", BytesIO(b"binary"), "application/octet-stream")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 400
        assert response.json()["code"] != 20000

    def test_upload_rejects_svg_file(self, auth_client: TestClient):
        files = {"file": ("payload.svg", BytesIO(b"<svg></svg>"), "image/svg+xml")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 400
        assert response.json()["code"] != 20000

    def test_upload_rejects_file_over_size_limit(self, auth_client: TestClient, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "max_upload_size", 4)
        files = {"file": ("large.txt", BytesIO(b"large content"), "text/plain")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 400
        assert response.json()["code"] != 20000


class TestFileDelete:
    """文件删除测试"""

    def test_delete_file_unauthorized(self, client: TestClient):
        response = client.delete("/api/v1/files/?filePath=test.jpg")
        assert response.status_code == 401

    def test_delete_uploaded_file_by_path(self, auth_client: TestClient, tmp_path, monkeypatch):
        """删除接口只接收上传返回的相对路径。"""
        from app.core.config import settings

        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        files = {"file": ("delete-me.txt", BytesIO(b"delete me"), "text/plain")}
        upload_response = auth_client.post("/api/v1/files/", files=files)
        assert upload_response.status_code == 200
        file_path = upload_response.json()["data"]["path"]
        uploaded_file = tmp_path / file_path
        assert uploaded_file.exists()

        response = auth_client.delete("/api/v1/files/", params={"filePath": file_path})

        assert response.status_code == 200
        assert response.json()["code"] == 20000
        assert not uploaded_file.exists()

    def test_delete_rejects_full_media_url(self, auth_client: TestClient, tmp_path, monkeypatch):
        """删除接口拒绝完整媒体 URL，避免把 URL 当本地路径解析。"""
        from app.core.config import settings

        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        files = {"file": ("url-delete.txt", BytesIO(b"delete by url"), "text/plain")}
        upload_response = auth_client.post("/api/v1/files/", files=files)
        assert upload_response.status_code == 200
        file_url = upload_response.json()["data"]["url"]

        response = auth_client.delete("/api/v1/files/", params={"filePath": file_url})

        assert response.status_code == 400
        assert response.json()["message"] == "非法的文件路径"

    def test_delete_rejects_other_user_file(
        self,
        auth_client: TestClient,
        client: TestClient,
        test_user: dict,
        tmp_path,
        monkeypatch,
    ):
        """普通用户不能删除其他用户目录下的上传文件。"""
        from app.core.config import settings

        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        files = {"file": ("other-user.txt", BytesIO(b"owned by admin"), "text/plain")}
        upload_response = auth_client.post("/api/v1/files/", files=files)
        assert upload_response.status_code == 200
        file_path = upload_response.json()["data"]["path"]
        uploaded_file = tmp_path / file_path
        assert uploaded_file.exists()

        response = client.delete(
            "/api/v1/files/",
            params={"filePath": file_path},
            headers=login_headers(client, test_user),
        )

        assert response.status_code == 403
        assert response.json()["message"] == "无权删除该文件"
        assert uploaded_file.exists()
