from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract
from scripts.api_endpoint_dept_contracts import DEPT_ENDPOINT_CONTRACTS
from scripts.api_endpoint_dict_contracts import DICT_ENDPOINT_CONTRACTS
from scripts.api_endpoint_menu_contracts import MENU_ENDPOINT_CONTRACTS
from scripts.api_endpoint_notice_contracts import NOTICE_ENDPOINT_CONTRACTS
from scripts.api_endpoint_role_contracts import ROLE_ENDPOINT_CONTRACTS


HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
REQUIRED_ENDPOINT_KEYS = {
    "auth_login",
    "auth_info",
    "auth_routes",
    "users_page",
    "users_form",
    "users_create",
    "users_update",
    "users_delete",
    "roles_page",
    "roles_create",
    "roles_update",
    "roles_form",
    "roles_delete",
    "roles_menu_ids",
    "roles_menu_assign",
    "depts_tree",
    "depts_create",
    "depts_update",
    "depts_delete",
    "menus_tree",
    "menus_create",
    "menus_update",
    "menus_delete",
    "dicts_page",
    "dicts_create",
    "dicts_update",
    "dicts_delete",
    "dict_items_page",
    "dict_items_create",
    "dict_items_update",
    "dict_items_delete",
    "notices_page",
    "notices_create",
    "notices_update",
    "notices_delete",
    "notices_publish",
    "notices_revoke",
    "logs_page",
    "files_upload",
    "files_delete",
}


