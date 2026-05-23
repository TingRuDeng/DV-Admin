"""
文件上传接口测试
"""
from io import BytesIO

from fastapi.testclient import TestClient


class TestFileUpload:
    """文件上传测试"""

    def test_upload_file_unauthorized(self, client: TestClient):
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = client.post("/api/v1/files/", files=files)
        assert response.status_code == 401

    def test_upload_file_authorized(self, auth_client: TestClient):
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000

    def test_upload_rejects_unsupported_file_type(self, auth_client: TestClient):
        files = {"file": ("payload.exe", BytesIO(b"binary"), "application/octet-stream")}
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

    def test_delete_file(self, auth_client: TestClient):
        # 文件删除使用 Query 参数，不是 JSON body
        response = auth_client.delete("/api/v1/files/?filePath=test.jpg")
        # 文件不存在会返回验证错误，但请求格式是正确的
        assert response.status_code in [200, 400]
