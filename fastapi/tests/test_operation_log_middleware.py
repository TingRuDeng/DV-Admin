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
