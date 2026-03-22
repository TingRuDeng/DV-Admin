# -*- coding: utf-8 -*-
"""
部门管理接口测试
"""
import pytest
import pytest_asyncio
import uuid
from fastapi.testclient import TestClient

from app.db.models.system import Departments


@pytest_asyncio.fixture
async def test_dept_for_api(db):
    """创建测试部门"""
    dept = await Departments.create(
        name=f"API测试部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    return dept


class TestDeptList:
    """部门列表测试"""

    def test_get_depts_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/system/departments/")
        assert response.status_code == 401

    def test_get_depts_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/departments/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
        assert isinstance(data.get("data"), list)


class TestDeptOptions:
    """部门下拉选项测试"""

    def test_get_dept_options(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/departments/options")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestDeptDetail:
    """部门详情测试"""

    def test_get_dept_detail_not_found(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/departments/99999/")
        assert response.status_code == 404


class TestDeptCRUD:
    """部门增删改测试"""

    def test_create_dept(self, auth_client: TestClient):
        response = auth_client.post("/api/v1/system/departments/", json={
            "name": f"测试部门_{uuid.uuid4().hex[:6]}",
            "sort": 1,
            "status": 1,
            "parentId": None
        })
        assert response.status_code == 200

    def test_update_dept_not_found(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/departments/99999/", json={
            "name": "更新部门",
            "sort": 2
        })
        assert response.status_code == 404