CRITICAL_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="auth_login",
        method="POST",
        path="/api/v1/oauth/login/",
        auth_required=False,
        request_fields=("username", "password"),
        response_fields=("accessToken", "refreshToken", "tokenType", "expiresIn"),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/oauth/urls.py", ("login/",)),
            ContractEvidence("fastapi/app/api/v1/oauth/routes/login.py", ("/login/", "UserLogin")),
            ContractEvidence("frontend/src/api/auth-api.ts", ("/api/oauth", "/login/")),
        ),
    ),
    EndpointContract(
        key="auth_info",
        method="GET",
        path="/api/v1/oauth/info/",
        auth_required=True,
        response_fields=("id", "username", "roles", "perms"),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/oauth/urls.py", ("info/",)),
            ContractEvidence("fastapi/app/api/v1/oauth/routes/profile.py", ("/info/", "CurrentUser")),
            ContractEvidence("frontend/src/api/auth-api.ts", ("getInfo", "/info/")),
        ),
    ),
    EndpointContract(
        key="auth_routes",
        method="GET",
        path="/api/v1/oauth/menus/routes/",
        auth_required=True,
        response_fields=("children", "component", "meta", "path"),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/oauth/urls.py", ("menus/routes/",)),
            ContractEvidence("fastapi/app/api/v1/oauth/routes/menus.py", ("/menus/routes/", "get_user_menus")),
            ContractEvidence("frontend/src/api/auth-api.ts", ("getRoutes", "/menus/routes/")),
        ),
    ),
    EndpointContract(
        key="users_page",
        method="GET",
        path="/api/v1/system/users/",
        auth_required=True,
        query_params=("pageNum", "pageSize", "search", "isActive", "dept"),
        response_fields=("list", "total"),
        permissions=("system:users:query",),
        paginated=True,
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("users", "UsersViewSet")),
            ContractEvidence(
                "fastapi/app/api/v1/system/user_routes/query.py",
                ("/", "system:users:query", "page_params"),
            ),
            ContractEvidence("fastapi/app/api/pagination.py", ("page_params", 'alias="pageNum"', 'alias="pageSize"')),
            ContractEvidence("frontend/src/api/system/user-api.ts", ("getPage", "/api/system/users")),
        ),
    ),
    EndpointContract(
        key="users_form",
        method="GET",
        path="/api/v1/system/users/{id}/",
        auth_required=True,
        response_fields=("id", "username", "roles"),
        permissions=("system:users:query",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("users", "UsersViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/user_routes/query.py", ("/{user_id}/", "UserFormOut")),
            ContractEvidence("frontend/src/api/system/user-api.ts", ("getFormData", "/api/system/users")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/users/{id}/",)),
        ),
    ),
    EndpointContract(
        key="users_create",
        method="POST",
        path="/api/v1/system/users/",
        auth_required=True,
        request_fields=("username", "name", "password"),
        response_fields=("id", "username", "name"),
        permissions=("system:users:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("users", "UsersViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/user_routes/mutation.py", ("@router.post", "system:users:add")),
            ContractEvidence("frontend/src/api/system/user-api.ts", ("create", 'method: "post"')),
        ),
    ),
    EndpointContract(
        key="users_update",
        method="PUT",
        path="/api/v1/system/users/{id}/",
        auth_required=True,
        response_fields=("id", "username", "name"),
        permissions=("system:users:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("users", "UsersViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/user_routes/mutation.py", ("@router.put", "system:users:edit")),
            ContractEvidence("frontend/src/api/system/user-api.ts", ("update", 'method: "put"')),
        ),
    ),
    EndpointContract(
        key="users_delete",
        method="DELETE",
        path="/api/v1/system/users/",
        auth_required=True,
        request_fields=("ids",),
        permissions=("system:users:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("users", "UsersViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/user_routes/mutation.py", ("@router.delete", "system:users:delete")),
            ContractEvidence("frontend/src/api/system/user-api.ts", ("deleteByIds", 'method: "delete"')),
        ),
    ),
    *ROLE_ENDPOINT_CONTRACTS,
    *DEPT_ENDPOINT_CONTRACTS,
    *MENU_ENDPOINT_CONTRACTS,
    *DICT_ENDPOINT_CONTRACTS,
    *NOTICE_ENDPOINT_CONTRACTS,
    EndpointContract(
        key="logs_page",
        method="GET",
        path="/api/v1/system/logs/page",
        auth_required=True,
        query_params=("pageNum", "pageSize", "operation", "startTime", "endTime"),
        response_fields=("list", "total"),
        permissions=("system:logs:query",),
        paginated=True,
        evidence=(
            ContractEvidence(
                "fastapi/app/api/v1/system/log_routes/query.py",
                ("/page", "system:logs:query", "page_params", 'alias="startTime"'),
            ),
            ContractEvidence("fastapi/app/api/pagination.py", ("page_params", 'alias="pageNum"', 'alias="pageSize"')),
            ContractEvidence("frontend/src/api/system/log-api.ts", ("getPage", "/api/system/logs")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/logs/page",)),
            ContractEvidence("fastapi/app/api/v1/README.md", ("GET /api/v1/system/logs/page",)),
        ),
    ),
    EndpointContract(
        key="files_upload",
        method="POST",
        path="/api/v1/files/",
        auth_required=True,
        request_fields=("file",),
        response_fields=("name", "url", "path"),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/files/upload.py", ("@router.post", "save_upload_file")),
            ContractEvidence("frontend/src/api/file-api.ts", ("upload", "/api/v1/files/", "path")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/files/", "name/url/path")),
            ContractEvidence("fastapi/app/api/v1/README.md", ("POST /api/v1/files/", "name/url/path")),
        ),
    ),
    EndpointContract(
        key="files_delete",
        method="DELETE",
        path="/api/v1/files/",
        auth_required=True,
        query_params=("filePath",),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/files/upload.py", ("@router.delete", "filePath")),
            ContractEvidence("frontend/src/api/file-api.ts", ("delete", "/api/v1/files/")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/files/",)),
            ContractEvidence("fastapi/app/api/v1/README.md", ("DELETE /api/v1/files/",)),
        ),
    ),
)


def iter_critical_endpoint_contracts() -> tuple[EndpointContract, ...]:
    """返回不可变端点契约目录，避免调用方修改共享基线。"""
    return CRITICAL_ENDPOINT_CONTRACTS


def assert_endpoint_contract_catalog() -> None:
    """断言关键端点契约目录自身完整且没有明显漂移。"""
    keys = {contract.key for contract in CRITICAL_ENDPOINT_CONTRACTS}
    assert keys == REQUIRED_ENDPOINT_KEYS
    assert len(keys) == len(CRITICAL_ENDPOINT_CONTRACTS)
    for contract in CRITICAL_ENDPOINT_CONTRACTS:
        _assert_endpoint_contract(contract)


def _assert_endpoint_contract(contract: EndpointContract) -> None:
    """校验单个端点契约的基础字段，避免无效契约进入门禁。"""
    assert contract.method in HTTP_METHODS, f"invalid method: {contract.method}"
    assert contract.path.startswith("/api/v1/"), f"invalid path: {contract.path}"
    assert " " not in contract.path, f"path must not contain spaces: {contract.path}"
    assert contract.evidence, f"{contract.key}: missing evidence"
    if contract.paginated:
        assert "list" in contract.response_fields
        assert "total" in contract.response_fields
    if contract.permissions:
        assert contract.auth_required, f"{contract.key}: permission requires auth"
