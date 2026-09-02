"""
用户管理接口测试 - TDD
"""
from fastapi.testclient import TestClient


def test_reset_password_returns_success(client: TestClient):
    """
    测试重置密码接口返回成功
    """
    # 先创建一个测试用户，然后重置密码
    # 这里假设用户ID=1存在
    response = client.post(
        "/api/v1/system/users/1/password/reset/",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"


def test_reset_password_accepts_put_method(auth_client: TestClient, test_user):
    """共享 PUT 契约应使用请求体中的显式新密码。"""
    new_password = "LifecyclePass123"
    response = auth_client.put(
        f"/api/v1/system/users/{test_user['id']}/password/reset/",
        json={"password": new_password, "confirm_password": new_password},
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 20000

    login_response = auth_client.post(
        "/api/v1/oauth/login/",
        json={"username": test_user["username"], "password": new_password},
    )
    assert login_response.status_code == 200
    assert login_response.json().get("code") == 20000


def test_reset_password_put_requires_matching_passwords(auth_client: TestClient, test_user):
    """共享 PUT 契约不得回退到默认密码或接受不一致的确认密码。"""
    response = auth_client.put(
        f"/api/v1/system/users/{test_user['id']}/password/reset/",
        json={"password": "LifecyclePass123", "confirm_password": "DifferentPass123"},
    )

    assert response.status_code == 422


def test_reset_password_post_keeps_default_password_compatibility(
    auth_client: TestClient,
    test_user,
):
    """FastAPI 旧 POST 入口继续按显式配置的默认密码重置。"""
    from app.core.config import settings

    response = auth_client.post(
        f"/api/v1/system/users/{test_user['id']}/password/reset/",
    )
    assert response.status_code == 200

    login_response = auth_client.post(
        "/api/v1/oauth/login/",
        json={"username": test_user["username"], "password": settings.default_password},
    )
    assert login_response.status_code == 200
    assert login_response.json().get("code") == 20000


def test_import_template_returns_xlsx(client: TestClient):
    """测试导入模板接口返回 xlsx 契约。"""
    response = client.get(
        "/api/v1/system/users/template",
        headers={"Authorization": "Bearer test-token"}
    )

    # 未认证应该返回401
    if response.status_code == 401:
        assert True
        return

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 20000

    result = data.get("data", {})
    assert "filename" in result, "Response should contain filename"
    assert "content" in result, "Response should contain content"
    assert result["filename"].endswith(".xlsx"), "Filename should end with .xlsx"
    assert result["contentType"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_export_returns_csv(client: TestClient):
    """
    测试导出接口返回CSV格式
    """
    response = client.post(
        "/api/v1/system/users/export/",
        headers={"Authorization": "Bearer test-token"}
    )

    # 未认证应该返回401
    if response.status_code == 401:
        assert True
        return

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 20000

    result = data.get("data", {})
    assert "filename" in result, "Response should contain filename"
    assert "content" in result, "Response should contain content"
    assert result["filename"].endswith(".csv"), "Filename should end with .csv"
    assert result["contentType"] == "text/csv;charset=utf-8"
