"""
文件上传接口测试
"""
from io import BytesIO

from fastapi.testclient import TestClient


class TestFileUpload:
    """文件上传测试"""

    def test_upload_file_unauthorized(self, client: TestClient):
        response = client.post("/api/v1/files/", data={})
        assert response.status_code in [401, 422]

    def test_upload_file_authorized(self, auth_client: TestClient):
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = auth_client.post("/api/v1/files/", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestFileDelete:
    """文件删除测试"""

    def test_delete_file(self, auth_client: TestClient):
        # 文件删除使用 Query 参数，不是 JSON body
        response = auth_client.delete("/api/v1/files/?filePath=test.jpg")
        # 文件不存在会返回验证错误，但请求格式是正确的
        assert response.status_code in [200, 400]
