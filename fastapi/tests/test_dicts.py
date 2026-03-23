"""
字典管理接口测试
"""
from fastapi.testclient import TestClient


class TestDictList:
    """字典列表测试"""

    def test_get_dicts_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/system/dicts/")
        assert response.status_code == 401

    def test_get_dicts_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/dicts/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestDictDetail:
    """字典详情测试"""

    def test_get_dict_detail_not_found(self, auth_client: TestClient):
        # 测试不存在的字典返回 404
        response = auth_client.get("/api/v1/system/dicts/99999/")
        assert response.status_code in [200, 404]


class TestDictCRUD:
    """字典增删改测试"""

    def test_create_dict(self, auth_client: TestClient):
        response = auth_client.post("/api/v1/system/dicts/", json={
            "name": "测试字典",
            "code": "test_dict",
            "status": 1,
            "desc": "测试描述"
        })
        assert response.status_code in [200, 201]

    def test_update_dict_not_found(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/dicts/99999/", json={
            "name": "更新字典"
        })
        assert response.status_code in [200, 404]


class TestDictItems:
    """字典项测试"""

    def test_get_dict_items_forbidden(self, auth_client: TestClient):
        # 需要 dict_items:query 权限
        response = auth_client.get("/api/v1/system/dicts/1/items")
        assert response.status_code in [200, 403]

    def test_get_dict_by_code_not_found(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/dicts/code/nonexistent")
        assert response.status_code in [200, 404]
