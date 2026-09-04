"""批量删除逐条结果与重试契约测试。"""

import uuid

import pytest

from app.core.exceptions import NotFound, ValidationError
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]


@pytest.mark.asyncio
async def test_user_batch_delete_returns_item_failures_without_blocking_other_items(
    db,
    test_user_for_service,
):
    """当前登录用户失败时，其他用户仍应成功删除并返回逐条结果。"""
    target = await Users.create(
        username=f"batch_target_{uuid.uuid4().hex[:8]}",
        password=get_password_hash("test123"),
        name="可删除用户",
        is_active=1,
        dept_id=test_user_for_service.dept_id,
    )
    test_user_for_service.is_superuser = True

    result = await user_service.batch_delete(
        [test_user_for_service.id, target.id],
        current_user=test_user_for_service,
    )

    assert result.status == "partial_failed"
    assert result.total_count == 2
    assert result.success_count == 1
    assert result.failed_count == 1
    assert result.processed_count == 2
    assert [item.object_id for item in result.success_items] == [str(target.id)]
    assert result.failures[0].object_id == str(test_user_for_service.id)
    assert result.failures[0].error_code == "PROTECTED_OBJECT"
    assert result.failures[0].retryable is False
    assert result.failures[0].object_name == "测试用户"
    assert await Users.filter(id=target.id).exists() is False
    assert await Users.filter(id=test_user_for_service.id).exists() is True


@pytest.mark.asyncio
async def test_user_batch_delete_deduplicates_ids_and_returns_success_item(
    db,
    test_dept_for_service,
):
    """重复 ID 只处理一次，并保留结果对象名称。"""
    target = await Users.create(
        username=f"batch_duplicate_{uuid.uuid4().hex[:8]}",
        password=get_password_hash("test123"),
        name="重复目标",
        is_active=1,
        dept_id=test_dept_for_service.id,
    )

    result = await user_service.batch_delete([target.id, target.id])

    assert result.status == "succeeded"
    assert result.total_count == 1
    assert result.processed_count == 1
    assert result.success_items[0].object_id == str(target.id)
    assert result.success_items[0].object_name == "重复目标"


@pytest.mark.asyncio
async def test_user_delete_stays_successful_when_cache_invalidation_raises(
    db,
    test_dept_for_service,
    monkeypatch,
):
    """数据库删除已提交时，缓存失效异常不能伪装成删除失败。"""
    target = await Users.create(
        username=f"cache_error_{uuid.uuid4().hex[:8]}",
        password=get_password_hash("test123"),
        name="缓存异常用户",
        is_active=1,
        dept_id=test_dept_for_service.id,
    )

    async def fail_cache_invalidation(_user_id: int) -> None:
        raise RuntimeError("cache unavailable")

    monkeypatch.setattr(user_service, "_clear_user_cache", fail_cache_invalidation)

    result = await user_service.batch_delete([target.id])

    assert result.status == "succeeded"
    assert result.success_count == 1
    assert result.failed_count == 0
    assert await Users.filter(id=target.id).exists() is False


@pytest.mark.asyncio
async def test_user_batch_delete_preflights_scope_before_deleting_anything(
    db,
    scoped_user_context,
):
    """范围外目标会让初次请求整批拒绝，范围内目标不能被部分删除。"""
    visible_user = scoped_user_context["visible_user"]
    hidden_user = scoped_user_context["hidden_user"]

    with pytest.raises(NotFound):
        await user_service.batch_delete(
            [visible_user.id, hidden_user.id],
            current_user=scoped_user_context["operator"],
        )

    assert await Users.filter(id=visible_user.id).exists()
    assert await Users.filter(id=hidden_user.id).exists()


@pytest.mark.asyncio
async def test_user_batch_delete_rejects_empty_or_non_positive_ids(db):
    """批量删除必须拒绝空列表和非正整数 ID。"""
    for ids in ([], [0], [-1], ["1"], [True]):
        with pytest.raises(ValidationError):
            await user_service.batch_delete(ids)  # type: ignore[arg-type]
