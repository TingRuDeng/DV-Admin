"""退出登录必须让当前会话的 Refresh Token 失效。"""

from scripts.api_error_codes import REFRESH_TOKEN_INVALID_CODE, SUCCESS_CODE


def _login(client, user) -> tuple[str, str]:
    response = client.post(
        "/api/v1/oauth/login/",
        json={"username": user["username"], "password": user["password"]},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return data["accessToken"], data["refreshToken"]


def _logout(client, access_token: str, body=None):
    headers = {"Authorization": f"Bearer {access_token}"}
    if body is None:
        return client.post("/api/v1/oauth/logout/", headers=headers)
    return client.post("/api/v1/oauth/logout/", headers=headers, json=body)


def _refresh(client, refresh_token: str):
    return client.post("/api/v1/oauth/refresh-token/", json={"refreshToken": refresh_token})


def test_logout_with_refresh_token_blocks_later_refresh(client, test_user_with_role):
    access_token, refresh_token = _login(client, test_user_with_role)

    response = _logout(client, access_token, {"refreshToken": refresh_token})
    assert response.status_code == 200
    assert response.json()["code"] == SUCCESS_CODE

    response = _refresh(client, refresh_token)
    assert response.status_code == 401
    assert response.json()["code"] == REFRESH_TOKEN_INVALID_CODE


def test_logout_without_body_still_succeeds(client, test_user_with_role):
    access_token, _refresh_token = _login(client, test_user_with_role)

    response = _logout(client, access_token)
    assert response.status_code == 200
    assert response.json()["code"] == SUCCESS_CODE


def test_logout_ignores_malformed_refresh_token(client, test_user_with_role):
    access_token, _refresh_token = _login(client, test_user_with_role)

    response = _logout(client, access_token, {"refreshToken": "not-a-jwt"})
    assert response.status_code == 200
    assert response.json()["code"] == SUCCESS_CODE


def test_logout_cannot_revoke_another_users_refresh_token(client, test_user_with_role, test_user):
    access_token, _refresh_token = _login(client, test_user_with_role)
    _other_access, other_refresh = _login(client, test_user)

    response = _logout(client, access_token, {"refreshToken": other_refresh})
    assert response.status_code == 200

    response = _refresh(client, other_refresh)
    assert response.status_code == 200
    assert response.json()["code"] == SUCCESS_CODE
