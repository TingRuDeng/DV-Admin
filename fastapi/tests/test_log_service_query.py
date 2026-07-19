"""
日志服务分页查询测试。
"""
import uuid
import warnings
from datetime import datetime, timedelta

import pytest

from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Departments, OperationLog, Permissions, Roles
from app.services.system.log_service import log_service

pytest_plugins = ["log_service_fixtures"]


class TestLogServiceGetPage:
    """测试日志分页查询。"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_logs):
        """测试基本分页查询。"""
        result = await log_service.get_page(page=1, page_size=10)
        assert result.total >= 1
        assert len(result.list) >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_username(self, db, test_logs):
        """测试按用户名过滤。"""
        result = await log_service.get_page(page=1, page_size=10, username="test_user_0")
        assert result.total >= 1
        for log in result.list:
            assert "test_user_0" in log.username

    @pytest.mark.asyncio
    async def test_get_page_with_operation(self, db, test_logs):
        """测试按操作描述过滤。"""
        result = await log_service.get_page(page=1, page_size=10, operation="测试操作")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_method(self, db, test_logs):
        """测试按请求方法过滤。"""
        result = await log_service.get_page(page=1, page_size=10, method="GET")
        assert result.total >= 1
        for log in result.list:
            assert log.method == "GET"

    @pytest.mark.asyncio
    async def test_get_page_with_method_lowercase(self, db, test_logs):
        """测试请求方法小写转换。"""
        result = await log_service.get_page(page=1, page_size=10, method="get")
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_status(self, db, test_logs):
        """测试按状态过滤。"""
        result = await log_service.get_page(page=1, page_size=10, status=1)
        assert result.total >= 1
        for log in result.list:
            assert log.status == 1

    @pytest.mark.asyncio
    async def test_get_page_with_time_range(self, db, test_logs):
        """测试按时间范围过滤。"""
        now = datetime.now()
        with warnings.catch_warnings():
            warnings.filterwarnings("error", message=".*naive datetime.*")
            result = await log_service.get_page(
                page=1,
                page_size=10,
                start_time=now - timedelta(days=1),
                end_time=now + timedelta(days=1),
            )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果。"""
        result = await log_service.get_page(page=1, page_size=10, username="nonexistent_user_xyz")
        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_page_pagination(self, db):
        """测试分页功能。"""
        for i in range(15):
            await OperationLog.create(
                username=f"page_user_{i}_{uuid.uuid4().hex[:6]}",
                operation=f"分页操作{i}",
                method="GET",
                path=f"/api/page/{i}",
                status=1,
            )

        result1 = await log_service.get_page(page=1, page_size=10)
        assert len(result1.results) == 10

        result2 = await log_service.get_page(page=2, page_size=10)
        assert len(result2.results) >= 5

    @pytest.mark.asyncio
    async def test_get_page_filters_by_current_user_dept_scope(self, db):
        """部门数据范围只返回本部门用户产生的操作日志。"""
        visible_dept = await Departments.create(name="日志可见部门", status=1, sort=1)
        hidden_dept = await Departments.create(name="日志隐藏部门", status=1, sort=2)
        permission = await Permissions.create(name="system:logs:query", type="BUTTON", perm="system:logs:query")
        role = await Roles.create(
            name="日志数据范围角色",
            code="log_scope_role",
            status=1,
            data_scope=Roles.DATA_SCOPE_DEPT,
        )
        await role.permissions.add(permission)
        scoped_user = await Users.create(
            username="log_scoped_user",
            password="admin123",
            name="日志范围用户",
            dept_id=visible_dept.id,
            is_active=1,
        )
        await scoped_user.roles.add(role)
        visible_user = await Users.create(
            username="log_visible_user",
            password="admin123",
            name="日志可见用户",
            dept_id=visible_dept.id,
            is_active=1,
        )
        hidden_user = await Users.create(
            username="log_hidden_user",
            password="admin123",
            name="日志隐藏用户",
            dept_id=hidden_dept.id,
            is_active=1,
        )
        visible_log = await OperationLog.create(
            user_id=visible_user.id,
            username=visible_user.username,
            operation="可见操作",
            method="POST",
            path="/api/visible",
            status=1,
        )
        hidden_log = await OperationLog.create(
            user_id=hidden_user.id,
            username=hidden_user.username,
            operation="隐藏操作",
            method="POST",
            path="/api/hidden",
            status=1,
        )

        result = await log_service.get_page(page=1, page_size=20, current_user=scoped_user)

        operations = {log.operation for log in result.list}
        assert "可见操作" in operations
        assert "隐藏操作" not in operations
        detail = await log_service.get_detail(visible_log.id, current_user=scoped_user)
        assert detail.operation == "可见操作"
        with pytest.raises(NotFound):
            await log_service.get_detail(hidden_log.id, current_user=scoped_user)

    @pytest.mark.asyncio
    async def test_get_page_masks_sensitive_fields_without_plain_permission(self, db):
        """无字段原文权限时，日志请求体、响应体和 IP 应脱敏。"""
        permission = await Permissions.create(
            name="system:logs:query",
            type="BUTTON",
            perm="system:logs:query",
        )
        role = await Roles.create(name="日志字段脱敏角色", code="masked_log_role", status=1)
        await role.permissions.add(permission)
        current_user = await Users.create(
            username="masked_log_reader",
            password="admin123",
            name="日志脱敏读取者",
            is_active=1,
        )
        await current_user.roles.add(role)
        log = await OperationLog.create(
            username="operator",
            operation="敏感日志",
            method="POST",
            path="/api/sensitive",
            request_body='{"password":"secret","mobile":"13800138000"}',
            response_body='{"token":"secret-token","ok":true}',
            ip="192.168.1.20",
            status=1,
        )

        result = await log_service.get_page(
            page=1,
            page_size=20,
            operation="敏感日志",
            current_user=current_user,
        )

        item = result.list[0]
        assert item.request_body == "[已脱敏]"
        assert item.response_body == "[已脱敏]"
        assert item.ip == "192.168.1.*"
        detail = await log_service.get_detail(log.id, current_user=current_user)
        assert detail.request_body == "[已脱敏]"
        assert detail.response_body == "[已脱敏]"
        assert detail.ip == "192.168.1.*"

    @pytest.mark.asyncio
    async def test_get_page_keeps_sensitive_fields_with_plain_permission(self, db):
        """拥有字段原文权限时，日志敏感字段返回原文。"""
        query_permission = await Permissions.create(
            name="system:logs:query",
            type="BUTTON",
            perm="system:logs:query",
        )
        plain_permission = await Permissions.create(
            name="system:logs:field:plain",
            type="BUTTON",
            perm="system:logs:field:plain",
        )
        role = await Roles.create(name="日志字段原文角色", code="plain_log_role", status=1)
        await role.permissions.add(query_permission, plain_permission)
        current_user = await Users.create(
            username="plain_log_reader",
            password="admin123",
            name="日志原文读取者",
            is_active=1,
        )
        await current_user.roles.add(role)
        await OperationLog.create(
            username="operator",
            operation="原文字段日志",
            method="POST",
            path="/api/plain",
            request_body='{"password":"secret"}',
            response_body='{"token":"secret-token"}',
            ip="10.0.0.8",
            status=1,
        )

        result = await log_service.get_page(
            page=1,
            page_size=20,
            operation="原文字段日志",
            current_user=current_user,
        )

        item = result.list[0]
        assert item.request_body == '{"password":"secret"}'
        assert item.response_body == '{"token":"secret-token"}'
        assert item.ip == "10.0.0.8"
