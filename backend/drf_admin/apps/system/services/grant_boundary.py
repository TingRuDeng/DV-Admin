"""Fresh database authorization inside the caller's atomic write transaction."""
from dataclasses import replace

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from drf_admin.apps.system.models import Departments, Permissions, Roles, Users
from drf_admin.utils.grant_policy import GrantDenied, GrantPolicy, Role, Subject, protected

_UNSET = object()


def role_fact(role):
    return Role(
        role.id, frozenset(role.permissions.values_list("id", flat=True)), role.data_scope,
        frozenset(role.data_depts.values_list("id", flat=True)), role.name or "", role.code or "",
        bool(role.is_default), role.status == 1,
    )


def subject_fact(user):
    role_ids = list(user.roles.values_list("id", flat=True))
    roles = Roles.objects.filter(id__in=role_ids).order_by("id").select_for_update()
    return Subject(user.id, user.dept_id, tuple(role_fact(r) for r in roles), user.is_superuser)


class GrantBoundary:
    def __init__(self, actor, policy):
        self.actor = actor
        self.policy = policy

    @classmethod
    def load(cls, actor, permission):
        if actor is None:
            return None  # Trusted internal jobs only; HTTP callers always supply an actor.
        fresh = Users.objects.filter(id=actor.id).select_for_update().first()
        if fresh is None or fresh.is_active != 1:
            raise PermissionDenied("操作者已失效")
        policy = GrantPolicy(subject_fact(fresh), dict(Departments.objects.values_list("id", "parent_id")))
        if not fresh.is_superuser and not Permissions.objects.filter(id__in=policy.permissions, perm=permission).exists():
            raise PermissionDenied("缺少操作权限")
        return cls(fresh, policy)

    def user(self, target, roles=None, *, dept_id=_UNSET, creating=False):
        old = Subject(None, target.dept_id, ()) if creating else subject_fact(target)
        new = replace(
            old, department=target.dept_id if dept_id is _UNSET else dept_id,
            roles=tuple(role_fact(role) for role in roles) if roles is not None else old.roles,
        )
        try:
            if not creating:
                self.policy.check_user(old)
            self.policy.check_user(new, creating=creating)
        except GrantDenied as exc:
            raise PermissionDenied(str(exc)) from exc


def check_role_write(actor, permission, role_id, changes):
    boundary = GrantBoundary.load(actor, permission)
    role = Roles.objects.filter(id=role_id).select_for_update().first() if role_id else None
    if role_id and role is None:
        raise NotFound("角色不存在")
    old = role_fact(role) if role else None
    base = old or Role(0, frozenset(), 1, frozenset())
    mapping = {"data_scope": "scope", "data_depts": "departments", "permissions": "permissions", "is_default": "default", "status": "active"}
    values = {}
    for key, value in changes.items():
        if value is None or key not in {*mapping, "name", "code"}:
            continue
        if key in {"data_depts", "permissions"}:
            ids = frozenset(item.id if hasattr(item, "id") else item for item in value)
            model = Departments if key == "data_depts" else Permissions
            if model.objects.filter(id__in=ids).count() != len(ids):
                raise ValidationError("部门或权限不存在")
            value = ids
        if key in {"status", "is_default"}:
            if value not in {0, 1}:
                raise ValidationError("角色状态无效")
            value = bool(value)
        values[mapping.get(key, key)] = value
    new = replace(base, **values)
    if new.scope not in {1, 2, 3, 4, 5}:
        raise ValidationError("角色数据范围无效")
    if old and protected(old) and not protected(new):
        raise ValidationError("不能移除系统角色保护标识")
    if boundary is None:
        return
    holders = tuple(subject_fact(user) for user in Users.objects.filter(roles=role).order_by("id").select_for_update()) if role else ()
    try:
        boundary.policy.check_role(old, new, holders)
    except GrantDenied as exc:
        raise PermissionDenied(str(exc)) from exc
