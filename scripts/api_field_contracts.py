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
        key="auth_info",
        canonical=frozenset(
            {"avatar", "deptName", "email", "gender", "id", "mobile", "name", "perms", "roleNames", "roles", "username"}
        ),
        fastapi_only=frozenset({"createdAt", "deptId", "isActive", "updatedAt"}),
        django_source="drf_admin.apps.system.models.Users.get_user_info",
        fastapi_source="app.schemas.oauth.UserInfo",
    ),
    FieldContract(
        key="auth_routes",
        canonical=frozenset({"children", "component", "meta", "name", "path", "redirect"}),
        django_source="drf_admin.apps.system.models.Users.get_menus",
        fastapi_source="app.db.models.oauth_user_access.build_menu_item",
    ),
    FieldContract(
        key="users_out",
        canonical=frozenset({"deptId", "deptName", "email", "id", "isActive", "mobile", "name", "roleNames", "roles", "username"}),
        django_only=frozenset({"dateJoined", "isSuperuser", "rolesList"}),
        fastapi_only=frozenset({"avatar", "createdAt", "gender", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.users.UsersSerializer",
        fastapi_source="app.schemas.system_user.UserOut",
    ),
    FieldContract(
        key="users_form_out",
        canonical=frozenset({"deptId", "deptName", "email", "id", "isActive", "mobile", "name", "roleNames", "roles", "username"}),
        django_only=frozenset({"dateJoined", "isSuperuser", "rolesList"}),
        fastapi_only=frozenset({"avatar", "createdAt", "gender", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.users.UsersSerializer",
        fastapi_source="app.schemas.system_user.UserFormOut",
    ),
    FieldContract(
        key="roles_out",
        canonical=frozenset({"code", "desc", "id", "isDefault", "name", "permissions", "sort", "status"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.roles.RolesSerializer",
        fastapi_source="app.schemas.system_role.RoleOut",
    ),
    FieldContract(
        key="roles_with_permissions",
        canonical=frozenset({"code", "desc", "id", "isDefault", "name", "permissions", "sort", "status"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.roles.RolesSerializer",
        fastapi_source="app.schemas.system_role.RoleWithPermissions",
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
                "parentId",
                "perm",
                "redirect",
                "routeName",
                "routePath",
                "sort",
                "type",
                "visible",
            }
        ),
        django_only=frozenset({"createTime", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        converge=frozenset({"createTime", "createdAt", "updateTime", "updatedAt"}),
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
                "children",
                "label",
                "parentId",
                "perm",
                "redirect",
                "routeName",
                "routePath",
                "sort",
                "type",
                "visible",
            }
        ),
        django_only=frozenset({"createTime", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
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
        canonical=frozenset({"dict", "dictName", "id", "label", "status", "tagType", "value"}),
        django_only=frozenset({"createTime", "updateTime"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.dicts.DictItemsSerializer",
        fastapi_source="app.schemas.system_dict.DictItemOut",
    ),
    FieldContract(
        key="depts_out",
        canonical=frozenset({"id", "name", "parentId", "sort", "status"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        converge=frozenset({"createdAt", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.departments.DepartmentsSerializer",
        fastapi_source="app.schemas.system_dept.DeptOut",
    ),
    FieldContract(
        key="depts_tree",
        canonical=frozenset({"children", "id", "label", "name", "parentId", "sort", "status"}),
        fastapi_only=frozenset({"createdAt", "updatedAt"}),
        django_source="drf_admin.apps.system.serializers.departments.DepartmentsTreeSerializer",
        fastapi_source="app.schemas.system_dept.DeptTree",
    ),
    FieldContract(
        key="notices_page",
        canonical=frozenset(
            {
                "content",
                "createTime",
                "id",
                "level",
                "publishStatus",
                "publishTime",
                "publisherId",
                "publisherName",
                "revokeTime",
                "targetType",
                "targetUserIds",
                "title",
                "type",
                "updateTime",
            }
        ),
        django_source="drf_admin.apps.system.serializers.notices.NoticesSerializer",
        fastapi_source="app.schemas.system_notice.NoticePageOut",
    ),
)

ENDPOINT_FIELD_CONTRACTS: dict[str, str] = {
    "auth_info": "auth_info",
    "auth_routes": "auth_routes",
    "users_page": "users_out",
    "users_form": "users_form_out",
    "users_create": "users_out",
    "users_update": "users_out",
    "roles_page": "roles_out",
    "roles_form": "roles_with_permissions",
    "roles_create": "roles_out",
    "roles_update": "roles_out",
    "menus_tree": "menus_tree",
    "menus_create": "menus_out",
    "menus_update": "menus_out",
    "depts_tree": "depts_tree",
    "depts_create": "depts_out",
    "depts_update": "depts_out",
    "dicts_page": "dicts_out",
    "dicts_create": "dicts_out",
    "dicts_update": "dicts_out",
    "dict_items_page": "dict_items_out",
    "dict_items_create": "dict_items_out",
    "dict_items_update": "dict_items_out",
    "notices_page": "notices_page",
    "notices_create": "notices_page",
    "notices_update": "notices_page",
}

FIELD_CONTRACT_EXEMPT_ENDPOINTS = frozenset({"auth_login", "files_upload", "logs_page"})


def iter_api_field_contracts() -> tuple[FieldContract, ...]:
    """返回不可变 API 字段契约目录。"""
    return API_FIELD_CONTRACTS


def iter_endpoint_field_contracts() -> tuple[tuple[str, str], ...]:
    """返回端点到字段契约的覆盖关系。"""
    return tuple(ENDPOINT_FIELD_CONTRACTS.items())


def iter_read_endpoint_field_contracts() -> tuple[tuple[str, str], ...]:
    """返回端点到字段契约的覆盖关系，保留旧入口兼容测试。"""
    return iter_endpoint_field_contracts()


def iter_field_contract_exempt_endpoints() -> frozenset[str]:
    """返回不适用双后端字段契约的端点。"""
    return FIELD_CONTRACT_EXEMPT_ENDPOINTS


def iter_field_contract_exempt_read_endpoints() -> frozenset[str]:
    """返回不适用双后端字段契约的端点，保留旧入口兼容测试。"""
    return iter_field_contract_exempt_endpoints()


def iter_api_field_converge_items() -> tuple[tuple[str, str], ...]:
    """返回所有待收敛字段，用于技术债看板和验证脚本展示。"""
    return tuple(
        (contract.key, field)
        for contract in API_FIELD_CONTRACTS
        for field in sorted(contract.converge)
    )


def assert_api_field_contract_catalog() -> None:
    """校验字段契约目录自身一致性，避免无效清单进入门禁。"""
    keys = {contract.key for contract in API_FIELD_CONTRACTS}
    assert len(keys) == len(API_FIELD_CONTRACTS)
    for contract in API_FIELD_CONTRACTS:
        _assert_field_contract(contract)
    for field_contract_key in ENDPOINT_FIELD_CONTRACTS.values():
        assert field_contract_key in keys


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
