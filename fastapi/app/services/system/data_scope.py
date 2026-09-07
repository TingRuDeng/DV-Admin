"""系统数据范围过滤服务。"""

from __future__ import annotations

from typing import TypeVar, cast

from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.expressions import Q, Subquery
from tortoise.models import Model
from tortoise.queryset import QuerySet

from app.db.models.oauth import Users
from app.db.models.system import Departments, Roles

T = TypeVar("T", bound=Model)


async def apply_user_data_scope(
    query: QuerySet[T],
    current_user: Users | None,
    using_db: BaseDBAsyncClient | None = None,
) -> QuerySet[T]:
    """按当前用户角色数据范围过滤用户查询。"""
    scope = await _get_user_scope(
        current_user,
        using_db=using_db or getattr(query, "_db", None),
    )
    if scope is None:
        return query
    return query.filter(scope)


async def apply_log_data_scope(
    query: QuerySet[T],
    current_user: Users | None,
    using_db: BaseDBAsyncClient | None = None,
) -> QuerySet[T]:
    """按当前用户角色数据范围过滤操作日志查询。"""
    connection = using_db or getattr(query, "_db", None)
    scope = await _get_user_scope(current_user, using_db=connection)
    if scope is None:
        return query
    users = Users.filter(scope).using_db(connection).order_by().values("id")
    return query.filter(user_id__in=Subquery(users))


async def apply_notice_admin_data_scope(
    query: QuerySet[T],
    current_user: Users | None,
    using_db: BaseDBAsyncClient | None = None,
) -> QuerySet[T]:
    """按发布人数据范围过滤后台通知管理查询。"""
    connection = using_db or getattr(query, "_db", None)
    scope = await _get_user_scope(current_user, using_db=connection)
    if scope is None:
        return query
    users = Users.filter(scope).using_db(connection).order_by().values("id")
    return query.filter(publisher_id__in=Subquery(users))


async def _get_user_scope(
    current_user: Users | None,
    using_db: BaseDBAsyncClient | None = None,
) -> Q | None:
    """构造角色范围并集，用户集合留在数据库；None 表示不受限制。"""
    if current_user is None or current_user.is_superuser:
        return None

    await current_user.fetch_related("roles", using_db=using_db)
    roles = [role for role in current_user.roles if role.status == 1]
    for role in roles:
        await role.fetch_related("data_depts", using_db=using_db)
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None

    dept_ids = await _visible_department_ids(current_user, roles, using_db=using_db)
    include_self = False
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_SELF:
            include_self = True

    scope = Q(dept_id__in=list(dept_ids)) if dept_ids else Q(id__in=[])
    if include_self and current_user.id:
        scope |= Q(id=current_user.id)
    return scope


async def get_visible_department_ids(
    current_user: Users | None,
    using_db: BaseDBAsyncClient | None = None,
) -> set[int] | None:
    """计算当前用户可管理的部门 ID；返回 None 表示不受部门范围限制。"""
    if current_user is None or current_user.is_superuser:
        return None

    await current_user.fetch_related("roles", using_db=using_db)
    roles = [role for role in current_user.roles if role.status == 1]
    for role in roles:
        await role.fetch_related("data_depts", using_db=using_db)
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None
    return await _visible_department_ids(current_user, roles, using_db=using_db)


async def can_manage_user_department(
    current_user: Users | None,
    dept_id: int | None,
) -> bool:
    """判断操作者能否把用户放入目标部门。"""
    visible_department_ids = await get_visible_department_ids(current_user)
    if visible_department_ids is None:
        return True
    return dept_id is not None and dept_id in visible_department_ids


async def _visible_department_ids(
    current_user: Users,
    roles: list[Roles],
    using_db: BaseDBAsyncClient | None = None,
) -> set[int]:
    """按角色并集计算部门范围；SELF 不产生可创建用户的目标部门。"""
    dept_ids: set[int] = set()
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_DEPT:
            _add_current_dept(dept_ids, current_user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_DEPT_AND_CHILDREN:
            await _add_current_dept_with_children(
                dept_ids,
                current_user.dept_id,
                using_db=using_db,
            )
        elif role.data_scope == Roles.DATA_SCOPE_CUSTOM:
            dept_ids.update(dept.id for dept in role.data_depts)
    return dept_ids


def _add_current_dept(dept_ids: set[int], dept_id: int | None) -> None:
    """将当前用户部门加入可见范围。"""
    if dept_id is not None:
        dept_ids.add(dept_id)


async def _add_current_dept_with_children(
    dept_ids: set[int],
    dept_id: int | None,
    using_db: BaseDBAsyncClient | None = None,
) -> None:
    """将当前用户部门及下级部门加入可见范围。"""
    if dept_id is None:
        return
    dept_ids.update(await _dept_with_descendant_ids(dept_id, using_db=using_db))


async def _dept_with_descendant_ids(
    root_id: int,
    using_db: BaseDBAsyncClient | None = None,
) -> set[int]:
    """迭代查询部门子树，避免递归深度受组织层级影响。"""
    collected = {root_id}
    frontier = {root_id}
    while frontier:
        child_id_list = cast(
            list[int],
            await Departments.filter(parent_id__in=list(frontier))
            .using_db(using_db)
            .values_list("id", flat=True),
        )
        child_ids = set(child_id_list)
        frontier = child_ids - collected
        collected.update(child_ids)
    return collected
