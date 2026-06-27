from __future__ import annotations

MAX_RUNTIME_CONTRACT_TEST_LINES = 300

REQUIRED_FILES = (
    "scripts/api_contracts.py",
    "scripts/api_capability_contracts.py",
    "scripts/api_error_codes.py",
    "scripts/api_field_contracts.py",
    "scripts/api_endpoint_contracts.py",
    "scripts/api_endpoint_contract_types.py",
    "scripts/api_endpoint_dept_contracts.py",
    "scripts/api_endpoint_dict_contracts.py",
    "scripts/api_endpoint_menu_contracts.py",
    "scripts/api_endpoint_notice_contracts.py",
    "scripts/api_endpoint_role_contracts.py",
    "scripts/api_contract_validation_rules.py",
    "backend/drf_admin/utils/runtime_api_contracts/helpers.py",
    "backend/drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py",
    "backend/drf_admin/utils/runtime_api_contracts/test_notice_write_contracts.py",
    "backend/drf_admin/utils/runtime_api_contracts/test_read_contracts.py",
    "backend/drf_admin/utils/runtime_api_contracts/test_write_contracts.py",
    "backend/drf_admin/utils/test_response_contract.py",
    "backend/drf_admin/utils/test_api_capability_contracts.py",
    "backend/drf_admin/utils/test_api_field_contracts.py",
    "fastapi/tests/test_api_contracts.py",
    "fastapi/tests/test_api_capability_contracts.py",
    "fastapi/tests/test_api_field_contracts.py",
    "fastapi/tests/runtime_api_contracts/helpers.py",
    "fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py",
    "fastapi/tests/runtime_api_contracts/test_notice_write_contracts.py",
    "fastapi/tests/runtime_api_contracts/test_read_and_file_contracts.py",
    "fastapi/tests/runtime_api_contracts/test_write_contracts.py",
    "frontend/src/utils/__tests__/api-contract.test.ts",
    "frontend/src/enums/api/code-enum.ts",
    "backend/drf_admin/apps/system/README.md",
    "docs/API_ENDPOINTS.md",
    "fastapi/app/api/v1/README.md",
)

RUNTIME_CONTRACT_TEST_PATTERNS = (
    "backend/drf_admin/utils/test_runtime_api_contracts.py",
    "backend/drf_admin/utils/runtime_api_contracts/test_*.py",
    "fastapi/tests/test_runtime_api_contracts.py",
    "fastapi/tests/runtime_api_contracts/test_*.py",
)

REQUIRED_CONTRACT_FUNCTIONS = (
    "normalize_api_envelope",
    "assert_success_envelope",
    "assert_error_envelope",
    "assert_page_payload",
    "iter_critical_endpoint_contracts",
    "assert_endpoint_contract_catalog",
)

REQUIRED_DOC_SNIPPETS = (
    "共享 API 契约验证",
    "关键端点契约目录",
    "共享错误码契约目录",
    "scripts/validate_api_contracts.py",
    "scripts/api_capability_contracts.py",
    "scripts/api_endpoint_contracts.py",
    "scripts/api_field_contracts.py",
    "scripts/api_error_codes.py",
    "Django 响应中间件统一输出",
    "FastAPI `ResponseModel` 默认输出",
)

