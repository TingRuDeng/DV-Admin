import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from scripts.api_contracts import (
    CRITICAL_ENDPOINT_CONTRACTS,
    assert_endpoint_contract_catalog,
    assert_error_envelope,
    assert_success_envelope,
)
from scripts.api_error_codes import (
    ACCESS_TOKEN_INVALID_CODE,
    ERROR_CODE,
    REFRESH_TOKEN_INVALID_CODE,
    SUCCESS_CODE,
    assert_api_error_code_catalog,
)

from drf_admin.utils.middleware import ResponseMiddleware


def build_json_response(data, status_code=status.HTTP_200_OK):
    """构造未经过 Django 渲染链路的 DRF JSON 响应。"""
    response = Response(data, status=status_code)
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    response["Content-Type"] = "application/json"
    return response


@pytest.fixture()
def api_request():
    """提供中间件测试所需的最小请求对象。"""
    return RequestFactory().get("/api/v1/system/users/")


def process_response(response, request):
    """执行 Django 统一响应中间件。"""
    middleware = ResponseMiddleware(lambda req: response)
    return middleware.process_response(request, response)


def test_django_success_response_matches_shared_contract(api_request):
    response = process_response(build_json_response({"id": 1}), api_request)

    assert_success_envelope(response.data, backend="django")
    assert response.data == {
        "msg": "成功",
        "errors": None,
        "code": 20000,
        "data": {"id": 1},
    }


def test_django_error_response_matches_shared_contract(api_request):
    response = process_response(
        build_json_response({"detail": "参数错误"}, status.HTTP_400_BAD_REQUEST),
        api_request,
    )

    assert_error_envelope(response.data, backend="django")
    assert response.data["code"] == 40000
    assert response.data["errors"] == "参数错误"


def test_django_wrapped_response_is_idempotent(api_request):
    wrapped = {"msg": "成功", "errors": None, "code": 20000, "data": {"id": 1}}
    response = process_response(build_json_response(wrapped), api_request)

    assert_success_envelope(response.data, backend="django")
    assert response.data == wrapped


def test_shared_endpoint_contract_catalog_covers_django_system_routes():
    assert_endpoint_contract_catalog()
    contracts = {contract.key: contract for contract in CRITICAL_ENDPOINT_CONTRACTS}

    assert contracts["auth_info"].path == "/api/v1/oauth/info/"
    assert contracts["auth_routes"].path == "/api/v1/oauth/menus/routes/"
    assert contracts["menus_tree"].permissions == ("system:permissions:query",)
    assert contracts["dicts_page"].permissions == ("system:dicts:query",)


def test_shared_api_error_code_catalog_covers_django_response_contracts():
    assert_api_error_code_catalog()

    assert SUCCESS_CODE == 20000
    assert ERROR_CODE == 40000
    assert ACCESS_TOKEN_INVALID_CODE == 40001
    assert REFRESH_TOKEN_INVALID_CODE == 40002
