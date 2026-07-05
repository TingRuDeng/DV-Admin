# -*- coding: utf-8 -*-
"""系统数据范围过滤服务。"""

from __future__ import annotations

from collections.abc import Iterable

from django.db.models import QuerySet

from drf_admin.apps.system.models import Departments, Roles, Users


def apply_user_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按当前用户角色数据范围过滤用户查询集。"""
    visible_user_ids = get_visible_user_ids(user)
    if visible_user_ids is None:
        return queryset
    return queryset.filter(id__in=visible_user_ids)


def apply_log_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按当前用户角色数据范围过滤操作日志查询集。"""
    visible_user_ids = get_visible_user_ids(user)
    if visible_user_ids is None:
        return queryset
    return queryset.filter(user_id__in=visible_user_ids)


def apply_notice_admin_data_scope(queryset: QuerySet, user: Users) -> QuerySet:
    """按发布人数据范围过滤后台通知管理查询集。"""
    visible_user_ids = get_visible_user_ids(user)
    if visible_user_ids is None:
        return queryset
    return queryset.filter(publisher_id__in=visible_user_ids)


def get_visible_user_ids(user: Users) -> set[int] | None:
    """计算当前用户可见的用户 ID；返回 None 表示无需过滤。"""
    if user.is_superuser:
        return None

    roles = list(user.roles.prefetch_related("data_depts").all())
    if any(role.data_scope == Roles.DATA_SCOPE_ALL for role in roles):
        return None

    dept_ids: set[int] = set()
    include_self = False
    for role in roles:
        if role.data_scope == Roles.DATA_SCOPE_SELF:
            include_self = True
        elif role.data_scope == Roles.DATA_SCOPE_DEPT:
            _add_current_dept(dept_ids, user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_DEPT_AND_CHILDREN:
            _add_current_dept_with_children(dept_ids, user.dept_id)
        elif role.data_scope == Roles.DATA_SCOPE_CUSTOM:
            dept_ids.update(role.data_depts.values_list("id", flat=True))

    visible_user_ids = set(_user_ids_in_depts(dept_ids))
    if include_self and user.id:
        visible_user_ids.add(user.id)
    return visible_user_ids


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


def _user_ids_in_depts(dept_ids: Iterable[int]) -> set[int]:
    """查询指定部门内的用户 ID。"""
    dept_id_set = set(dept_ids)
    if not dept_id_set:
        return set()
    return set(Users.objects.filter(dept_id__in=dept_id_set).values_list("id", flat=True))
