"""角色与通知结果化批量删除及逐条重试测试。"""

import importlib
import uuid
from datetime import datetime

import pytest
from tortoise.transactions import in_transaction

from app.core.exceptions import NotFound, ValidationError
from app.db.models.oauth import Users
from app.db.models.system import Departments, Notices, Roles
from app.services.system import data_scope as data_scope_module
from app.services.system.notice_service import notice_service
from app.services.system.role_service import role_service

pytest_plugins = ["notice_service_fixtures"]


@pytest.mark.asyncio
async def test_role_batch_delete_reports_protected_items_and_deletes_other_items(db):
    protected = await Roles.create(
        name="超级管理员",
        code=f"admin_{uuid.uuid4().hex[:8]}",
        status=1,
    )
    target = await Roles.create(
        name=f"可删除角色_{uuid.uuid4().hex[:8]}",
        code=f"deletable_{uuid.uuid4().hex[:8]}",
        status=1,
    )

    result = await role_service.batch_delete([protected.id, target.id])

    assert result.status == "partial_failed"
    assert result.total_count == 2
    assert result.success_count == 1
    assert result.failed_count == 1
    assert result.success_items[0].object_id == str(target.id)
    assert result.failures[0].object_id == str(protected.id)
    assert result.failures[0].error_code == "PROTECTED_OBJECT"
    assert result.failures[0].retryable is False
    assert await Roles.filter(id=protected.id).exists()
    assert not await Roles.filter(id=target.id).exists()


@pytest.mark.asyncio
async def test_role_batch_delete_preflights_missing_ids(db):
    target = await Roles.create(
        name=f"预检角色_{uuid.uuid4().hex[:8]}",
        code=f"preflight_{uuid.uuid4().hex[:8]}",
        status=1,
    )

    with pytest.raises(NotFound):
        await role_service.batch_delete([target.id, 999999])

    assert await Roles.filter(id=target.id).exists()


@pytest.mark.asyncio
async def test_role_delete_stays_successful_when_cache_invalidation_raises(
    db,
    monkeypatch,
):
    """数据库删除已提交时，缓存失效异常不能伪装成删除失败。"""
    target = await Roles.create(
        name=f"缓存异常角色_{uuid.uuid4().hex[:8]}",
        code=f"cache_error_{uuid.uuid4().hex[:8]}",
        status=1,
    )

    async def fail_cache_invalidation(_role_id: int) -> None:
        raise RuntimeError("cache unavailable")

    monkeypatch.setattr(role_service, "_clear_role_cache", fail_cache_invalidation)

    result = await role_service.batch_delete([target.id])

    assert result.status == "succeeded"
    assert result.success_count == 1
    assert result.failed_count == 0
    assert not await Roles.filter(id=target.id).exists()


@pytest.mark.asyncio
async def test_role_batch_delete_rejects_invalid_ids(db):
    for ids in ([], [0], [-1], ["1"], [True]):
        with pytest.raises(ValidationError):
            await role_service.batch_delete(ids)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_notice_batch_delete_reports_published_failure_and_allows_retry(db):
    pending = await Notices.create(
        title=f"待删除通知_{uuid.uuid4().hex[:8]}",
        content="内容",
        publisher_id=1,
        publish_status=0,
    )
    published = await Notices.create(
        title=f"已发布通知_{uuid.uuid4().hex[:8]}",
        content="内容",
        publisher_id=1,
        publish_status=1,
        publish_time=datetime.now(),
    )
    revoked = await Notices.create(
        title=f"已撤回通知_{uuid.uuid4().hex[:8]}",
        content="内容",
        publisher_id=1,
        publish_status=-1,
    )

    result = await notice_service.delete_by_ids([pending.id, published.id, revoked.id])

    assert result.status == "partial_failed"
    assert result.total_count == 3
    assert result.success_count == 2
    assert result.failed_count == 1
    assert {item.object_id for item in result.success_items} == {
        str(pending.id),
        str(revoked.id),
    }
    assert result.failures[0].object_id == str(published.id)
    assert result.failures[0].error_code == "PUBLISHED_OBJECT"
    assert result.failures[0].retryable is True
    assert not await Notices.filter(id=pending.id).exists()
    assert not await Notices.filter(id=revoked.id).exists()
    assert await Notices.filter(id=published.id).exists()

    await Notices.filter(id=published.id).update(publish_status=-1)
    retry_result = await notice_service.retry_batch_delete([published.id])
    assert retry_result.status == "succeeded"
    assert retry_result.success_items[0].object_id == str(published.id)
    assert not await Notices.filter(id=published.id).exists()


