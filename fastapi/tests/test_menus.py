# -*- coding: utf-8 -*-
"""
菜单管理接口测试
"""
import pytest
from fastapi.testclient import TestClient


class TestMenuList:
    """菜单列表测试"""

    def test_get_menus_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/system/menus/")
        assert response.status_code == 401

    def test_get_menus_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/menus/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), list)


class TestMenuOptions:
    """菜单下拉选项测试"""

    def test_get_menu_options(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/menus/options/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestMenuPerms:
    """菜单权限标识测试"""

    def test_get_menu_perms(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/menus/perms")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), list)


class TestMenuDetail:
    """菜单详情测试"""

    def test_get_menu_detail(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/menus/1/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestMenuCRUD:
    """菜单增删改测试"""

    def test_create_menu(self, auth_client: TestClient):
        response = auth_client.post("/api/v1/system/menus/", json={
            "name": "测试菜单",
            "type": "MENU",
            "path": "/test",
            "component": "test/index",
            "sort": 1,
            "status": 1
        })
        assert response.status_code == 200

    def test_update_menu(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/menus/1/", json={
            "name": "更新菜单",
            "type": "MENU",
            "path": "/test",
            "sort": 2
        })
        assert response.status_code == 200
