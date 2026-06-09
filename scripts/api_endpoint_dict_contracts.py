from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract


DICT_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="dicts_page",
        method="GET",
        path="/api/v1/system/dicts/",
        auth_required=True,
        query_params=("page", "pageSize", "search"),
        response_fields=("list", "total"),
        permissions=("system:dicts:query",),
        paginated=True,
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dicts", "DictsViewSet")),
            ContractEvidence(
                "fastapi/app/api/v1/system/dicts.py",
                ("/", "system:dicts:query", 'alias="pageSize"'),
            ),
            ContractEvidence("frontend/src/api/system/dict-api.ts", ("getPage", "/api/system/dicts")),
        ),
    ),
    EndpointContract(
        key="dicts_create",
        method="POST",
        path="/api/v1/system/dicts/",
        auth_required=True,
        request_fields=("name", "dictCode"),
        response_fields=("id", "name", "dictCode", "remark"),
        permissions=("system:dicts:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dicts", "DictsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dicts.py", ("@router.post", "system:dicts:add")),
            ContractEvidence("frontend/src/api/system/dict-api.ts", ("create", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/dicts/",)),
        ),
    ),
    EndpointContract(
        key="dicts_update",
        method="PUT",
        path="/api/v1/system/dicts/{id}/",
        auth_required=True,
        response_fields=("id", "name", "dictCode", "remark"),
        permissions=("system:dicts:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dicts", "DictsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dicts.py", ("@router.put", "system:dicts:edit")),
            ContractEvidence("frontend/src/api/system/dict-api.ts", ("update", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/dicts/{id}/",)),
        ),
    ),
    EndpointContract(
        key="dicts_delete",
        method="DELETE",
        path="/api/v1/system/dicts/",
        auth_required=True,
        request_fields=("ids",),
        permissions=("system:dicts:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dicts", "DictsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dicts.py", ("@router.delete", "system:dicts:delete")),
            ContractEvidence("frontend/src/api/system/dict-api.ts", ("deleteByIds", 'method: "delete"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/system/dicts/",)),
        ),
    ),
    EndpointContract(
        key="dict_items_page",
        method="GET",
        path="/api/v1/system/dict-items/",
        auth_required=True,
        query_params=("page", "pageSize", "dict", "dictCode"),
        response_fields=("list", "total"),
        permissions=("system:dictitems:query",),
        paginated=True,
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dict-items", "DictItemsViewSet")),
            ContractEvidence(
                "fastapi/app/api/v1/system/dict_items.py",
                ("/", "system:dictitems:query", 'alias="pageSize"'),
            ),
            ContractEvidence("frontend/src/api/system/dict-items-api.ts", ("getDictItemPage", "/api/system/dict-items")),
        ),
    ),
    EndpointContract(
        key="dict_items_create",
        method="POST",
        path="/api/v1/system/dict-items/",
        auth_required=True,
        request_fields=("dict", "label", "value"),
        response_fields=("id", "dict", "label", "value"),
        permissions=("system:dictitems:add",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dict-items", "DictItemsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dict_items.py", ("@router.post", "system:dictitems:add")),
            ContractEvidence("frontend/src/api/system/dict-items-api.ts", ("createDictItem", 'method: "post"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("POST   /api/v1/system/dict-items/",)),
        ),
    ),
    EndpointContract(
        key="dict_items_update",
        method="PUT",
        path="/api/v1/system/dict-items/{id}/",
        auth_required=True,
        response_fields=("id", "dict", "label", "value"),
        permissions=("system:dictitems:edit",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dict-items", "DictItemsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dict_items.py", ("@router.put", "system:dictitems:edit")),
            ContractEvidence("frontend/src/api/system/dict-items-api.ts", ("updateDictItem", 'method: "put"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("PUT    /api/v1/system/dict-items/{id}/",)),
        ),
    ),
    EndpointContract(
        key="dict_items_delete",
        method="DELETE",
        path="/api/v1/system/dict-items/",
        auth_required=True,
        request_fields=("ids",),
        permissions=("system:dictitems:delete",),
        evidence=(
            ContractEvidence("backend/drf_admin/apps/system/urls.py", ("dict-items", "DictItemsViewSet")),
            ContractEvidence("fastapi/app/api/v1/system/dict_items.py", ("@router.delete", "system:dictitems:delete")),
            ContractEvidence("frontend/src/api/system/dict-items-api.ts", ("deleteDictItems", 'method: "delete"')),
            ContractEvidence("docs/API_ENDPOINTS.md", ("DELETE /api/v1/system/dict-items/",)),
        ),
    ),
)
