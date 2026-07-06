"""
通知服务写操作测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound, ValidationError
from app.db.models.oauth import Users
from app.db.models.system import Departments, Notices, Permissions, Roles
from app.schemas.system import NoticeCreate, NoticeUpdate
from app.services.system.notice_service import notice_service

pytest_plugins = ["notice_service_fixtures"]


class TestNoticeServiceCreate:
    """测试创建通知。"""

    async def create_operator(self, permission_codes: tuple[str, ...] = ()) -> Users:
        """创建通知字段权限测试操作人。"""
        role = await Roles.create(
            name=f"通知字段写入角色_{uuid.uuid4().hex[:8]}",
            code=f"notice_target_write_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        for code in permission_codes:
            permission = await Permissions.create(name=code, type="BUTTON", perm=code)
            await role.permissions.add(permission)
        operator = await Users.create(
            username=f"notice_operator_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="通知字段操作人",
            is_active=1,
        )
        await operator.roles.add(role)
        return operator

    @pytest.mark.asyncio
    async def test_create_basic(self, db):
        """测试基本创建。"""
        notice_in = NoticeCreate(
            title=f"新通知_{uuid.uuid4().hex[:6]}",
            content="新通知内容",
            type=0,
            level="L",
            target_type=1,
        )
        result = await notice_service.create(
            notice_in,
            publisher_id=1,
            publisher_name="管理员",
        )
        assert result.id is not None
        assert result.title == notice_in.title
        assert result.publish_status == 0

    @pytest.mark.asyncio
    async def test_create_with_target_users(self, db):
        """测试创建指定用户通知。"""
        notice_in = NoticeCreate(
            title=f"指定用户通知_{uuid.uuid4().hex[:6]}",
            content="指定用户通知内容",
            type=0,
            level="H",
            target_type=2,
            target_user_ids=[1, 2, 3],
        )
        result = await notice_service.create(
            notice_in,
            publisher_id=1,
            publisher_name="管理员",
        )
        assert result.target_type == 2

    @pytest.mark.asyncio
    async def test_create_target_users_validation(self, db):
        """测试创建指定用户通知验证。"""
        notice_in = NoticeCreate(
            title=f"测试通知_{uuid.uuid4().hex[:6]}",
            content="测试内容",
            type=0,
            level="L",
            target_type=2,
            target_user_ids=[],
        )
        with pytest.raises(ValidationError):
            await notice_service.create(
                notice_in,
                publisher_id=1,
                publisher_name="管理员",
            )

    @pytest.mark.asyncio
    async def test_create_rejects_target_users_without_field_write_permission(self, db):
        """无字段写入权限时，创建指定用户通知应被拒绝。"""
        operator = await self.create_operator()
        notice_in = NoticeCreate(
            title=f"无权限定向通知_{uuid.uuid4().hex[:6]}",
            content="指定用户通知内容",
            type=0,
            level="H",
            target_type=2,
            target_user_ids=[operator.id],
        )

        with pytest.raises(ValidationError) as exc_info:
            await notice_service.create(
                notice_in,
                publisher_id=operator.id,
                publisher_name=operator.name,
                current_user=operator,
            )

        assert "通知目标字段写入权限" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_allows_target_users_with_field_write_permission(self, db):
        """拥有字段写入权限时，创建指定用户通知应通过。"""
        operator = await self.create_operator(("system:notices:target:write",))
        notice_in = NoticeCreate(
            title=f"授权定向通知_{uuid.uuid4().hex[:6]}",
            content="指定用户通知内容",
            type=0,
            level="H",
            target_type=2,
            target_user_ids=[operator.id],
        )

        result = await notice_service.create(
            notice_in,
            publisher_id=operator.id,
            publisher_name=operator.name,
            current_user=operator,
        )

        assert result.target_user_ids == [operator.id]


class TestNoticeServiceUpdate:
    """测试更新通知。"""

    async def create_operator(self, permission_codes: tuple[str, ...] = ()) -> Users:
        """创建通知字段权限测试操作人。"""
        role = await Roles.create(
            name=f"通知字段写入角色_{uuid.uuid4().hex[:8]}",
            code=f"notice_target_write_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        for code in permission_codes:
            permission = await Permissions.create(name=code, type="BUTTON", perm=code)
            await role.permissions.add(permission)
        operator = await Users.create(
            username=f"notice_operator_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="通知字段操作人",
            is_active=1,
        )
        await operator.roles.add(role)
        return operator

    @pytest.mark.asyncio
    async def test_update_basic(self, db, test_notices_for_service):
        """测试基本更新。"""
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(title=f"更新标题_{uuid.uuid4().hex[:6]}")
        result = await notice_service.update(notice.id, notice_in)
        assert result.title == notice_in.title

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db):
        """测试更新不存在的通知。"""
        notice_in = NoticeUpdate(title="更新标题")
        with pytest.raises(NotFound):
            await notice_service.update(99999, notice_in)

    @pytest.mark.asyncio
    async def test_update_published_notice(self, db, test_published_notice):
        """测试更新已发布通知。"""
        notice_in = NoticeUpdate(title="更新标题")
        with pytest.raises(ValidationError):
            await notice_service.update(test_published_notice.id, notice_in)

    @pytest.mark.asyncio
    async def test_update_target_type(self, db, test_notices_for_service):
        """测试更新目标类型。"""
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(target_type=1)
        result = await notice_service.update(notice.id, notice_in)
        assert result.target_type == 1

    @pytest.mark.asyncio
    async def test_update_rejects_target_users_without_field_write_permission(
        self, db, test_notices_for_service
    ):
        """无字段写入权限时，更新指定用户通知应被拒绝。"""
        operator = await self.create_operator()
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(target_type=2, target_user_ids=[operator.id])

        with pytest.raises(ValidationError) as exc_info:
            await notice_service.update(notice.id, notice_in, current_user=operator)

        assert "通知目标字段写入权限" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_allows_target_users_with_field_write_permission(
        self, db, test_notices_for_service
    ):
        """拥有字段写入权限时，更新指定用户通知应通过。"""
        operator = await self.create_operator(("system:notices:target:write",))
        notice = test_notices_for_service[0]
        notice_in = NoticeUpdate(target_type=2, target_user_ids=[operator.id])

        result = await notice_service.update(notice.id, notice_in, current_user=operator)

        assert result.target_user_ids == [operator.id]


class TestNoticeServiceDelete:
    """测试删除通知。"""

    async def create_scoped_delete_context(self) -> tuple[Users, Notices]:
        """创建通知删除数据范围测试上下文。"""
        visible_dept = await Departments.create(
            name=f"通知删除可见部门_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=1,
        )
        hidden_dept = await Departments.create(
            name=f"通知删除隐藏部门_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=2,
        )
        permission = await Permissions.create(
            name="system:notices:delete",
            type="BUTTON",
            perm="system:notices:delete",
        )
        role = await Roles.create(
            name=f"通知删除数据范围角色_{uuid.uuid4().hex[:6]}",
            code=f"notice_delete_scope_{uuid.uuid4().hex[:8]}",
            status=1,
            data_scope=Roles.DATA_SCOPE_DEPT,
        )
        await role.permissions.add(permission)
        scoped_user = await Users.create(
            username=f"notice_delete_scoped_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="通知删除范围用户",
            dept_id=visible_dept.id,
            is_active=1,
        )
        await scoped_user.roles.add(role)
        hidden_publisher = await Users.create(
            username=f"notice_delete_hidden_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="通知删除隐藏发布人",
            dept_id=hidden_dept.id,
            is_active=1,
        )
        hidden_notice = await Notices.create(
            title=f"隐藏部门待删除通知_{uuid.uuid4().hex[:6]}",
            content="内容",
            target_type=1,
            publisher_id=hidden_publisher.id,
            publisher_name=hidden_publisher.username,
            publish_status=0,
        )
        return scoped_user, hidden_notice

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, db, test_notices_for_service):
        """测试批量删除。"""
        ids = [n.id for n in test_notices_for_service[:2]]
        await notice_service.delete_by_ids(ids)

        for nid in ids:
            exists = await Notices.filter(id=nid).exists()
            assert not exists

    @pytest.mark.asyncio
    async def test_delete_published_notice(self, db, test_published_notice):
        """测试删除已发布通知。"""
        with pytest.raises(ValidationError):
            await notice_service.delete_by_ids([test_published_notice.id])

    @pytest.mark.asyncio
    async def test_delete_rejects_notice_outside_publisher_dept_scope(self, db):
        """删除接口不能绕过通知发布人部门数据范围。"""
        scoped_user, hidden_notice = await self.create_scoped_delete_context()

        with pytest.raises(NotFound):
            await notice_service.delete_by_ids([hidden_notice.id], current_user=scoped_user)

        assert await Notices.filter(id=hidden_notice.id).exists()
