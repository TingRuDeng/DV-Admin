"""Fresh, transaction-local authorization for delegated administrative writes."""
from dataclasses import replace
from typing import Any

from app.core.exceptions import NotFound, PermissionDenied, ValidationError
from app.core.grant_policy import GrantDenied, GrantPolicy, Role, Subject, protected
from app.db.models.oauth import Users
from app.db.models.system import Departments, Permissions, Roles


async def role_fact(role: Roles) -> Role:
    # Locking reads must include relations: RR snapshots can predate the actor lock.
    # Keep model queries here; Tortoise values_list() drops SELECT FOR UPDATE.
    permissions = await role.permissions.all().order_by("id").select_for_update().only("id")
    departments = await role.data_depts.all().order_by("id").select_for_update().only("id")
    return Role(
        role.id, frozenset(p.id for p in permissions), role.data_scope,
        frozenset(d.id for d in departments), role.name or "", role.code or "",
        bool(role.is_default), role.status == 1,
    )


async def subject_fact(user: Users) -> Subject:
    roles = await user.roles.all().order_by("id").select_for_update()
    return Subject(user.id, user.dept_id, tuple([await role_fact(r) for r in roles]), user.is_superuser)


class GrantBoundary:
    def __init__(self, actor: Users, policy: GrantPolicy):
        self.actor = actor
        self.policy = policy

    @classmethod
    async def load(cls, actor: Users | None, permission: str):
        # None is reserved for trusted internal jobs; every HTTP write passes its actor.
        if actor is None:
            return None
        fresh = await Users.filter(id=actor.id).select_for_update().first()
        if fresh is None or fresh.is_active != 1:
            raise PermissionDenied("操作者已失效")
        subject = await subject_fact(fresh)
        parents = dict(await Departments.all().values_list("id", "parent_id"))
        policy = GrantPolicy(subject, parents)
        if not fresh.is_superuser and not await Permissions.filter(
            id__in=policy.permissions, perm=permission,
        ).exists():
            raise PermissionDenied("缺少操作权限")
        return cls(fresh, policy)

    async def user(self, target: Users, roles: list[Roles] | None = None, *, dept_id=None, creating=False):
        if creating:
            old = Subject(None, target.dept_id, ())
        else:
            old = await subject_fact(target)
        new = replace(
            old,
            department=dept_id if dept_id is not None else target.dept_id,
            roles=tuple([await role_fact(role) for role in roles]) if roles is not None else old.roles,
        )
        try:
            if not creating:
                self.policy.check_user(old)
            self.policy.check_user(new, creating=creating)
        except GrantDenied as exc:
            raise PermissionDenied(str(exc)) from exc


async def check_role_write(actor: Users | None, permission: str, role_id: int | None, changes: dict[str, Any]) -> None:
    boundary = await GrantBoundary.load(actor, permission)
    role = await Roles.filter(id=role_id).select_for_update().first() if role_id else None
    if role_id and role is None:
        raise NotFound("角色不存在")
    old = await role_fact(role) if role else None
    base = old or Role(0, frozenset(), 1, frozenset())
    mapping = {"data_scope": "scope", "dept_ids": "departments", "permission_ids": "permissions", "is_default": "default", "status": "active"}
    values = {}
    for key, value in changes.items():
        if value is None or key not in {*mapping, "name", "code"}:
            continue
        if key in {"dept_ids", "permission_ids"}:
            model = Departments if key == "dept_ids" else Permissions
            if await model.filter(id__in=set(value)).count() != len(set(value)):
                raise ValidationError("部门或权限不存在")
            value = frozenset(value)
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
    holders = []
    if role:
        users = await Users.filter(roles__id=role.id).order_by("id").select_for_update()
        holders = [await subject_fact(user) for user in users]
    try:
        boundary.policy.check_role(old, new, tuple(holders))
    except GrantDenied as exc:
        raise PermissionDenied(str(exc)) from exc
