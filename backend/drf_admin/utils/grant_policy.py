"""Pure delegation rules; keep both backend copies byte-identical."""
from dataclasses import dataclass, replace

PROTECTED_IDENTIFIERS = frozenset(
    {"root", "admin", "superadmin", "administrator", "超级管理员", "系统管理员"}
)


class GrantDenied(ValueError):
    """The requested authority exceeds the actor's current authority."""


@dataclass(frozen=True)
class Role:
    id: int
    permissions: frozenset[int]
    scope: int
    departments: frozenset[int]
    name: str = ""
    code: str = ""
    default: bool = False
    active: bool = True


@dataclass(frozen=True)
class Subject:
    id: int | None
    department: int | None
    roles: tuple[Role, ...]
    superuser: bool = False


@dataclass(frozen=True)
class Domain:
    all: bool = False
    departments: frozenset[int] = frozenset()
    self_only: bool = False

    def contains(self, actor: Subject, target: Subject) -> bool:
        return (
            self.all
            or target.department in self.departments
            or (self.self_only and actor.id is not None and actor.id == target.id)
        )


def protected(role: Role) -> bool:
    return any(
        value.strip().casefold() in PROTECTED_IDENTIFIERS
        for value in (role.name, role.code)
    )


class GrantPolicy:
    def __init__(self, actor: Subject, parents: dict[int, int | None]):
        self.actor = actor
        self.parents = parents
        self.permissions = self.permission_union(
            tuple(role for role in actor.roles if role.active)
        )
        self.domain = self.domain_for(actor, active_only=True)

    @staticmethod
    def permission_union(roles: tuple[Role, ...]) -> frozenset[int]:
        return frozenset(permission for role in roles for permission in role.permissions)

    def domain_for(self, user: Subject, *, active_only: bool = False) -> Domain:
        departments: set[int] = set()
        include_self = False
        for role in user.roles:
            if active_only and not role.active:
                continue
            if role.scope == 1:
                return Domain(all=True)
            if role.scope == 2:
                include_self = True
            elif role.scope == 3 and user.department is not None:
                departments.add(user.department)
            elif role.scope == 4 and user.department is not None:
                descendants = {user.department}
                while True:
                    children = {
                        child for child, parent in self.parents.items()
                        if parent in descendants
                    }
                    expanded = descendants | children
                    if expanded == descendants:
                        break
                    descendants = expanded
                departments.update(descendants)
            elif role.scope == 5:
                departments.update(role.departments)
            elif role.scope not in {2, 3, 4}:
                raise GrantDenied("角色数据范围无效")
        return Domain(departments=frozenset(departments), self_only=include_self)

    def check_user(self, target: Subject, *, creating: bool = False) -> None:
        if self.actor.superuser:
            return
        if target.superuser or not self.domain.contains(self.actor, target):
            raise GrantDenied("目标用户超出可管理范围")
        if any(role.code.strip().casefold() == "root" for role in target.roles):
            raise GrantDenied("不能授予超级管理员身份标识")
        if not self.permission_union(target.roles) <= self.permissions:
            raise GrantDenied("不能管理或授予操作者未拥有的权限")
        granted = self.domain_for(target)
        if self.domain.all:
            return
        if granted.all or not granted.departments <= self.domain.departments:
            raise GrantDenied("角色数据范围超出操作者范围")
        if granted.self_only and not self.domain.contains(self.actor, target):
            raise GrantDenied("角色自身数据范围超出操作者范围")
        if creating and target.department not in self.domain.departments:
            raise GrantDenied("目标部门超出操作者范围")

    def check_role(
        self, old: Role | None, new: Role, holders: tuple[Subject, ...]
    ) -> None:
        if self.actor.superuser:
            return
        if new.default or (old is not None and old.default):
            raise GrantDenied("全局默认角色必须由超级管理员管理")
        for role in (old, new):
            if role is not None and (
                protected(role) or not role.permissions <= self.permissions
            ):
                raise GrantDenied("角色权限超出操作者范围")
        if not holders:
            for role in (old, new):
                if role is not None:
                    self.check_user(replace(self.actor, roles=(role,)))
        for holder in holders:
            self.check_user(holder)
            roles = tuple(new if role.id == new.id else role for role in holder.roles)
            self.check_user(replace(holder, roles=roles))
