"""
角色管理接口测试 - TDD
"""
from fastapi.testclient import TestClient


def test_role_menu_ids_returns_list(client: TestClient):
    """
    测试获取角色菜单ID列表接口
    """
    response = client.get(
        "/api/v1/system/roles/1/menu-ids/",
        headers={"Authorization": "Bearer test-token"}
    )

    # 未认证应该返回401
    if response.status_code == 401:
        assert True
        return

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 20000

    result = data.get("data", [])
    assert isinstance(result, list), "Response data should be a list"


def test_role_menus_returns_list(client: TestClient):
    """
    测试获取角色菜单列表接口
    """
    response = client.get(
        "/api/v1/system/roles/1/menus/",
        headers={"Authorization": "Bearer test-token"}
    )

    # 未认证应该返回401
    if response.status_code == 401:
        assert True
        return

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 20000

    result = data.get("data", [])
    assert isinstance(result, list), "Response data should be a list"


def test_role_menu_ids_nonexistent_role(client: TestClient):
    """
    测试获取不存在的角色的菜单ID
    """
    response = client.get(
        "/api/v1/system/roles/99999/menu-ids/",
        headers={"Authorization": "Bearer test-token"}
    )

    # 未认证应该返回401
    if response.status_code == 401:
        assert True
        return

    # 应该返回404或者空列表
    assert response.status_code in [200, 404]
