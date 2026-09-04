from __future__ import annotations

from scripts.api_endpoint_contract_types import (
    BATCH_DELETE_RESPONSE_FIELDS,
    ContractEvidence,
    EndpointContract,
)


NOTICE_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="notices_page",
        method="GET",
        path="/api/v1/system/notices/page",
        auth_required=True,
        query_params=("pageNum", "pageSize", "title", "publishStatus"),
        response_fields=("list", "total"),
        permissions=("system:notices:query",),
        paginated=True,
        evidence=(
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ("/page", "system:notices:query", 'alias="pageSize"'),
            ),
            ContractEvidence("frontend/src/api/system/notice-api.ts", ("getPage", "/api/system/notices", "/page")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("GET    /api/v1/system/notices/page",)),
        ),
    ),
    EndpointContract(
        key="notices_create",
        method="POST",
        path="/api/v1/system/notices",
        auth_required=True,
        request_fields=("title", "content", "type", "level", "targetType"),
        response_fields=("id", "title", "content"),
        permissions=("system:notices:add",),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/system/notices.py", ("@router.post", "system:notices:add")),
            ContractEvidence("frontend/src/api/system/notice-api.ts", ("create", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/notices",)),
        ),
    ),
    EndpointContract(
        key="notices_update",
        method="PUT",
        path="/api/v1/system/notices/{id}",
        auth_required=True,
        response_fields=("id", "title", "content"),
        permissions=("system:notices:edit",),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/system/notices.py", ("@router.put", "system:notices:edit")),
            ContractEvidence("frontend/src/api/system/notice-api.ts", ("update", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/notices/{id}",)),
        ),
    ),
    EndpointContract(
        key="notices_delete",
        method="DELETE",
        path="/api/v1/system/notices/",
        auth_required=True,
        request_fields=("ids",),
        response_fields=BATCH_DELETE_RESPONSE_FIELDS,
        permissions=("system:notices:delete",),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/system/urls.py",
                ("notices/", "notices/<str:ids>"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ('@router.delete("",', '@router.delete("/",', '@router.delete("/{ids}",', "system:notices:delete"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("deleteByIds", 'method: "delete"', 'data: batchDeleteRequest(ids)'),
            ),
            ContractEvidence(
                "docs/API_ENDPOINTS.md",
                ("DELETE /api/v1/system/notices/", "DELETE /api/v1/system/notices/{ids}"),
            ),
        ),
    ),
    EndpointContract(
        key="notices_delete_retry",
        method="POST",
        path="/api/v1/system/notices/batch-delete/retry/",
        auth_required=True,
        request_fields=("ids",),
        response_fields=BATCH_DELETE_RESPONSE_FIELDS,
        permissions=("system:notices:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("notices/batch-delete/retry/",)),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ("/batch-delete/retry/", "system:notices:delete"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("retryBatchDelete", "/batch-delete/retry/", 'method: "post"'),
            ),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/notices/batch-delete/retry/",)),
        ),
    ),
    EndpointContract(
        key="notices_publish",
        method="PUT",
        path="/api/v1/system/notices/{id}/publish",
        auth_required=True,
        permissions=("system:notices:publish",),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/system/notices.py", ("publish_notice", "system:notices:publish")),
            ContractEvidence("frontend/src/api/system/notice-api.ts", ("publish", "/publish")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/notices/{id}/publish",)),
        ),
    ),
    EndpointContract(
        key="notices_revoke",
        method="PUT",
        path="/api/v1/system/notices/{id}/revoke",
        auth_required=True,
        permissions=("system:notices:revoke",),
        evidence=(
            ContractEvidence("fastapi/app/api/v1/system/notices.py", ("revoke_notice", "system:notices:revoke")),
            ContractEvidence("frontend/src/api/system/notice-api.ts", ("revoke", "/revoke")),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/notices/{id}/revoke",)),
        ),
    ),
    EndpointContract(
        key="notices_form",
        method="GET",
        path="/api/v1/system/notices/{id}/form",
        auth_required=True,
        response_fields=("id", "title", "content"),
        permissions=("system:notices:query",),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/system/urls.py",
                ("notices/<int:pk>/form", "retrieve"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ("/{notice_id}/form", "system:notices:query"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("getFormData", "/form"),
            ),
        ),
    ),
    EndpointContract(
        key="notices_detail",
        method="GET",
        path="/api/v1/system/notices/{id}/detail",
        auth_required=True,
        response_fields=("id", "title", "content"),
        permissions=("system:notices:query",),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/system/urls.py",
                ("notices/<int:pk>/detail", "NoticeDetailAPIView"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ("/{notice_id}/detail", "system:notices:query"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("getDetail", "/detail"),
            ),
        ),
    ),
    EndpointContract(
        key="notices_read_all",
        method="PUT",
        path="/api/v1/system/notices/read-all",
        auth_required=True,
        permissions=("system:notices:query",),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/system/urls.py",
                ("notices/read-all", "NoticeReadAllAPIView"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ('@router.put("/read-all"', "system:notices:query"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("readAll", "/read-all"),
            ),
        ),
    ),
    EndpointContract(
        key="notices_my_page",
        method="GET",
        path="/api/v1/system/notices/my-page/",
        auth_required=True,
        query_params=("pageNum", "pageSize", "title", "isRead"),
        response_fields=("list", "total"),
        permissions=("system:notices:query",),
        paginated=True,
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/system/urls.py",
                ("notices/my-page/", "NoticesAPIView"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/system/notices.py",
                ('@router.get("/my-page/"', "system:notices:query"),
            ),
            ContractEvidence(
                "frontend/src/api/system/notice-api.ts",
                ("getMyNoticePage", "/my-page/"),
            ),
        ),
    ),
)
