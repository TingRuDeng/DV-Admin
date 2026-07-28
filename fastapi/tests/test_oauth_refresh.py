"""OAuth 刷新令牌轮换测试。"""

from fastapi.testclient import TestClient

from app.core.security import create_refresh_token

pytest_plugins = ["token_blacklist_fixtures"]


def login(client: TestClient, user: dict) -> dict:
    """登录并返回令牌响应数据。"""
    response = client.post(
        "/api/v1/oauth/login/",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_refresh_token_is_rotated_and_cannot_be_replayed(
    client: TestClient,
    test_user_with_role,
):
    """刷新后旧令牌失效，新令牌仍可继续轮换。"""
    tokens = login(client, test_user_with_role)
    refresh_token = tokens["refreshToken"]

    response = client.post(
        "/api/v1/oauth/refresh-token/",
        json={"refreshToken": refresh_token},
    )
    assert response.status_code == 200
    rotated_refresh_token = response.json()["data"]["refreshToken"]
    assert rotated_refresh_token != refresh_token

    replay_response = client.post(
        "/api/v1/oauth/refresh-token/",
        json={"refreshToken": refresh_token},
    )
    assert replay_response.status_code == 401
    assert replay_response.json()["code"] == 40002

    rotated_response = client.post(
        "/api/v1/oauth/refresh-token/",
        json={"refreshToken": rotated_refresh_token},
    )
    assert rotated_response.status_code == 200


def test_refresh_token_with_non_numeric_subject_is_rejected(client: TestClient):
    """畸形 subject 应按刷新令牌错误处理，不能变成 500。"""
    response = client.post(
        "/api/v1/oauth/refresh-token/",
        json={"refreshToken": create_refresh_token("not-a-user-id")},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 40002
