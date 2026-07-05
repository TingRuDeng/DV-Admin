from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontendFieldContract:
    """描述前端 API 类型文件必须显式声明的字段契约。"""

    key: str
    frontend_source: str
    required_fields: frozenset[str]
    tracked_backend_contract: str


API_FRONTEND_FIELD_CONTRACTS: tuple[FrontendFieldContract, ...] = (
    FrontendFieldContract(
        key="auth_info_type",
        frontend_source="frontend/src/api/auth-api.ts",
        required_fields=frozenset(
            {
                "avatar",
                "deptName",
                "email",
                "gender",
                "id",
                "mobile",
                "name",
                "perms",
                "roleNames",
                "roles",
                "username",
            }
        ),
        tracked_backend_contract="auth_info",
    ),
    FrontendFieldContract(
        key="auth_routes_type",
        frontend_source="frontend/src/api/auth-api.ts",
        required_fields=frozenset({"children", "component", "meta", "name", "path", "redirect"}),
        tracked_backend_contract="auth_routes",
    ),
    FrontendFieldContract(
        key="users_page_type",
        frontend_source="frontend/src/api/system/user-api.ts",
        required_fields=frozenset(
            {"avatar", "deptName", "email", "gender", "id", "isActive", "mobile", "name", "roleNames", "roles", "username"}
        ),
        tracked_backend_contract="users_out",
    ),
    FrontendFieldContract(
        key="users_form_type",
        frontend_source="frontend/src/api/system/user-api.ts",
        required_fields=frozenset(
            {"avatar", "deptId", "email", "gender", "id", "isActive", "mobile", "name", "roleNames", "roles", "username"}
        ),
        tracked_backend_contract="users_form_out",
    ),
    FrontendFieldContract(
        key="roles_page_type",
        frontend_source="frontend/src/api/system/role-api.ts",
        required_fields=frozenset(
            {"dataScope", "deptIds", "desc", "id", "name", "permissions", "sort", "status"}
        ),
        tracked_backend_contract="roles_out",
    ),
    FrontendFieldContract(
        key="roles_form_type",
        frontend_source="frontend/src/api/system/role-api.ts",
        required_fields=frozenset(
            {"dataScope", "deptIds", "desc", "id", "isDefault", "name", "sort", "status"}
        ),
        tracked_backend_contract="roles_out",
    ),
    FrontendFieldContract(
        key="menus_list_type",
        frontend_source="frontend/src/api/system/menu-api.ts",
        required_fields=frozenset(
            {
                "children",
                "component",
                "icon",
                "id",
                "name",
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
        tracked_backend_contract="menus_tree",
    ),
    FrontendFieldContract(
        key="menus_form_type",
        frontend_source="frontend/src/api/system/menu-api.ts",
        required_fields=frozenset(
            {
                "alwaysShow",
                "component",
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
        tracked_backend_contract="menus_out",
    ),
    FrontendFieldContract(
        key="depts_tree_type",
        frontend_source="frontend/src/api/system/dept-api.ts",
        required_fields=frozenset(
            {"children", "createTime", "id", "name", "parentId", "sort", "status", "updateTime"}
        ),
        tracked_backend_contract="depts_tree",
    ),
    FrontendFieldContract(
        key="dicts_page_type",
        frontend_source="frontend/src/api/system/dict-api.ts",
        required_fields=frozenset({"dictCode", "id", "name", "status"}),
        tracked_backend_contract="dicts_out",
    ),
    FrontendFieldContract(
        key="dicts_form_type",
        frontend_source="frontend/src/api/system/dict-api.ts",
        required_fields=frozenset({"dictCode", "id", "name", "remark", "status"}),
        tracked_backend_contract="dicts_out",
    ),
    FrontendFieldContract(
        key="dict_items_option_type",
        frontend_source="frontend/src/api/system/dict-items-api.ts",
        required_fields=frozenset({"label", "tagType", "value"}),
        tracked_backend_contract="dict_items_out",
    ),
    FrontendFieldContract(
        key="dict_items_page_type",
        frontend_source="frontend/src/api/system/dict-items-api.ts",
        required_fields=frozenset({"dictCode", "dictName", "id", "label", "status", "value"}),
        tracked_backend_contract="dict_items_out",
    ),
    FrontendFieldContract(
        key="dict_items_form_type",
        frontend_source="frontend/src/api/system/dict-items-api.ts",
        required_fields=frozenset({"dict", "dictCode", "id", "label", "status", "tagType", "value"}),
        tracked_backend_contract="dict_items_out",
    ),
    FrontendFieldContract(
        key="notices_page_type",
        frontend_source="frontend/src/api/system/notice-api.ts",
        required_fields=frozenset(
            {
                "content",
                "id",
                "publishStatus",
                "publishTime",
                "publisherId",
                "revokeTime",
                "targetType",
                "targetUserIds",
                "title",
                "type",
                "updateTime",
            }
        ),
        tracked_backend_contract="notices_page",
    ),
)


def iter_api_frontend_field_contracts() -> tuple[FrontendFieldContract, ...]:
    """返回不可变前端 API 字段契约目录。"""
    return API_FRONTEND_FIELD_CONTRACTS


def assert_api_frontend_field_contract_catalog() -> None:
    """校验前端字段契约目录自身一致性。"""
    backend_keys = _backend_field_contract_keys()
    keys = {contract.key for contract in API_FRONTEND_FIELD_CONTRACTS}
    assert len(keys) == len(API_FRONTEND_FIELD_CONTRACTS)
    for contract in API_FRONTEND_FIELD_CONTRACTS:
        assert contract.key
        assert contract.frontend_source.startswith("frontend/src/api/")
        assert contract.frontend_source.endswith(".ts")
        assert contract.required_fields
        assert contract.tracked_backend_contract in backend_keys


def _backend_field_contract_keys() -> set[str]:
    """返回后端字段契约 key，用于约束前端契约必须挂靠已登记漂移面。"""
    from scripts.api_field_contracts import iter_api_field_contracts

    return {contract.key for contract in iter_api_field_contracts()}
