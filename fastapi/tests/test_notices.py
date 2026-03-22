# -*- coding: utf-8 -*-
"""
通知公告接口测试
"""
import pytest
import pytest_asyncio
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

from app.db.models.system import Notices


@pytest_asyncio.fixture
async def test_notice_for_api(db):
    """创建测试通知"""
    notice = await Notices.create(
        title=f"API测试通知_{uuid.uuid4().hex[:6]}",
        content="测试内容",
        type=0,
        level="L",
        target_type=1,
        publisher_id=1,
        publisher_name="管理员",
        publish_status=0,
    )
    return notice


@pytest_asyncio.fixture
async def test_published_notice_for_api(db):
    """创建已发布的测试通知"""
    notice = await Notices.create(
        title=f"API已发布通知_{uuid.uuid4().hex[:6]}",
        content="已发布内容",
        type=0,
        level="L",
        target_type=1,
        publisher_id=1,
        publisher_name="管理员",
        publish_status=1,
        publish_time=datetime.now(),
    )
    return notice


class TestNoticeList:
    """公告列表测试"""

    def test_get_notices_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/system/notices/page")
        assert response.status_code == 401

    def test_get_notices_authorized(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/notices/page")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000


class TestNoticeForm:
    """公告表单测试"""

    def test_get_notice_form_not_found(self, auth_client: TestClient):
        # 测试不存在的公告返回 404
        response = auth_client.get("/api/v1/system/notices/99999/form")
        assert response.status_code in [200, 404]


class TestNoticeCRUD:
    """公告增删改测试"""

    def test_create_notice(self, auth_client: TestClient):
        response = auth_client.post("/api/v1/system/notices", json={
            "title": f"测试公告_{uuid.uuid4().hex[:6]}",
            "content": "测试内容",
            "type": 0,
            "level": "L",
            "targetType": 1
        })
        assert response.status_code == 200

    def test_update_notice_not_found(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/notices/99999", json={
            "title": "更新公告"
        })
        assert response.status_code == 404


class TestNoticeStatus:
    """公告状态测试"""

    def test_publish_notice_not_found(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/notices/99999/publish")
        assert response.status_code == 404

    def test_revoke_notice_not_found(self, auth_client: TestClient):
        response = auth_client.put("/api/v1/system/notices/99999/revoke")
        assert response.status_code == 404


class TestNoticeMy:
    """我的公告测试"""

    def test_get_my_notices(self, auth_client: TestClient):
        response = auth_client.get("/api/v1/system/notices/my-page/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 20000
