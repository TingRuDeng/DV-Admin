"""系统数据范围过滤服务。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar, cast

from tortoise.models import Model
from tortoise.queryset import QuerySet

from app.db.models.oauth import Users
from app.db.models.system import Departments, Roles

T = TypeVar("T", bound=Model)


async def apply_user_data_scope(query: QuerySet[T], current_user: Users | None) -> QuerySet[T]:
    """按当前用户角色数据范围过滤用户查询。"""
    visible_user_ids = await get_visible_user_ids(current_user)
    if visible_user_ids is None:
        return query
    return query.filter(id__in=list(visible_user_ids))


async def apply_log_data_scope(query: QuerySet[T], current_user: Users | None) -> QuerySet[T]:
    """按当前用户角色数据范围过滤操作日志查询。"""
    visible_user_ids = await get_visible_user_ids(current_user)
    if visible_user_ids is None:
        return query
    return query.filter(user_id__in=list(visible_user_ids))


async def get_visible_user_ids(current_user: Users | None) -> set[int] | None:
    """计算当前用户可见的用户 ID；返回 None 表示无需过滤。"""
    if current_user is None or current_user.is_superuser:
        return None

    await current_user.fetch_related("roles")
    roles = list(current_user.roles)
    for role in roles:
        await role.fetch_related("data_depts")
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None

    dept_ids: set[int] = set()
    include_self = False
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_SELF:
            include_self = True
        elif role.data_scope == Roles.DATA_SCOPE_DEPT:
            _add_current_dept(dept_ids, current_user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_DEPT_AND_CHILDREN:
            await _add_current_dept_with_children(dept_ids, current_user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_CUSTOM:
            dept_ids.update(dept.id for dept in role.data_depts)

    visible_user_ids = await _user_ids_in_depts(dept_ids)
    if include_self and current_user.id:
        visible_user_ids.add(current_user.id)
    return visible_user_ids


def _add_current_dept(dept_ids: set[int], dept_id: int | None) -> None:
    """将当前用户部门加入可见范围。"""
    if dept_id is not None:
        dept_ids.add(dept_id)


async def _add_current_dept_with_children(dept_ids: set[int], dept_id: int | None) -> None:
    """将当前用户部门及下级部门加入可见范围。"""
    if dept_id is None:
        return
    dept_ids.update(await _dept_with_descendant_ids(dept_id))


async def _dept_with_descendant_ids(root_id: int) -> set[int]:
    """迭代查询部门子树，避免递归深度受组织层级影响。"""
    collected = {root_id}
    frontier = {root_id}
    while frontier:
        child_id_list = cast(
            list[int],
            await Departments.filter(parent_id__in=list(frontier)).values_list("id", flat=True),
        )
        child_ids = set(child_id_list)
        frontier = child_ids - collected
        collected.update(child_ids)
    return collected


async def _user_ids_in_depts(dept_ids: Iterable[int]) -> set[int]:
    """查询指定部门内的用户 ID。"""
    dept_id_set = set(dept_ids)
    if not dept_id_set:
        return set()
    user_ids = cast(
        list[int],
        await Users.filter(dept_id__in=list(dept_id_set)).values_list("id", flat=True),
    )
    return set(user_ids)
