"""个人中心写入口的审计对象关联集成测试。"""

from __future__ import annotations

import json
from io import BytesIO

from fastapi.testclient import TestClient


def _find_log(auth_client: TestClient, request_id: str) -> dict:
    """按请求 ID读取唯一审计日志。"""
    response = auth_client.get(
        "/api/v1/system/logs/page",
        params={"requestId": request_id},
    )
    assert response.status_code == 200
    rows = response.json()["data"]["list"]
    assert len(rows) == 1
    return rows[0]


def test_profile_update_audit_links_current_user(
    auth_client: TestClient,
    test_user_with_role: dict,
):
    request_id = "fastapi-profile-audit"

    response = auth_client.put(
        "/api/v1/information/profile/",
        json={"name": "审计资料用户", "gender": 1},
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    log = _find_log(auth_client, request_id)
    assert log["objectType"] == "system.users"
    assert log["objectId"] == str(test_user_with_role["id"])
    assert log["requestContext"]["changedFields"] == ["name", "gender"]
    assert log["requestContext"]["objectId"] == str(test_user_with_role["id"])


def test_password_change_audit_masks_password_values(
    auth_client: TestClient,
    test_user_with_role: dict,
):
    request_id = "fastapi-password-audit"
    payload = {
        "oldPassword": test_user_with_role["password"],
        "newPassword": "Newpass123",
        "confirmPassword": "Newpass123",
    }

    response = auth_client.put(
        "/api/v1/information/password",
        json=payload,
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    log = _find_log(auth_client, request_id)
    context = log["requestContext"]
    assert log["objectType"] == "system.users"
    assert log["objectId"] == str(test_user_with_role["id"])
    assert context["changedFields"] == ["oldPassword", "newPassword", "confirmPassword"]
    assert context["body"]["oldPassword"] == "******"
    assert context["body"]["newPassword"] == "******"
    assert test_user_with_role["password"] not in json.dumps(context)
    assert "Newpass123" not in json.dumps(context)


def test_avatar_upload_audit_records_file_metadata(
    auth_client: TestClient,
    test_user_with_role: dict,
    tmp_path,
    monkeypatch,
):
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    request_id = "fastapi-avatar-audit"
    response = auth_client.post(
        "/api/v1/information/change-avatar/",
        files={"file": ("audit-avatar.gif", BytesIO(b"avatar-bytes"), "image/gif")},
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    log = _find_log(auth_client, request_id)
    context = log["requestContext"]
    assert log["objectType"] == "system.users"
    assert log["objectId"] == str(test_user_with_role["id"])
    assert context["changedFields"] == ["file"]
    assert context["fileMeta"][0]["fieldName"] == "file"
    assert context["fileMeta"][0]["fileName"] == "audit-avatar.gif"
    assert context["fileMeta"][0]["size"] == len(b"avatar-bytes")
    assert "avatar-bytes" not in json.dumps(context)
