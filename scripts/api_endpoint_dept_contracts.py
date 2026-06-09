from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract


DEPT_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="depts_tree",
        method="GET",
        path="/api/v1/system/departments/",
        auth_required=True,
        query_params=("search", "status"),
        response_fields=("id", "name", "status"),
        permissions=("system:departments:query",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("departments", "DepartmentsViewSet")),
            ContractEvidence(
                "backend/drf_admin/apps/system/views/departments.py",
                ("DepartmentsViewSet", "search_fields", "filterset_fields"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/depts.py",
                ("/", "system:departments:query", "search", "status"),
            ),
            ContractEvidence("frontend/src/api/system/dept-api.ts", ("getList", "/api/system/departments")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/departments/",)),
        ),
    ),
    EndpointContract(
        key="depts_create",
        method="POST",
        path="/api/v1/system/departments/",
        auth_required=True,
        request_fields=("name",),
        permissions=("system:departments:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("departments", "DepartmentsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/depts.py", ("@router.post", "system:departments:add")),
            ContractEvidence("frontend/src/api/system/dept-api.ts", ("create", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/departments/",)),
        ),
    ),
    EndpointContract(
        key="depts_update",
        method="PUT",
        path="/api/v1/system/departments/{id}/",
        auth_required=True,
        permissions=("system:departments:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("departments", "DepartmentsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/depts.py", ("@router.put", "system:departments:edit")),
            ContractEvidence("frontend/src/api/system/dept-api.ts", ("update", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/departments/{id}/",)),
        ),
    ),
    EndpointContract(
        key="depts_delete",
        method="DELETE",
        path="/api/v1/system/departments/",
        auth_required=True,
        request_fields=("ids",),
        permissions=("system:departments:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("departments", "DepartmentsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/depts.py", ("@router.delete", "system:departments:delete")),
            ContractEvidence("frontend/src/api/system/dept-api.ts", ("deleteByIds", 'method: "delete"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/system/departments/",)),
        ),
    ),
)
