from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract


ROLE_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="roles_page",
        method="GET",
        path="/api/v1/system/roles/",
        auth_required=True,
        query_params=("page", "pageSize", "search"),
        response_fields=("list", "total"),
        permissions=("system:roles:query",),
        paginated=True,
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles", "RolesViewSet")),
            ContractEvidence(
                "fastapi/app/api/v1/system/roles.py",
                ("/", "system:roles:query", 'alias="pageSize"'),
            ),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("getPage", "/api/system/roles")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/roles/",)),
        ),
    ),
    EndpointContract(
        key="roles_create",
        method="POST",
        path="/api/v1/system/roles/",
        auth_required=True,
        request_fields=("name",),
        permissions=("system:roles:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles", "RolesViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("@router.post", "system:roles:add")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("create", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/roles/",)),
        ),
    ),
    EndpointContract(
        key="roles_update",
        method="PUT",
        path="/api/v1/system/roles/{id}/",
        auth_required=True,
        permissions=("system:roles:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles", "RolesViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("@router.put", "system:roles:edit")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("update", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/roles/{id}/",)),
        ),
    ),
    EndpointContract(
        key="roles_form",
        method="GET",
        path="/api/v1/system/roles/{id}/",
        auth_required=True,
        response_fields=("id", "name", "permissions"),
        permissions=("system:roles:query",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles", "RolesViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("/{role_id}/", "RoleWithPermissions")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("getFormData", "/api/system/roles")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/roles/{id}/",)),
        ),
    ),
    EndpointContract(
        key="roles_delete",
        method="DELETE",
        path="/api/v1/system/roles/",
        auth_required=True,
        request_fields=("ids",),
        permissions=("system:roles:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles", "RolesViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("@router.delete", "system:roles:delete")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("deleteByIds", 'method: "delete"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/system/roles/",)),
        ),
    ),
    EndpointContract(
        key="roles_menu_ids",
        method="GET",
        path="/api/v1/system/roles/{id}/menu-ids/",
        auth_required=True,
        permissions=("system:roles:query",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("roles/<int:pk>/menu-ids/",)),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("/{role_id}/menu-ids/", "system:roles:query")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("getRoleMenuIds", "/menu-ids/")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/roles/{id}/menu-ids/",)),
        ),
    ),
    EndpointContract(
        key="roles_menu_assign",
        method="PUT",
        path="/api/v1/system/roles/{id}/menus/",
        auth_required=True,
        request_fields=("menuIds",),
        permissions=("system:roles:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/views/roles.py", ("assign_menus", "menu_ids")),
            ContractEvidence("fastapi/app/api/v1/system/roles.py", ("assign_role_menus", "system:roles:edit")),
            ContractEvidence("frontend/src/api/system/role-api.ts", ("updateRoleMenus", "/menus/", "menuIds")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/roles/{id}/menus/",)),
        ),
    ),
)
