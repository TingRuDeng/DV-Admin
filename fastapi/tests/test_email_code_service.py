from app.services.email_code_service import EmailCodeError, EmailCodeService


def test_email_code_route_accepts_captcha(client):
    import asyncio

    from app.services.captcha_service import get_captcha_service
    from app.services.email_code_service import email_code_service

    captcha = client.get("/api/v1/oauth/captcha/").json()["data"]
    code = asyncio.run(get_captcha_service()._cache.get(captcha["captchaKey"]))
    response = client.post(
        "/api/v1/oauth/email-code/",
        json={
            "purpose": "register",
            "email": "route@example.com",
            "captcha_key": captcha["captchaKey"],
            "captcha_code": code,
        },
    )
    assert response.status_code == 200
    assert response.json()["code"] == 20000
    assert email_code_service.captured(purpose="register", email="route@example.com")


def test_email_code_is_one_time_and_captured_locally():
    service = EmailCodeService()
    service.send(purpose="register", email="User@example.com")
    code = service.captured(purpose="register", email="user@example.com")
    assert code and service.verify(purpose="register", email="user@example.com", code=code)
    assert not service.verify(purpose="register", email="user@example.com", code=code)


def test_email_code_resend_is_throttled():
    service = EmailCodeService()
    service.send(purpose="reset_password", email="user@example.com")
    try:
        service.send(purpose="reset_password", email="user@example.com")
    except EmailCodeError as exc:
        assert "频繁" in str(exc)
    else:
        raise AssertionError("second send should be throttled")


def test_email_code_route_returns_retry_after(client):
    payload = {"purpose": "register", "email": "throttle-route@example.com"}
    assert client.post("/api/v1/oauth/email-code/", json=payload).status_code == 200
    response = client.post("/api/v1/oauth/email-code/", json=payload)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["code"] == 429
