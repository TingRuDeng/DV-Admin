from scripts.api_contracts import (
    CRITICAL_ENDPOINT_CONTRACTS,
    assert_endpoint_contract_catalog,
    assert_error_envelope,
    assert_page_payload,
    assert_success_envelope,
    normalize_api_envelope,
)
from scripts.api_error_codes import (
    ACCESS_TOKEN_INVALID_CODE,
    ERROR_CODE,
    REFRESH_TOKEN_INVALID_CODE,
    SUCCESS_CODE,
    assert_api_error_code_catalog,
)

from app.schemas.base import PageResult, ResponseModel


def test_fastapi_success_response_matches_shared_contract():
    response = ResponseModel.success(data={"id": 1}, message="成功").model_dump()

    assert_success_envelope(response, backend="fastapi")
    envelope = normalize_api_envelope(response)
    assert envelope.message == "成功"
    assert envelope.data == {"id": 1}


def test_fastapi_error_response_matches_shared_contract():
    response = ResponseModel.error(code=40000, message="参数错误").model_dump()

    assert_error_envelope(response, backend="fastapi")
    envelope = normalize_api_envelope(response)
    assert envelope.message == "参数错误"


def test_fastapi_page_result_matches_frontend_pagination_contract():
    page = PageResult.create(total=1, page=1, page_size=10, results=[{"id": 1}]).model_dump()

    assert_page_payload(page)
    assert page["list"] == [{"id": 1}]
    assert page["total"] == 1


def test_shared_resource_timestamps_use_django_compatible_aliases():
    """共享业务资源对外时间字段统一使用 createTime/updateTime。"""
    from datetime import datetime, timezone

    from app.schemas.system import DeptOut, DictDataOut, MenuOut, RoleOut

    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    samples = [
        DeptOut(id=1, name="部门", status=1, sort=1, parent_id=None, created_at=now, updated_at=now),
        DictDataOut(id=1, name="字典", dict_code="demo", status=1, remark="", created_at=now, updated_at=now),
        MenuOut(id=1, name="菜单", type="MENU", created_at=now, updated_at=now),
        RoleOut(id=1, name="角色", code="role", status=1, sort=1, created_at=now, updated_at=now),
    ]

    for sample in samples:
        payload = sample.model_dump(by_alias=True)
        assert "createTime" in payload
        assert "updateTime" in payload
        assert "createdAt" not in payload
        assert "updatedAt" not in payload


def test_fastapi_critical_endpoint_contract_catalog_matches_route_contracts():
    assert_endpoint_contract_catalog()
    contracts = {contract.key: contract for contract in CRITICAL_ENDPOINT_CONTRACTS}

    assert contracts["auth_login"].path == "/api/v1/oauth/login/"
    assert contracts["users_page"].paginated is True
    assert contracts["users_page"].permissions == ("system:users:query",)
    assert contracts["roles_page"].path == "/api/v1/system/roles/"
    assert contracts["roles_page"].permissions == ("system:roles:query",)
    assert contracts["roles_menu_assign"].path == "/api/v1/system/roles/{id}/menus/"
    assert contracts["roles_menu_assign"].request_fields == ("menuIds",)
    assert contracts["roles_menu_assign"].permissions == ("system:roles:edit",)
    assert contracts["depts_tree"].path == "/api/v1/system/departments/"
    assert contracts["depts_tree"].permissions == ("system:departments:query",)
    assert contracts["depts_create"].permissions == ("system:departments:add",)
    assert contracts["depts_update"].permissions == ("system:departments:edit",)
    assert contracts["depts_delete"].request_fields == ("ids",)
    assert contracts["menus_create"].permissions == ("system:permissions:add",)
    assert contracts["menus_update"].permissions == ("system:permissions:edit",)
    assert contracts["menus_delete"].method == "DELETE"
    assert contracts["dicts_create"].request_fields == ("name", "dictCode")
    assert contracts["dicts_update"].permissions == ("system:dicts:edit",)
    assert contracts["dicts_delete"].request_fields == ("ids",)
    assert contracts["dict_items_page"].permissions == ("system:dictitems:query",)
    assert contracts["dict_items_create"].request_fields == ("dict", "label", "value")
    assert contracts["dict_items_update"].permissions == ("system:dictitems:edit",)
    assert contracts["dict_items_delete"].request_fields == ("ids",)
    assert contracts["notices_page"].path == "/api/v1/system/notices/page"
    assert contracts["notices_page"].permissions == ("system:notices:query",)
    assert contracts["notices_create"].permissions == ("system:notices:add",)
    assert contracts["notices_update"].permissions == ("system:notices:edit",)
    assert contracts["notices_delete"].path == "/api/v1/system/notices/{ids}"
    assert contracts["notices_publish"].permissions == ("system:notices:publish",)
    assert contracts["notices_revoke"].permissions == ("system:notices:revoke",)
    assert contracts["logs_page"].path == "/api/v1/system/logs/page"
    assert contracts["logs_page"].permissions == ("system:logs:query",)
    assert contracts["files_upload"].response_fields == ("name", "url", "path")


def test_fastapi_error_codes_match_shared_catalog():
    assert_api_error_code_catalog()

    assert ResponseModel.success(data={"id": 1}).code == SUCCESS_CODE
    assert ResponseModel.error(code=ERROR_CODE, message="参数错误").code == ERROR_CODE
    assert ACCESS_TOKEN_INVALID_CODE == 40001
    assert REFRESH_TOKEN_INVALID_CODE == 40002
