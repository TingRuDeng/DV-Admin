import asyncio

from app.core.security import hash_password
from app.db.models.oauth import Users
from app.db.models.system import Roles
from app.services.captcha_service import get_captcha_service
from app.services.email_code_service import email_code_service


def run(coro):
    async def resolve():
        return await coro

    return asyncio.run(resolve())


def captcha_payload(client):
    data = client.get("/api/v1/oauth/captcha/").json()["data"]
    code = asyncio.run(get_captcha_service()._cache.get(data["captchaKey"]))
    return data["captchaKey"], code


def test_registration_activates_user_and_assigns_default_role(client, db):
    role = run(Roles.create(name="Public default", code="public-default", is_default=1, status=1))
    captcha_key, captcha_code = captcha_payload(client)
    run(email_code_service.asend(purpose="register", email="new@example.com"))
    email_code = email_code_service.captured(purpose="register", email="new@example.com")

    response = client.post(
        "/api/v1/oauth/register/",
        json={
            "username": "new-user",
            "email": "new@example.com",
            "password": "a sufficiently long passphrase",
            "confirmPassword": "a sufficiently long passphrase",
            "captchaKey": captcha_key,
            "captchaCode": captcha_code,
            "emailCode": email_code,
        },
    )

    assert response.status_code == 200, response.text
    user = run(Users.filter(username="new-user").first())
    assert user is not None
    assert user.is_active == 1
    assert run(user.roles.filter(id=role.id).exists())


def test_password_reset_revokes_old_refresh_token(client, db):
    old_password = "old sufficiently long passphrase"
    new_password = "new sufficiently long passphrase"
    user = run(
        Users.create(
            username="reset-user",
            email="reset@example.com",
            password=run(hash_password(old_password)),
            is_active=1,
        )
    )
    login = client.post("/api/v1/oauth/login/", json={"username": user.username, "password": old_password})
    assert login.status_code == 200, login.text
    old_refresh = login.json()["data"]["refreshToken"]

    captcha_key, captcha_code = captcha_payload(client)
    run(email_code_service.asend(purpose="reset_password", email=user.email))
    email_code = email_code_service.captured(purpose="reset_password", email=user.email)
    reset = client.post(
        "/api/v1/oauth/password/reset/",
        json={
            "username": user.username,
            "email": user.email,
            "newPassword": new_password,
            "confirmPassword": new_password,
            "captchaKey": captcha_key,
            "captchaCode": captcha_code,
            "emailCode": email_code,
        },
    )
    assert reset.status_code == 200, reset.text

    refresh = client.post("/api/v1/oauth/refresh-token/", json={"refreshToken": old_refresh})
    assert refresh.status_code != 200 or refresh.json().get("code") != 20000
    assert client.post(
        "/api/v1/oauth/login/",
        json={"username": user.username, "password": new_password},
    ).status_code == 200
