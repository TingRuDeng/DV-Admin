"""
通知服务后台查询测试。
"""
import pytest

from app.core.exceptions import NotFound
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


class TestNoticeServiceGetPage:
    """测试通知分页查询。"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_notices_for_service):
        """测试基本分页查询。"""
        result = await notice_service.get_page(page_num=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_title(self, db, test_notices_for_service):
        """测试按标题过滤。"""
        result = await notice_service.get_page(
            page_num=1,
            page_size=10,
            title="测试通知",
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_publish_status(self, db, test_notices_for_service):
        """测试按发布状态过滤。"""
        result = await notice_service.get_page(
            page_num=1,
            page_size=10,
            publish_status=0,
        )
        assert result.total >= 1
        for notice in result.list:
            assert notice.publish_status == 0

    @pytest.mark.asyncio
    async def test_get_page_empty(self, db):
        """测试空结果。"""
        result = await notice_service.get_page(
            page_num=1,
            page_size=10,
            title="nonexistent_notice_xyz",
        )
        assert result.total == 0
        assert len(result.list) == 0


class TestNoticeServiceGetForm:
    """测试获取通知表单。"""

    @pytest.mark.asyncio
    async def test_get_form_existing(self, db, test_notices_for_service):
        """测试获取存在的通知表单。"""
        notice = test_notices_for_service[0]
        result = await notice_service.get_form(notice.id)
        assert result.id == notice.id
        assert result.title == notice.title

    @pytest.mark.asyncio
    async def test_get_form_nonexistent(self, db):
        """测试获取不存在的通知表单。"""
        with pytest.raises(NotFound):
            await notice_service.get_form(99999)
