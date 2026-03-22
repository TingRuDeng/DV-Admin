# -*- coding: utf-8 -*-
"""
验证码接口测试 - TDD 红阶段
"""
import pytest
from fastapi.testclient import TestClient


def test_captcha_returns_key_and_base64(client: TestClient):
    """
    测试验证码接口返回正确的格式
    - 响应包含 captchaKey
    - 响应包含 captchaBase64
    - captchaBase64 是有效的 base64 图片
    """
    response = client.get("/api/v1/oauth/captcha/")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    # FastAPI 使用 code=20000 表示成功
    assert data.get("code") == 20000, f"Expected code 20000, got {data.get('code')}"

    result = data.get("data", {})
    assert "captchaKey" in result, "Response should contain captchaKey"
    assert "captchaBase64" in result, "Response should contain captchaBase64"

    # 验证 captchaBase64 是有效的 base64 图片格式
    captcha_base64 = result["captchaBase64"]
    assert captcha_base64.startswith("data:image/png;base64,"), \
        "captchaBase64 should be a valid base64 image"


def test_captcha_returns_unique_keys(client: TestClient):
    """
    测试每次调用返回不同的验证码 key
    """
    response1 = client.get("/api/v1/oauth/captcha/")
    response2 = client.get("/api/v1/oauth/captcha/")

    data1 = response1.json()["data"]
    data2 = response2.json()["data"]

    # 每次请求应该返回不同的 key
    assert data1["captchaKey"] != data2["captchaKey"], \
        "Each request should return a unique captchaKey"
