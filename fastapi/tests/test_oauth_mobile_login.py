"""用户名字段也接受 11 位手机号，与 Django 实现保持一致。"""

import uuid

import pytest_asyncio

from scripts.api_error_codes import ERROR_CODE, SUCCESS_CODE

MOBILE = "13900139000"
PASSWORD = "admin123"


async def _create_mobile_user(is_active: int) -> dict:
    from app.core.security import hash_password
    from app.db.models.oauth import Users

    user = await Users.create(
        username=f"mobile_{uuid.uuid4().hex[:8]}",
        password=await hash_password(PASSWORD),
        name="手机号用户",
        is_active=is_active,
        mobile=MOBILE,
    )
    return {"id": user.id, "username": user.username}


@pytest_asyncio.fixture(scope="function")
async def mobile_user(db) -> dict:
    return await _create_mobile_user(is_active=1)


@pytest_asyncio.fixture(scope="function")
async def disabled_mobile_user(db) -> dict:
    return await _create_mobile_user(is_active=0)


def _login(client, username: str, password: str = PASSWORD):
    return client.post("/api/v1/oauth/login/", json={"username": username, "password": password})


def test_login_with_mobile(client, mobile_user):
    response = _login(client, MOBILE)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == SUCCESS_CODE
    assert body["data"]["accessToken"]


def test_login_with_username_still_works(client, mobile_user):
    response = _login(client, mobile_user["username"])
    assert response.status_code == 200
    assert response.json()["code"] == SUCCESS_CODE


def test_login_with_mobile_and_wrong_password(client, mobile_user):
    response = _login(client, MOBILE, "wrong-password")
    assert response.json()["code"] == ERROR_CODE


def test_login_with_mobile_of_disabled_user(client, disabled_mobile_user):
    response = _login(client, MOBILE)
    body = response.json()
    assert body["code"] == ERROR_CODE
    assert "禁用" in body["message"]
