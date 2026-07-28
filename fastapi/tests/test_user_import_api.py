"""用户导入接口资源边界测试。"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.schemas.system import UserImportResult


def test_user_import_rejects_oversize_file(
    auth_client: TestClient,
    monkeypatch,
):
    """导入工作簿在解析前执行分块大小校验。"""
    from app.core.config import settings

    monkeypatch.setattr(settings, "max_upload_size", 4)
    files = {
        "file": (
            "users.xlsx",
            BytesIO(b"oversize workbook"),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    response = auth_client.post("/api/v1/system/users/import", files=files)

    assert response.status_code == 400
    assert "文件大小不能超过" in response.json()["message"]


@pytest.mark.parametrize(
    ("query_name", "filename"),
    [
        ("deptId", "USERS.XLSX"),
        ("dept_id", "users.xlsx"),
    ],
)
def test_user_import_forwards_department_query_contract(
    auth_client: TestClient,
    monkeypatch,
    query_name,
    filename,
):
    """公开 deptId 与过渡期 dept_id 都必须传入导入服务。"""
    from app.api.v1.system.user_routes.import_export import user_service

    captured = {}

    async def fake_import_users(file, dept_id, current_user=None):
        captured["content"] = file.read()
        captured["dept_id"] = dept_id
        captured["user_id"] = current_user.id
        return UserImportResult()

    monkeypatch.setattr(user_service, "import_users", fake_import_users)
    files = {
        "file": (
            filename,
            BytesIO(b"fake workbook"),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    response = auth_client.post(
        "/api/v1/system/users/import",
        params={query_name: 42},
        files=files,
    )

    assert response.status_code == 200
    assert captured["content"] == b"fake workbook"
    assert captured["dept_id"] == 42
    assert captured["user_id"] is not None
