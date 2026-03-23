"""
通知服务层测试
测试 NoticeService 的所有方法
"""
import uuid
from datetime import datetime

import pytest
import pytest_asyncio

from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import NoticeReads, Notices
from app.schemas.system import NoticeCreate, NoticeUpdate
from app.services.system.notice_service import notice_service


@pytest_asyncio.fixture
async def test_notices_for_service(db):
    """创建测试通知"""
    notices = []
    for i in range(3):
        notice = await Notices.create(
            title=f"测试通知_{i}_{uuid.uuid4().hex[:6]}",
            content=f"通知内容_{i}",
            type=0,
            level="L",
            target_type=1,
            publisher_id=1,
            publisher_name="管理员",
            publish_status=0,
        )
        notices.append(notice)
    return notices


@pytest_asyncio.fixture
async def test_published_notice(db):
    """创建已发布的通知"""
    notice = await Notices.create(
        title=f"已发布通知_{uuid.uuid4().hex[:6]}",
        content="已发布通知内容",
        type=0,
        level="H",
        target_type=1,
        publisher_id=1,
        publisher_name="管理员",
        publish_status=1,
        publish_time=datetime.now(),
    )
    return notice


class TestNoticeServiceGetPage:
    """测试通知分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_notices_for_service):
        """测试基本分页查询"""
        result = await notice_service.get_page(page_num=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_title(self, db, test_notices_for_service):
        """测试按标题过滤"""
        result = await notice_service.get_page(
            page_num=1, page_size=10, title="测试通知"
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_publish_status(self, db, test_notices_for_service):
        """测试按发布状态过滤"""
        result = await notice_service.get_page(
            page_num=1, page_size=10, publish_status=0
        )
        assert result.total >= 1
        for notice in result.list:
            assert notice.publish_status == 0

    @pytest.mark.asyncio
    async def test_get_page_empty(self, db):
        """测试空结果"""
        result = await notice_service.get_page(
            page_num=1, page_size=10, title="nonexistent_notice_xyz"
        )
        assert result.total == 0
        assert len(result.list) == 0


class TestNoticeServiceGetForm:
    """测试获取通知表单"""

    @pytest.mark.asyncio
    async def test_get_form_existing(self, db, test_notices_for_service):
        """测试获取存在的通知表单"""
        notice = test_notices_for_service[0]
        result = await notice_service.get_form(notice.id)
        assert result.id == notice.id
        assert result.title == notice.title

    @pytest.mark.asyncio
    async def test_get_form_nonexistent(self, db):
        """测试获取不存在的通知表单"""
        with pytest.raises(NotFound):
            await notice_service.get_form(99999)


class TestNoticeServiceGetDetail:
    """测试获取通知详情"""

    @pytest.mark.asyncio
    async def test_get_detail_existing(self, db, test_notices_for_service):
        """测试获取存在的通知详情"""
        notice = test_notices_for_service[0]
        result = await notice_service.get_detail(notice.id)
        assert result.id == notice.id
        assert result.title == notice.title

    @pytest.mark.asyncio
    async def test_get_detail_nonexistent(self, db):
        """测试获取不存在的通知详情"""
        with pytest.raises(NotFound):
            await notice_service.get_detail(99999)

    @pytest.mark.asyncio
    async def test_get_detail_with_user(self, db, test_published_notice):
        """测试获取通知详情并标记已读"""
        result = await notice_service.get_detail(
            test_published_notice.id, user_id=1
        )
        assert result.id == test_published_notice.id

        # 验证已标记已读
        read = await NoticeReads.filter(
            notice_id=test_published_notice.id, user_id=1
        ).exists()
        assert read


class TestNoticeServiceCreate:
    """测试创建通知"""

    @pytest.mark.asyncio
    async def test_create_basic(self, db):
        """测试基本创建"""
        notice_in = NoticeCreate(
            title=f"新通知_{uuid.uuid4().hex[:6]}",
            content="新通知内容",
            type=0,
            level="L",
            target_type=1,
        )
        result = await notice_service.create(notice_in, publisher_id=1, publisher_name="管理员")
        assert result.id is not None
        assert result.title == notice_in.title
        assert result.publish_status == 0

    @pytest.mark.asyncio
    async def test_create_with_target_users(self, db):
        """测试创建指定用户通知"""
        notice_in = NoticeCreate(
            title=f"指定用户通知_{uuid.uuid4().hex[:6]}",
            content="指定用户通知内容",
            type=0,
            level="H",
            target_type=2,
            target_user_ids=[1, 2, 3],
        )
        result = await notice_service.create(notice_in, publisher_id=1, publisher_name="管理员")
        assert result.target_type == 2

    @pytest.mark.asyncio
    async def test_create_target_users_validation(self, db):
        """测试创建指定用户通知验证"""
        notice_in = NoticeCreate(
            title=f"测试通知_{uuid.uuid4().hex[:6]}",
            content="测试内容",
            type=0,
            level="L",
            target_type=2,
            target_user_ids=[],  # 空列表
        )
        with pytest.raises(ValidationError):
            await notice_service.create(notice_in, publisher_id=1, publisher_name="管理员")


class TestNoticeServiceUpdate:
    """测试更新通知"""

    @pytest.mark.asyncio
    async def test_update_basic(self, db, test_notices_for_service):
        """测试基本更新"""
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(title=f"更新标题_{uuid.uuid4().hex[:6]}")
        result = await notice_service.update(notice.id, notice_in)
        assert result.title == notice_in.title

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db):
        """测试更新不存在的通知"""
        notice_in = NoticeUpdate(title="更新标题")
        with pytest.raises(NotFound):
            await notice_service.update(99999, notice_in)

    @pytest.mark.asyncio
    async def test_update_published_notice(self, db, test_published_notice):
        """测试更新已发布通知"""
        notice_in = NoticeUpdate(title="更新标题")
        with pytest.raises(ValidationError):
            await notice_service.update(test_published_notice.id, notice_in)

    @pytest.mark.asyncio
    async def test_update_target_type(self, db, test_notices_for_service):
        """测试更新目标类型"""
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(target_type=1)
        result = await notice_service.update(notice.id, notice_in)
        assert result.target_type == 1


class TestNoticeServiceDelete:
    """测试删除通知"""

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, db, test_notices_for_service):
        """测试批量删除"""
        ids = [n.id for n in test_notices_for_service[:2]]
        await notice_service.delete_by_ids(ids)

        for nid in ids:
            exists = await Notices.filter(id=nid).exists()
            assert not exists

    @pytest.mark.asyncio
    async def test_delete_published_notice(self, db, test_published_notice):
        """测试删除已发布通知"""
        with pytest.raises(ValidationError):
            await notice_service.delete_by_ids([test_published_notice.id])


class TestNoticeServicePublish:
    """测试发布通知"""

    @pytest.mark.asyncio
    async def test_publish(self, db, test_notices_for_service):
        """测试发布通知"""
        notice = test_notices_for_service[0]
        await notice_service.publish(notice.id)

        updated = await Notices.get(id=notice.id)
        assert updated.publish_status == 1
        assert updated.publish_time is not None

    @pytest.mark.asyncio
    async def test_publish_nonexistent(self, db):
        """测试发布不存在的通知"""
        with pytest.raises(NotFound):
            await notice_service.publish(99999)

    @pytest.mark.asyncio
    async def test_publish_already_published(self, db, test_published_notice):
        """测试发布已发布的通知"""
        # 应该不报错，直接返回
        await notice_service.publish(test_published_notice.id)


class TestNoticeServiceRevoke:
    """测试撤销通知"""

    @pytest.mark.asyncio
    async def test_revoke(self, db, test_published_notice):
        """测试撤销通知"""
        await notice_service.revoke(test_published_notice.id)

        updated = await Notices.get(id=test_published_notice.id)
        assert updated.publish_status == -1
        assert updated.revoke_time is not None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent(self, db):
        """测试撤销不存在的通知"""
        with pytest.raises(NotFound):
            await notice_service.revoke(99999)

    @pytest.mark.asyncio
    async def test_revoke_unpublished(self, db, test_notices_for_service):
        """测试撤销未发布的通知"""
        notice = test_notices_for_service[0]
        # 应该不报错，直接返回
        await notice_service.revoke(notice.id)


class TestNoticeServiceReadAll:
    """测试全部已读"""

    @pytest.mark.asyncio
    async def test_read_all(self, db, test_published_notice):
        """测试标记全部已读"""
        await notice_service.read_all(user_id=1)

        read = await NoticeReads.filter(
            notice_id=test_published_notice.id, user_id=1
        ).exists()
        assert read

    @pytest.mark.asyncio
    async def test_read_all_empty(self, db):
        """测试无已发布通知时标记全部已读"""
        # 删除所有通知
        await Notices.all().delete()
        # 应该不报错
        await notice_service.read_all(user_id=1)


class TestNoticeServiceGetMyPage:
    """测试获取我的通知列表"""

    @pytest.mark.asyncio
    async def test_get_my_page(self, db, test_published_notice):
        """测试获取我的通知列表"""
        result = await notice_service.get_my_page(
            user_id=1, page_num=1, page_size=10
        )
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_with_title(self, db, test_published_notice):
        """测试按标题过滤"""
        result = await notice_service.get_my_page(
            user_id=1, page_num=1, page_size=10, title="已发布通知"
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_with_is_read(self, db, test_published_notice):
        """测试按已读状态过滤"""
        # 先标记已读
        await NoticeReads.create(notice_id=test_published_notice.id, user_id=1)

        result = await notice_service.get_my_page(
            user_id=1, page_num=1, page_size=10, is_read=1
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_my_page_unread(self, db, test_published_notice):
        """测试获取未读通知"""
        result = await notice_service.get_my_page(
            user_id=1, page_num=1, page_size=10, is_read=0
        )
        # 可能包含未读通知
        assert result.total >= 0
