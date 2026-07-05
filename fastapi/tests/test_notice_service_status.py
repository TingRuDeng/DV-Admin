"""
通知服务发布状态测试。
"""
import pytest

from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Departments, NoticeReads, Notices, Permissions, Roles
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


async def create_scoped_notice_publish_context() -> tuple[Users, Notices]:
    """创建通知发布数据范围测试上下文。"""
    visible_dept = await Departments.create(name="通知发布可见部门", status=1, sort=1)
    hidden_dept = await Departments.create(name="通知发布隐藏部门", status=1, sort=2)
    permission = await Permissions.create(
        name="system:notices:publish",
        type="BUTTON",
        perm="system:notices:publish",
    )
    role = await Roles.create(
        name="通知发布数据范围角色",
        code="notice_publish_scope_role",
        status=1,
        data_scope=Roles.DATA_SCOPE_DEPT,
    )
    await role.permissions.add(permission)
    scoped_user = await Users.create(
        username="notice_publish_scoped_user",
        password="admin123",
        name="通知发布范围用户",
        dept_id=visible_dept.id,
        is_active=1,
    )
    await scoped_user.roles.add(role)
    hidden_publisher = await Users.create(
        username="notice_publish_hidden_publisher",
        password="admin123",
        name="通知发布隐藏人",
        dept_id=hidden_dept.id,
        is_active=1,
    )
    hidden_notice = await Notices.create(
        title="隐藏部门待发布通知",
        content="内容",
        target_type=1,
        publisher_id=hidden_publisher.id,
        publisher_name=hidden_publisher.username,
        publish_status=0,
    )
    return scoped_user, hidden_notice


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

    @pytest.mark.asyncio
    async def test_publish_rejects_notice_outside_publisher_dept_scope(self, db):
        """发布接口不能绕过通知发布人部门数据范围。"""
        scoped_user, hidden_notice = await create_scoped_notice_publish_context()

        with pytest.raises(NotFound):
            await notice_service.publish(hidden_notice.id, current_user=scoped_user)


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
