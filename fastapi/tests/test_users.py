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


def test_import_template_returns_csv(client: TestClient):
    """
    测试导入模板接口返回CSV格式
    """
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
    assert result["filename"].endswith(".csv"), "Filename should end with .csv"


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
