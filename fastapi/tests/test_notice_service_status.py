"""
通知服务发布状态测试。
"""
import pytest

from app.core.exceptions import NotFound
from app.db.models.system import NoticeReads, Notices
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


class TestNoticeServicePublish:
    """测试发布通知。"""

    @pytest.mark.asyncio
    async def test_publish(self, db, test_notices_for_service):
        """测试发布通知。"""
        notice = test_notices_for_service[0]
        await notice_service.publish(notice.id)

        updated = await Notices.get(id=notice.id)
        assert updated.publish_status == 1
        assert updated.publish_time is not None
        assert updated.publish_time.tzinfo is None

    @pytest.mark.asyncio
    async def test_publish_nonexistent(self, db):
        """测试发布不存在的通知。"""
        with pytest.raises(NotFound):
            await notice_service.publish(99999)

    @pytest.mark.asyncio
    async def test_publish_already_published(self, db, test_published_notice):
        """测试发布已发布的通知。"""
        await notice_service.publish(test_published_notice.id)


class TestNoticeServiceRevoke:
    """测试撤销通知。"""

    @pytest.mark.asyncio
    async def test_revoke(self, db, test_published_notice):
        """测试撤销通知。"""
        await notice_service.revoke(test_published_notice.id)

        updated = await Notices.get(id=test_published_notice.id)
        assert updated.publish_status == -1
        assert updated.revoke_time is not None
        assert updated.revoke_time.tzinfo is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent(self, db):
        """测试撤销不存在的通知。"""
        with pytest.raises(NotFound):
            await notice_service.revoke(99999)

    @pytest.mark.asyncio
    async def test_revoke_unpublished(self, db, test_notices_for_service):
        """测试撤销未发布的通知。"""
        notice = test_notices_for_service[0]
        await notice_service.revoke(notice.id)


class TestNoticeServiceReadAll:
    """测试全部已读。"""

    @pytest.mark.asyncio
    async def test_read_all(self, db, test_published_notice):
        """测试标记全部已读。"""
        await notice_service.read_all(user_id=1)

        read = await NoticeReads.filter(
            notice_id=test_published_notice.id,
            user_id=1,
        ).exists()
        assert read

    @pytest.mark.asyncio
    async def test_read_all_empty(self, db):
        """测试无已发布通知时标记全部已读。"""
        await Notices.all().delete()
        await notice_service.read_all(user_id=1)
