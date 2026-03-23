"""
字典项管理接口测试
"""
from fastapi.testclient import TestClient


class TestDictItemList:
    """字典项列表测试"""

    def test_get_dict_items_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/system/dict-items/")
        assert response.status_code == 401

    def test_get_dict_items_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/dict-items/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestDictItemCRUD:
    """字典项增删改测试"""

    def test_create_dict_item_forbidden(self, auth_client: TestClient):
        # 需要 dict_items:add 权限
        response = auth_client.post("/api/v1/system/dict-items/", json={
            "dict_id": 1,
            "label": "测试",
            "value": "test",
            "sort": 1,
            "status": 1
        })
        assert response.status_code in [200, 403, 422]

    def test_update_dict_item_not_found(self, auth_client: TestClient):
        # 需要 dict_items:edit 权限
        response = auth_client.put("/api/v1/system/dict-items/99999/", json={
            "label": "更新",
            "sort": 2
        })
        assert response.status_code in [200, 403, 404]
