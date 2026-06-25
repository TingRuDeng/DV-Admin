"""
通知服务详情测试。
"""
import pytest

from app.core.exceptions import NotFound
from app.db.models.system import NoticeReads
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


class TestNoticeServiceGetDetail:
    """测试获取通知详情。"""

    @pytest.mark.asyncio
    async def test_get_detail_existing(self, db, test_notices_for_service):
        """测试获取存在的通知详情。"""
        notice = test_notices_for_service[0]
        result = await notice_service.get_detail(notice.id)
        assert result.id == notice.id
        assert result.title == notice.title

    @pytest.mark.asyncio
    async def test_get_detail_nonexistent(self, db):
        """测试获取不存在的通知详情。"""
        with pytest.raises(NotFound):
            await notice_service.get_detail(99999)

    @pytest.mark.asyncio
    async def test_get_detail_with_user(self, db, test_published_notice):
        """测试获取通知详情并标记已读。"""
        result = await notice_service.get_detail(test_published_notice.id, user_id=1)
        assert result.id == test_published_notice.id

        read = await NoticeReads.filter(
            notice_id=test_published_notice.id,
            user_id=1,
        ).exists()
        assert read
