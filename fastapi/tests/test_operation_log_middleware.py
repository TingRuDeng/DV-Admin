"""操作日志落库中间件测试（FastAPI 侧）。"""

from __future__ import annotations

import uuid

from app.middleware.request_logging.middleware import (
    MAX_REQUEST_ID_LENGTH,
    mask_sensitive_body,
    normalize_request_id,
    summarize_error_response,
)


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


def test_error_summary_uses_masked_response():
    """错误摘要不得绕过响应体敏感字段掩码。"""
    summary = summarize_error_response(
        '{"errors": {"password": "must-not-leak"}}',
        400,
    )

    assert "must-not-leak" not in summary
    assert "******" in summary


def test_request_id_normalization_rejects_log_and_header_injection():
    assert normalize_request_id("trace-123") == "trace-123"
    assert normalize_request_id("x" * (MAX_REQUEST_ID_LENGTH + 16)) == (
        "x" * MAX_REQUEST_ID_LENGTH
    )
    assert normalize_request_id("trace\nforged") == ""
    assert normalize_request_id("trace id") == ""


def test_mutating_request_persists_request_id(auth_client, test_user):
    """写请求经中间件落库，并持久化响应头对应的 request id。"""
    suffix = uuid.uuid4().hex[:6]
    request_id = f"fastapi-audit-{suffix}"
    create = auth_client.post(
        "/api/v1/system/dicts/",
        json={"name": f"审计字典{suffix}", "dictCode": f"audit_{suffix}", "remark": "审计测试", "status": 1},
        headers={"X-Request-ID": request_id},
    )
    assert create.status_code in (200, 201)
    assert create.headers["X-Request-ID"] == request_id

    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "POST"},
    ).json()["data"]
    row = next(row for row in page["list"] if "/system/dicts" in row["path"])
    assert row["requestId"] == request_id
    assert row["errorMsg"] == ""
    assert row["responseBody"] == ""


def test_long_request_id_is_trimmed_consistently(auth_client, test_user):
    """响应头和持久化字段必须使用同一个有界 request id。"""
    request_id = "x" * (MAX_REQUEST_ID_LENGTH + 16)
    response = auth_client.post(
        "/api/v1/system/dicts/",
        json={
            "name": f"长请求ID{uuid.uuid4().hex[:6]}",
            "dictCode": f"long_request_id_{uuid.uuid4().hex[:6]}",
            "remark": "请求 ID 长度测试",
            "status": 1,
        },
        headers={"X-Request-ID": request_id},
    )

    expected_request_id = request_id[:MAX_REQUEST_ID_LENGTH]
    assert response.status_code in (200, 201)
    assert response.headers["X-Request-ID"] == expected_request_id

    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "POST"},
    ).json()["data"]
    row = next(row for row in page["list"] if row["requestId"] == expected_request_id)
    assert row["requestId"] == expected_request_id


def test_failed_mutating_request_persists_error_summary(auth_client, test_user):
    """失败写请求必须记录可定位且已脱敏的错误摘要。"""
    request_id = f"fastapi-audit-failure-{uuid.uuid4().hex[:6]}"
    response = auth_client.post(
        "/api/v1/system/dicts/",
        json={
            "name": "失败审计字典",
            "dictCode": f"failed_audit_{uuid.uuid4().hex[:6]}",
            "remark": "校验失败不会创建记录",
            "status": "invalid-status",
            "password": "must-not-leak",
        },
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code >= 400
    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "POST", "status": 0},
    ).json()["data"]
    row = next(row for row in page["list"] if row["requestId"] == request_id)
    assert row["errorMsg"]
    assert row["responseBody"]
    assert "must-not-leak" not in row["errorMsg"]
    assert "must-not-leak" not in row["responseBody"]


def test_get_request_is_not_persisted(auth_client, test_user):
    """GET 读请求不落库，审计表只保留写操作。"""
    auth_client.get("/api/v1/system/dicts/")
    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"pageNum": 1, "pageSize": 50, "method": "GET"},
    ).json()["data"]
    assert page["total"] == 0
