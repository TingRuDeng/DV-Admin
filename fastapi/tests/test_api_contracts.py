from scripts.api_contracts import (
    assert_error_envelope,
    assert_page_payload,
    assert_success_envelope,
    normalize_api_envelope,
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
