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
        key="information_profile_type",
        frontend_source="frontend/src/api/information-api.ts",
        required_fields=frozenset(
            {
                "avatar",
                "deptName",
                "email",
                "gender",
                "id",
                "mobile",
                "name",
                "roleNames",
                "username",
            }
        ),
        tracked_backend_contract="information_profile",
    ),
    FrontendFieldContract(
        key="information_profile_update_type",
        frontend_source="frontend/src/api/information-api.ts",
        required_fields=frozenset({"email", "gender", "id", "mobile", "name"}),
        tracked_backend_contract="information_profile_update",
    ),
    FrontendFieldContract(
        key="information_avatar_type",
        frontend_source="frontend/src/api/information-api.ts",
        required_fields=frozenset({"avatar", "url"}),
        tracked_backend_contract="information_avatar",
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
        key="users_encoded_file_type",
        frontend_source="frontend/src/api/system/user-api.ts",
        required_fields=frozenset({"filename", "content", "contentType"}),
        tracked_backend_contract="encoded_file",
    ),
    FrontendFieldContract(
        key="users_import_result_type",
        frontend_source="frontend/src/api/system/user-api.ts",
        required_fields=frozenset({"validCount", "invalidCount", "messageList"}),
        tracked_backend_contract="user_import_result",
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
        tracked_backend_contract="roles_with_permissions",
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
        key="depts_form_type",
        frontend_source="frontend/src/api/system/dept-api.ts",
        required_fields=frozenset({"id", "name", "parentId", "sort", "status"}),
        tracked_backend_contract="depts_out",
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
    FrontendFieldContract(
        key="notices_form_type",
        frontend_source="frontend/src/api/system/notice-api.ts",
        required_fields=frozenset(
            {"content", "id", "level", "targetType", "targetUserIds", "title", "type"}
        ),
        tracked_backend_contract="notices_form",
    ),
    FrontendFieldContract(
        key="notices_detail_type",
        frontend_source="frontend/src/api/system/notice-api.ts",
        required_fields=frozenset(
            {
                "content",
                "id",
                "level",
                "publishStatus",
                "publishTime",
                "publisherName",
                "title",
                "type",
            }
        ),
        tracked_backend_contract="notices_detail",
    ),
    FrontendFieldContract(
        key="notices_my_page_type",
        frontend_source="frontend/src/api/system/notice-api.ts",
        required_fields=frozenset(
            {
                "content",
                "id",
                "isRead",
                "level",
                "publishStatus",
                "publishTime",
                "publisherId",
                "publisherName",
                "targetType",
                "targetUserIds",
                "title",
                "type",
                "updateTime",
            }
        ),
        tracked_backend_contract="notices_my_page",
    ),
    FrontendFieldContract(
        key="logs_page_type",
        frontend_source="frontend/src/api/system/log-api.ts",
        required_fields=frozenset(
            {
                "browser",
                "createdAt",
                "errorMsg",
                "executionTime",
                "id",
                "ip",
                "method",
                "name",
                "operation",
                "os",
                "objectId",
                "objectType",
                "path",
                "queryParams",
                "requestBody",
                "requestId",
                "requestContext",
                "responseBody",
                "responseStatus",
                "status",
                "updatedAt",
                "userId",
                "username",
            }
        ),
        tracked_backend_contract="logs_out",
    ),
    FrontendFieldContract(
        key="batch_delete_result_type",
        frontend_source="frontend/src/api/system/batch-delete.ts",
        required_fields=frozenset(
            {
                "failedCount",
                "failures",
                "message",
                "objectId",
                "objectName",
                "processedCount",
                "retryable",
                "status",
                "successCount",
                "successItems",
                "totalCount",
            }
        ),
        tracked_backend_contract="batch_delete_result",
    ),
)

FRONTEND_FIELD_CONTRACT_EXEMPT_ENDPOINTS = frozenset({"auth_login", "files_upload"})


def iter_api_frontend_field_contracts() -> tuple[FrontendFieldContract, ...]:
    """返回不可变前端 API 字段契约目录。"""
    return API_FRONTEND_FIELD_CONTRACTS


def iter_frontend_field_contract_exempt_endpoints() -> frozenset[str]:
    """返回不适用普通前端对象字段契约的端点。"""
    return FRONTEND_FIELD_CONTRACT_EXEMPT_ENDPOINTS


def assert_api_frontend_field_contract_catalog() -> None:
    """校验前端字段契约目录自身一致性。"""
    backend_keys = _backend_field_contract_keys()
    endpoint_keys = _critical_endpoint_keys()
    keys = {contract.key for contract in API_FRONTEND_FIELD_CONTRACTS}
    assert len(keys) == len(API_FRONTEND_FIELD_CONTRACTS)
    for contract in API_FRONTEND_FIELD_CONTRACTS:
        assert contract.key
        assert contract.frontend_source.startswith("frontend/src/api/")
        assert contract.frontend_source.endswith(".ts")
        assert contract.required_fields
        assert contract.tracked_backend_contract in backend_keys
    assert FRONTEND_FIELD_CONTRACT_EXEMPT_ENDPOINTS <= endpoint_keys
    assert FRONTEND_FIELD_CONTRACT_EXEMPT_ENDPOINTS.isdisjoint(keys)


def _backend_field_contract_keys() -> set[str]:
    """返回后端字段契约 key，用于约束前端契约必须挂靠已登记漂移面。"""
    from scripts.api_field_contracts import iter_api_field_contracts

    return {contract.key for contract in iter_api_field_contracts()}


def _critical_endpoint_keys() -> set[str]:
    """返回关键端点 key，用于约束前端字段契约豁免必须可追溯。"""
    from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts

    return {contract.key for contract in iter_critical_endpoint_contracts()}
