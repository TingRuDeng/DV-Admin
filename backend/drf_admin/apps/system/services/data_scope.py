# -*- coding: utf-8 -*-
"""系统数据范围过滤服务。"""

from __future__ import annotations

from django.db.models import Q, QuerySet, Subquery

from drf_admin.apps.system.models import Departments, Roles, Users


def apply_user_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按当前用户角色数据范围过滤用户查询集。"""
    scope = _get_user_scope(user)
    if scope is None:
        return queryset
    return queryset.filter(scope)


def apply_log_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按当前用户角色数据范围过滤操作日志查询集。"""
    scope = _get_user_scope(user)
    if scope is None:
        return queryset
    users = Users.objects.filter(scope).order_by().values("id")
    return queryset.filter(user_id__in=Subquery(users))


def apply_notice_admin_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按发布人数据范围过滤后台通知管理查询集。"""
    scope = _get_user_scope(user)
    if scope is None:
        return queryset
    users = Users.objects.filter(scope).order_by().values("id")
    return queryset.filter(publisher_id__in=Subquery(users))


def _get_user_scope(user: Users) -> Q | None:
    """构造角色范围并集，用户集合留在数据库；None 表示不受限制。"""
    if user.is_superuser:
        return None

    roles = list(user.roles.filter(status=1).prefetch_related("data_depts"))
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None

    dept_ids = _visible_department_ids(user, roles)
    include_self = False
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_SELF:
            include_self = True

    scope = Q(dept_id__in=dept_ids) if dept_ids else Q(id__in=[])
    if include_self and user.id:
        scope |= Q(id=user.id)
    return scope


def get_visible_department_ids(user: Users) -> set[int] | None:
    """计算当前用户可管理的部门 ID；返回 None 表示不受部门范围限制。"""
    if user.is_superuser:
        return None
    roles = list(user.roles.filter(status=1).prefetch_related("data_depts"))
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None
    return _visible_department_ids(user, roles)


def can_manage_user_department(user: Users, dept_id: int | None) -> bool:
    """判断操作者能否把用户放入目标部门。"""
    visible_department_ids = get_visible_department_ids(user)
    if visible_department_ids is None:
        return True
    return dept_id is not None and dept_id in visible_department_ids


def _visible_department_ids(user: Users, roles: list[Roles]) -> set[int]:
    """按角色并集计算部门范围；SELF 不产生可创建用户的目标部门。"""
    dept_ids: set[int] = set()
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_DEPT:
            _add_current_dept(dept_ids, user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_DEPT_AND_CHILDREN:
            _add_current_dept_with_children(dept_ids, user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_CUSTOM:
            dept_ids.update(dept.id for dept in role.data_depts.all())
    return dept_ids


def _add_current_dept(dept_ids: set[int], dept_id: int | None) -> None:
    """将当前用户部门加入可见范围。"""
    if dept_id is not None:
        dept_ids.add(dept_id)


def _add_current_dept_with_children(dept_ids: set[int], dept_id: int | None) -> None:
    """将当前用户部门及下级部门加入可见范围。"""
    if dept_id is None:
        return
    dept_ids.update(_dept_with_descendant_ids(dept_id))


def _dept_with_descendant_ids(root_id: int) -> set[int]:
    """迭代查询部门子树，避免递归深度受组织层级影响。"""
    collected = {root_id}
    frontier = {root_id}
    while frontier:
        child_ids = set(Departments.objects.filter(parent_id__in=frontier).values_list("id", flat=True))
        frontier = child_ids - collected
        collected.update(child_ids)
    return collected
