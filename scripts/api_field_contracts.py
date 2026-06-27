from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldContract:
    """描述一个对外响应对象的字段集合契约。"""

    key: str
    canonical: frozenset[str]
    django_only: frozenset[str] = frozenset()
    fastapi_only: frozenset[str] = frozenset()
    converge: frozenset[str] = frozenset()
    django_source: str = ""
    fastapi_source: str = ""


API_FIELD_CONTRACTS: tuple[FieldContract, ...] = (
    FieldContract(
        key="users_out",
        canonical=frozenset({"deptId", "deptName", "email", "id", "isActive", "mobile", "name", "username"}),
        django_only=frozenset({"dateJoined", "isSuperuser", "roles", "rolesList"}),
        fastapi_only=frozenset({"avatar", "createdAt", "gender", "roleNames", "updatedAt"}),
        converge=frozenset({"roleNames", "roles", "rolesList"}),
        django_source="drf_admin.apps.system.serializers.users.UsersSerializer",
        fastapi_source="app.schemas.system_user.UserOut",
    ),
    FieldContract(
        key="users_form_out",
        canonical=frozenset({"deptId", "deptName", "email", "id", "isActive", "mobile", "name", "roles", "username"}),
        django_only=frozenset({"dateJoined", "isSuperuser", "rolesList"}),
        fastapi_only=frozenset({"avatar", "createdAt", "gender", "roleNames", "updatedAt"}),
        converge=frozenset({"roleNames", "rolesList"}),
        django_source="drf_admin.apps.system.serializers.users.UsersSerializer",
        fastapi_source="app.schemas.system_user.UserFormOut",
    ),
    FieldContract(
        key="roles_out",
        canonical=frozenset({"code", "desc", "id", "isDefault", "name", "sort", "status"}),
        django_only=frozenset({"permissions"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        converge=frozenset({"permissions"}),
        django_source="drf_admin.apps.system.serializers.roles.RolesSerializer",
        fastapi_source="app.schemas.system_role.RoleOut",
    ),
    FieldContract(
        key="menus_out",
        canonical=frozenset(
            {
                "alwaysShow",
                "component",
                "desc",
                "icon",
                "id",
                "keepAlive",
                "name",
                "params",
                "perm",
                "redirect",
                "routeName",
                "routePath",
                "sort",
                "type",
                "visible",
            }
        ),
        django_only=frozenset({"createTime", "parent", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "parentId", "updatedAt"}),
        converge=frozenset({"createTime", "createdAt", "parent", "parentId", "updateTime", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.permissions.MenusSerializer",
        fastapi_source="app.schemas.system_menu.MenuOut",
    ),
    FieldContract(
        key="menus_tree",
        canonical=frozenset(
            {
                "alwaysShow",
                "component",
                "desc",
                "icon",
                "id",
                "keepAlive",
                "name",
                "params",
                "perm",
                "redirect",
                "routeName",
                "routePath",
                "sort",
                "type",
                "visible",
            }
        ),
        django_only=frozenset({"createTime", "label", "parent", "updateTime"}),
        fastapi_only=frozenset({"children", "createdAt", "parentId", "updatedAt"}),
        converge=frozenset({"children", "label", "parent", "parentId"}),
        django_source="drf_admin.apps.system.serializers.permissions.MenusTreeSerializer",
        fastapi_source="app.schemas.system_menu.MenuTree",
    ),
    FieldContract(
        key="dicts_out",
        canonical=frozenset({"dictCode", "id", "name", "remark", "status"}),
        django_only=frozenset({"createTime", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        converge=frozenset({"createTime", "createdAt", "updateTime", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.dicts.DictsSerializer",
        fastapi_source="app.schemas.system_dict.DictDataOut",
    ),
    FieldContract(
        key="dict_items_out",
        canonical=frozenset({"dict", "id", "label", "status", "value"}),
        django_only=frozenset({"createTime", "dictName", "tagType", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        converge=frozenset({"tagType"}),
        django_source="drf_admin.apps.system.serializers.dicts.DictItemsSerializer",
        fastapi_source="app.schemas.system_dict.DictItemOut",
    ),
    FieldContract(
        key="depts_tree",
        canonical=frozenset({"id", "label", "name", "parentId", "sort", "status"}),
        django_only=frozenset({"parentName"}),
        fastapi_only=frozenset({"children", "createdAt", "updatedAt"}),
        converge=frozenset({"children", "parentName"}),
        django_source="drf_admin.apps.system.serializers.departments.DepartmentsTreeSerializer",
        fastapi_source="app.schemas.system_dept.DeptTree",
    ),
)


def iter_api_field_contracts() -> tuple[FieldContract, ...]:
    """返回不可变 API 字段契约目录。"""
    return API_FIELD_CONTRACTS


def assert_api_field_contract_catalog() -> None:
    """校验字段契约目录自身一致性，避免无效清单进入门禁。"""
    keys = {contract.key for contract in API_FIELD_CONTRACTS}
    assert len(keys) == len(API_FIELD_CONTRACTS)
    for contract in API_FIELD_CONTRACTS:
        _assert_field_contract(contract)


def _assert_field_contract(contract: FieldContract) -> None:
    """校验单个字段契约的基础结构。"""
    assert contract.key
    assert contract.canonical
    assert contract.django_source
    assert contract.fastapi_source
    assert contract.canonical.isdisjoint(contract.django_only)
    assert contract.canonical.isdisjoint(contract.fastapi_only)
    assert contract.django_only.isdisjoint(contract.fastapi_only)
    allowed_drift = contract.django_only | contract.fastapi_only
    assert contract.converge <= allowed_drift