@pytest.mark.asyncio
async def test_notice_batch_delete_rechecks_scope_before_locked_delete(db, monkeypatch):
    """预检后发布人变更到范围外时，最终锁定删除必须拒绝。"""
    visible_dept = await Departments.create(
        name=f"通知竞态可见部门_{uuid.uuid4().hex[:8]}",
        status=1,
        sort=1,
    )
    hidden_dept = await Departments.create(
        name=f"通知竞态隐藏部门_{uuid.uuid4().hex[:8]}",
        status=1,
        sort=2,
    )
    role = await Roles.create(
        name=f"通知竞态范围角色_{uuid.uuid4().hex[:8]}",
        code=f"notice_race_scope_{uuid.uuid4().hex[:8]}",
        status=1,
        data_scope=Roles.DATA_SCOPE_DEPT,
    )
    scoped_user = await Users.create(
        username=f"notice_race_scoped_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="通知竞态操作人",
        dept_id=visible_dept.id,
        is_active=1,
    )
    await scoped_user.roles.add(role)
    hidden_publisher = await Users.create(
        username=f"notice_race_hidden_{uuid.uuid4().hex[:8]}",
        password="admin123",
        name="通知竞态隐藏发布人",
        dept_id=hidden_dept.id,
        is_active=1,
    )
    notice = await Notices.create(
        title="通知竞态对象",
        content="内容",
        publisher_id=scoped_user.id,
        publisher_name=scoped_user.username,
        publish_status=0,
    )

    notice_module = importlib.import_module("app.services.system.notice_service")
    original_scope = notice_module.apply_notice_admin_data_scope
    scope_calls = 0

    async def scope_with_race(query, current_user):
        nonlocal scope_calls
        scope_calls += 1
        if scope_calls == 2:
            await Notices.filter(id=notice.id).update(publisher_id=hidden_publisher.id)
        return await original_scope(query, current_user)

    monkeypatch.setattr(notice_module, "apply_notice_admin_data_scope", scope_with_race)
    result = await notice_service.batch_delete([notice.id], current_user=scoped_user)

    assert result.status == "failed"
    assert result.failures[0].error_code == "NOT_FOUND"
    assert await Notices.filter(id=notice.id).exists()
    assert scope_calls == 2


@pytest.mark.asyncio
async def test_notice_batch_delete_preflights_missing_ids(db):
    pending = await Notices.create(
        title=f"通知预检_{uuid.uuid4().hex[:8]}",
        content="内容",
        publisher_id=1,
        publish_status=0,
    )

    with pytest.raises(NotFound):
        await notice_service.delete_by_ids([pending.id, 999999])

    assert await Notices.filter(id=pending.id).exists()


@pytest.mark.asyncio
async def test_notice_scope_resolution_uses_transaction_connection(db, monkeypatch):
    """通知删除事务内计算数据范围时必须使用同一数据库连接。"""
    seen_connections = []

    async def capture_visible_user_ids(_current_user, *, using_db=None):
        seen_connections.append(using_db)
        return None

    monkeypatch.setattr(data_scope_module, "get_visible_user_ids", capture_visible_user_ids)

    async with in_transaction() as connection:
        query = Notices.all().using_db(connection)
        await data_scope_module.apply_notice_admin_data_scope(query, None)

    assert seen_connections == [connection]


@pytest.mark.asyncio
async def test_role_delete_collects_affected_users_inside_transaction(db, monkeypatch):
    """角色删除清理缓存所需的用户集合必须从删除事务连接读取。"""
    target = await Roles.create(
        name=f"事务角色_{uuid.uuid4().hex[:8]}",
        code=f"transaction_{uuid.uuid4().hex[:8]}",
        status=1,
    )
    role_module = importlib.import_module("app.services.system.role_service")
    seen_connections = []

    async def capture_role_user_ids(_role_id: int, *, using_db=None):
        seen_connections.append(using_db)
        return []

    monkeypatch.setattr(role_module, "get_role_user_ids", capture_role_user_ids)

    result = await role_service.batch_delete([target.id])

    assert result.status == "succeeded"
    assert seen_connections and seen_connections[0] is not None
