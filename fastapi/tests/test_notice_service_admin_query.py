"""
通知服务后台查询测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Departments, Notices, Permissions, Roles
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]

NOTICE_TARGET_PLAIN_PERMISSION = "system:notices:target:plain"
NOTICE_CONTENT_PLAIN_PERMISSION = "system:notices:content:plain"


async def create_scoped_notice_user() -> Users:
    """创建仅可管理本部门通知的测试用户。"""
    visible_dept = await Departments.create(name="通知可见部门", status=1, sort=1)
    hidden_dept = await Departments.create(name="通知隐藏部门", status=1, sort=2)
    permission = await Permissions.create(
        name="system:notices:query",
        type="BUTTON",
        perm="system:notices:query",
    )
    role = await Roles.create(
        name="通知数据范围角色",
        code="notice_scope_role",
        status=1,
        data_scope=Roles.DATA_SCOPE_DEPT,
    )
    await role.permissions.add(permission)
    scoped_user = await Users.create(
        username="notice_scoped_user",
        password="admin123",
        name="通知范围用户",
        dept_id=visible_dept.id,
        is_active=1,
    )
    await scoped_user.roles.add(role)
    visible_publisher = await Users.create(
        username="notice_visible_publisher",
        password="admin123",
        name="通知可见发布人",
        dept_id=visible_dept.id,
        is_active=1,
    )
    hidden_publisher = await Users.create(
        username="notice_hidden_publisher",
        password="admin123",
        name="通知隐藏发布人",
        dept_id=hidden_dept.id,
        is_active=1,
    )
    await Notices.create(
        title="可见部门通知",
        content="内容",
        target_type=1,
        publisher_id=visible_publisher.id,
        publisher_name=visible_publisher.username,
        publish_status=0,
    )
    await Notices.create(
        title="隐藏部门通知",
        content="内容",
        target_type=1,
        publisher_id=hidden_publisher.id,
        publisher_name=hidden_publisher.username,
        publish_status=0,
    )
    return scoped_user


async def create_notice_target_plain_operator(
    permission_codes: tuple[str, ...] = (),
) -> tuple[Users, Notices, Users]:
    """创建通知目标字段读取权限测试上下文。"""
    role = await Roles.create(
        name=f"通知目标字段读取角色_{uuid.uuid4().hex[:6]}",
        code=f"notice_target_plain_{uuid.uuid4().hex[:8]}",
        status=1,
    )
    for code in ("system:notices:query", *permission_codes):
        permission = await Permissions.create(name=code, type="BUTTON", perm=code)
        await role.permissions.add(permission)
    operator = await Users.create(
        username=f"notice_target_operator_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="通知目标字段读取操作人",
        is_active=1,
    )
    await operator.roles.add(role)
    target_user = await Users.create(
        username=f"notice_target_user_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="通知目标用户",
        is_active=1,
    )
    notice = await Notices.create(
        title=f"定向通知_{uuid.uuid4().hex[:6]}",
        content="内容",
        target_type=2,
        target_user_ids=[target_user.id],
        publisher_id=operator.id,
        publisher_name=operator.username,
        publish_status=0,
    )
    return operator, notice, target_user


class TestNoticeServiceGetPage:
    """测试通知分页查询。"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_notices_for_service):
        """测试基本分页查询。"""
        result = await notice_service.get_page(page_num=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_includes_target_users_and_update_time(self, db, test_notices_for_service):
        """后台分页输出必须包含目标用户和更新时间字段。"""
        notice = test_notices_for_service[0]
        result = await notice_service.get_page(page_num=1, page_size=10, title=notice.title)

        page_notice = next(item for item in result.list if item.id == notice.id)
        assert page_notice.target_user_ids == list(notice.target_user_ids or [])
        assert page_notice.update_time == notice.updated_at

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

    @pytest.mark.asyncio
    async def test_get_page_filters_notices_by_publisher_dept_scope(self, db):
        """部门数据范围只返回本部门用户发布的后台通知。"""
        scoped_user = await create_scoped_notice_user()

        result = await notice_service.get_page(
            page_num=1,
            page_size=20,
            current_user=scoped_user,
        )

        titles = {notice.title for notice in result.list}
        assert "可见部门通知" in titles
        assert "隐藏部门通知" not in titles

    @pytest.mark.asyncio
    async def test_get_page_masks_target_users_without_plain_permission(self, db):
        """无字段原文权限时，后台分页不暴露通知指定用户 ID。"""
        operator, notice, _target_user = await create_notice_target_plain_operator()

        result = await notice_service.get_page(
            page_num=1,
            page_size=20,
            title=notice.title,
            current_user=operator,
        )

        assert result.total == 1
        assert result.list[0].target_user_ids == []
        assert result.list[0].content == "[已脱敏]"

    @pytest.mark.asyncio
    async def test_get_page_keeps_target_users_with_plain_permission(self, db):
        """拥有字段原文权限时，后台分页返回通知指定用户 ID。"""
        operator, notice, target_user = await create_notice_target_plain_operator(
            (NOTICE_TARGET_PLAIN_PERMISSION,)
        )

        result = await notice_service.get_page(
            page_num=1,
            page_size=20,
            title=notice.title,
            current_user=operator,
        )

        assert result.total == 1
        assert result.list[0].target_user_ids == [target_user.id]

    @pytest.mark.asyncio
    async def test_get_page_keeps_content_with_plain_permission(self, db):
        """拥有正文原文权限时，后台分页返回通知正文。"""
        operator, notice, _target_user = await create_notice_target_plain_operator(
            (NOTICE_CONTENT_PLAIN_PERMISSION,)
        )

        result = await notice_service.get_page(
            page_num=1,
            page_size=20,
            title=notice.title,
            current_user=operator,
        )

        assert result.total == 1
        assert result.list[0].content == "内容"


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

    @pytest.mark.asyncio
    async def test_get_form_masks_target_users_without_plain_permission(self, db):
        """无字段原文权限时，表单查询不暴露通知指定用户 ID。"""
        operator, notice, _target_user = await create_notice_target_plain_operator()

        result = await notice_service.get_form(notice.id, current_user=operator)

        assert result.target_user_ids == []
        assert result.content == "[已脱敏]"

    @pytest.mark.asyncio
    async def test_get_form_keeps_target_users_with_plain_permission(self, db):
        """拥有字段原文权限时，表单查询返回通知指定用户 ID。"""
        operator, notice, target_user = await create_notice_target_plain_operator(
            (NOTICE_TARGET_PLAIN_PERMISSION,)
        )

        result = await notice_service.get_form(notice.id, current_user=operator)

        assert result.target_user_ids == [target_user.id]

    @pytest.mark.asyncio
    async def test_get_form_keeps_content_with_plain_permission(self, db):
        """拥有正文原文权限时，表单查询返回通知正文。"""
        operator, notice, _target_user = await create_notice_target_plain_operator(
            (NOTICE_CONTENT_PLAIN_PERMISSION,)
        )

        result = await notice_service.get_form(notice.id, current_user=operator)

        assert result.content == "内容"
