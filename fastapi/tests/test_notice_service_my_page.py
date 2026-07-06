"""
通知服务我的通知列表测试。
"""
import uuid

import pytest

from app.db.models.oauth import Users
from app.db.models.system import NoticeReads, Notices, Permissions, Roles
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]

NOTICE_TARGET_PLAIN_PERMISSION = "system:notices:target:plain"


async def create_my_notice_target_context(
    permission_codes: tuple[str, ...] = (),
) -> tuple[Users, Notices, Users]:
    """创建我的通知目标字段读取测试上下文。"""
    role = await Roles.create(
        name=f"我的通知目标读取角色_{uuid.uuid4().hex[:6]}",
        code=f"my_notice_target_plain_{uuid.uuid4().hex[:8]}",
        status=1,
    )
    for code in ("system:notices:query", *permission_codes):
        permission = await Permissions.create(name=code, type="BUTTON", perm=code)
        await role.permissions.add(permission)
    current_user = await Users.create(
        username=f"my_notice_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="我的通知用户",
        is_active=1,
    )
    await current_user.roles.add(role)
    publisher = await Users.create(
        username=f"my_notice_publisher_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="我的通知发布人",
        is_active=1,
    )
    notice = await Notices.create(
        title=f"我的定向通知_{uuid.uuid4().hex[:6]}",
        content="内容",
        target_type=2,
        target_user_ids=[current_user.id],
        publisher_id=publisher.id,
        publisher_name=publisher.username,
        publish_status=1,
    )
    return current_user, notice, publisher


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

    @pytest.mark.asyncio
    async def test_get_my_page_masks_target_users_without_plain_permission(self, db):
        """无字段原文权限时，我的通知不暴露指定用户 ID。"""
        current_user, notice, _publisher = await create_my_notice_target_context()

        result = await notice_service.get_my_page(
            user_id=current_user.id,
            page_num=1,
            page_size=20,
            title=notice.title,
            current_user=current_user,
        )

        assert result.total == 1
        assert result.list[0].target_user_ids == []

    @pytest.mark.asyncio
    async def test_get_my_page_keeps_target_users_with_plain_permission(self, db):
        """拥有字段原文权限时，我的通知返回指定用户 ID。"""
        current_user, notice, _publisher = await create_my_notice_target_context(
            (NOTICE_TARGET_PLAIN_PERMISSION,)
        )

        result = await notice_service.get_my_page(
            user_id=current_user.id,
            page_num=1,
            page_size=20,
            title=notice.title,
            current_user=current_user,
        )

        assert result.total == 1
        assert result.list[0].target_user_ids == [current_user.id]