REQUIRED_TEST_SNIPPETS = {
    "backend/drf_admin/utils/test_response_contract.py": (
        "assert_success_envelope",
        "assert_error_envelope",
        "assert_api_error_code_catalog",
        "assert_endpoint_contract_catalog",
        "dicts_create",
        "dict_items_create",
    ),
    "backend/drf_admin/utils/test_api_field_contracts.py": (
        "iter_api_field_contracts",
        "assert_api_field_contract_catalog",
        "django_output_keys",
        "未登记字段",
    ),
    "backend/drf_admin/utils/test_api_capability_contracts.py": (
        "iter_api_capability_contracts",
        "assert_api_capability_contract_catalog",
        "FastAPI 独占",
        "OperationLog",
    ),
    "backend/drf_admin/utils/runtime_api_contracts/helpers.py": (
        "iter_critical_endpoint_contracts",
        "assert_success_envelope",
        "DICT_WRITE_SAMPLE_KEYS",
        "DICT_ITEM_WRITE_SAMPLE_KEYS",
        "NOTICE_WRITE_SAMPLE_KEYS",
    ),
    "backend/drf_admin/utils/runtime_api_contracts/test_read_contracts.py": ("dictCode", "depts_tree"),
    "backend/drf_admin/utils/runtime_api_contracts/test_write_contracts.py": (
        "test_django_user_write_runtime_samples_match_endpoint_catalog",
        "users_create",
        "users_update",
        "users_delete",
        "depts_create",
        "menus_create",
    ),
    "backend/drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py": (
        "test_django_dict_write_runtime_samples_match_endpoint_catalog",
        "test_django_dict_item_write_runtime_samples_match_endpoint_catalog",
        "dicts_create",
        "dict_items_create",
    ),
    "backend/drf_admin/utils/runtime_api_contracts/test_notice_write_contracts.py": (
        "test_django_notice_write_runtime_samples_match_endpoint_catalog",
        "notices_create",
        "notices_publish",
        "notices_revoke",
    ),
    "fastapi/tests/test_api_contracts.py": (
        "ResponseModel.success",
        "PageResult.create",
        "assert_api_error_code_catalog",
        "assert_endpoint_contract_catalog",
        "roles_menu_assign",
        "depts_create",
        "menus_create",
        "dicts_create",
        "dict_items_create",
        "notices_create",
        "logs_page",
    ),
    "fastapi/tests/test_api_field_contracts.py": (
        "iter_api_field_contracts",
        "assert_api_field_contract_catalog",
        "fastapi_output_keys",
        "未登记字段",
    ),
    "fastapi/tests/test_api_capability_contracts.py": (
        "iter_api_capability_contracts",
        "assert_api_capability_contract_catalog",
        "fastapi_snippets",
        "真实路由源码",
    ),
    "fastapi/tests/runtime_api_contracts/helpers.py": (
        "iter_critical_endpoint_contracts",
        "DICT_WRITE_SAMPLE_KEYS",
        "DICT_ITEM_WRITE_SAMPLE_KEYS",
        "NOTICE_WRITE_SAMPLE_KEYS",
    ),
    "fastapi/tests/runtime_api_contracts/test_read_and_file_contracts.py": ("files_upload", "files_delete", "logs_page"),
    "fastapi/tests/runtime_api_contracts/test_write_contracts.py": (
        "test_fastapi_user_write_runtime_samples_match_endpoint_catalog",
        "users_create",
        "roles_menu_assign",
        "depts_create",
        "menus_create",
    ),
    "fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py": (
        "test_fastapi_dict_write_runtime_samples_match_endpoint_catalog",
        "test_fastapi_dict_item_write_runtime_samples_match_endpoint_catalog",
        "dicts_create",
        "dict_items_create",
    ),
    "fastapi/tests/runtime_api_contracts/test_notice_write_contracts.py": (
        "test_fastapi_notice_write_runtime_samples_match_endpoint_catalog",
        "notices_create",
        "notices_publish",
        "notices_revoke",
    ),
    "frontend/src/utils/__tests__/api-contract.test.ts": (
        "Django",
        "FastAPI",
        "ApiCodeEnum.ACCESS_TOKEN_INVALID",
        "ApiCodeEnum.REFRESH_TOKEN_INVALID",
        "normalizeApiErrorEnvelope",
        "list",
        "total",
    ),
}

REQUIRED_FILE_ROUTE_SNIPPETS = {
    "docs/API_ENDPOINTS.md": (
        "POST   /api/v1/files/",
        "DELETE /api/v1/files/?filePath=files/{user_id}/{filename}",
        "上传响应 `data.path`",
    ),
    "fastapi/app/api/v1/README.md": (
        "POST /api/v1/files/",
        "DELETE /api/v1/files/?filePath=files/{user_id}/{filename}",
        "GET /api/v1/system/notices/page",
        "PUT /api/v1/system/notices/{id}/publish",
        "GET /api/v1/system/logs/page",
    ),
}

FORBIDDEN_FILE_ROUTE_SNIPPETS = {
    "docs/API_ENDPOINTS.md": ("/api/v1/files/upload/",),
    "fastapi/app/api/v1/README.md": ("/api/v1/files/upload/",),
    "backend/drf_admin/apps/system/README.md": (
        "logs.py       # 操作日志",
        "| `/api/v1/system/logs/` | GET | 日志列表 |",
    ),
}
