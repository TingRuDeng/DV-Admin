"""操作日志落库中间件测试（FastAPI 侧）。"""

from __future__ import annotations

import uuid

from app.middleware.request_logging.middleware import mask_sensitive_body


def test_mask_sensitive_body_masks_secret_fields():
    """敏感字段必须被掩码，非敏感字段保留。"""
    masked = mask_sensitive_body('{"username": "admin", "password": "secret", "nested": {"token": "abc"}}')
    assert '"username": "admin"' in masked
    assert "secret" not in masked
    assert "abc" not in masked
    assert "******" in masked


def test_mask_sensitive_body_returns_empty_for_non_json():
    """非 JSON 请求体不落库，避免泄露未结构化内容。"""
    assert mask_sensitive_body("not-json") == ""
    assert mask_sensitive_body("") == ""


def test_mutating_request_is_persisted_and_visible(auth_client, test_user):
    """写请求经中间件落库，并能通过 /logs/page 查询到。"""
    suffix = uuid.uuid4().hex[:6]
    create = auth_client.post(
        "/api/v1/system/dicts/",
        json={"name": f"审计字典{suffix}", "dictCode": f"audit_{suffix}", "remark": "审计测试", "status": 1},
    )
    assert create.status_code in (200, 201)

    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "POST"},
    ).json()["data"]
    paths = [row["path"] for row in page["list"]]
    assert any("/system/dicts" in path for path in paths)


def test_get_request_is_not_persisted(auth_client, test_user):
    """GET 读请求不落库，审计表只保留写操作。"""
    auth_client.get("/api/v1/system/dicts/")
    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "GET"},
    ).json()["data"]
    assert page["total"] == 0
