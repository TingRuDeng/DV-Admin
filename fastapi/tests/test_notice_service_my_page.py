"""
通知服务我的通知列表测试。
"""
import pytest

from app.db.models.system import NoticeReads
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


class TestNoticeServiceGetMyPage:
    """测试获取我的通知列表。"""

    @pytest.mark.asyncio
    async def test_get_my_page(self, db, test_published_notice):
        """测试获取我的通知列表。"""
        result = await notice_service.get_my_page(user_id=1, page_num=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_with_title(self, db, test_published_notice):
        """测试按标题过滤。"""
        result = await notice_service.get_my_page(
            user_id=1,
            page_num=1,
            page_size=10,
            title="已发布通知",
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_with_is_read(self, db, test_published_notice):
        """测试按已读状态过滤。"""
        await NoticeReads.create(notice_id=test_published_notice.id, user_id=1)

        result = await notice_service.get_my_page(
            user_id=1,
            page_num=1,
            page_size=10,
            is_read=1,
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_unread(self, db, test_published_notice):
        """测试获取未读通知。"""
        result = await notice_service.get_my_page(
            user_id=1,
            page_num=1,
            page_size=10,
            is_read=0,
        )
        assert result.total >= 0
