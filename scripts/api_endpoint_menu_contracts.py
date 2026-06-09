from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract


MENU_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="menus_tree",
        method="GET",
        path="/api/v1/system/menus/",
        auth_required=True,
        response_fields=("children", "component", "perm", "routePath"),
        permissions=("system:permissions:query",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("menus", "MenusViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/menus.py", ("/", "system:permissions:query")),
            ContractEvidence("frontend/src/api/system/menu-api.ts", ("getList", "/api/system/menus")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/menus/",)),
        ),
    ),
    EndpointContract(
        key="menus_create",
        method="POST",
        path="/api/v1/system/menus/",
        auth_required=True,
        request_fields=("name", "type"),
        permissions=("system:permissions:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("menus", "MenusViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/menus.py", ("@router.post", "system:permissions:add")),
            ContractEvidence("frontend/src/api/system/menu-api.ts", ("create", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/menus/",)),
        ),
    ),
    EndpointContract(
        key="menus_update",
        method="PUT",
        path="/api/v1/system/menus/{id}/",
        auth_required=True,
        permissions=("system:permissions:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("menus", "MenusViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/menus.py", ("@router.put", "system:permissions:edit")),
            ContractEvidence("frontend/src/api/system/menu-api.ts", ("update", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/menus/{id}/",)),
        ),
    ),
    EndpointContract(
        key="menus_delete",
        method="DELETE",
        path="/api/v1/system/menus/{id}/",
        auth_required=True,
        permissions=("system:permissions:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("menus", "MenusViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/menus.py", ("@router.delete", "system:permissions:delete")),
            ContractEvidence("frontend/src/api/system/menu-api.ts", ("deleteById", 'method: "delete"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/system/menus/{id}/",)),
        ),
    ),
)
