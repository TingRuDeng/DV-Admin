"""基于关键端点目录的 FastAPI 运行时契约抽样测试。"""

from io import BytesIO
from pathlib import Path
from typing import Any, Mapping

from scripts.api_contracts import (
    assert_page_payload,
    assert_success_envelope,
    iter_critical_endpoint_contracts,
)

HTTP_OK = 200
PAGE_SIZE_SAMPLE = 1
READ_SAMPLE_KEYS = (
    "auth_info",
    "auth_routes",
    "users_page",
    "menus_tree",
    "dicts_page",
    "dict_items_page",
)


def contracts_by_key() -> dict[str, Any]:
    """按 key 索引关键端点契约，避免测试重复维护端点清单细节。"""
    return {contract.key: contract for contract in iter_critical_endpoint_contracts()}


def assert_success_payload(response, contract) -> Any:
    """断言运行时响应满足 FastAPI 成功信封，并返回 data 载荷。"""
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert_success_envelope(payload, backend="fastapi")
    data = payload["data"]
    if contract.paginated:
        assert_page_payload(data)
    return data


def assert_response_fields(data: Any, fields: tuple[str, ...]) -> None:
    """抽样检查响应关键字段，空列表仅验证外层结构。"""
    if isinstance(data, Mapping):
        for field in fields:
            assert field in data
        return
    if isinstance(data, list) and data:
        for field in fields:
            assert field in data[0]


def sample_query_params(contract) -> dict[str, Any]:
    """按前端共享契约构造查询参数，避免误用后端私有参数名。"""
    params: dict[str, Any] = {}
    if "page" in contract.query_params:
        params["page"] = 1
    if "pageSize" in contract.query_params:
        params["pageSize"] = PAGE_SIZE_SAMPLE
    return params


def test_fastapi_read_runtime_samples_match_endpoint_catalog(auth_client, test_user):
    """关键读接口运行时响应必须满足端点目录声明的信封、分页和字段契约。"""
    contracts = contracts_by_key()
    for key in READ_SAMPLE_KEYS:
        contract = contracts[key]
        response = auth_client.get(contract.path, params=sample_query_params(contract))
        data = assert_success_payload(response, contract)
        assert_response_fields(data, contract.response_fields)

    users_data = assert_success_payload(
        auth_client.get(contracts["users_page"].path, params={"page": 1, "pageSize": PAGE_SIZE_SAMPLE}),
        contracts["users_page"],
    )
    assert len(users_data["list"]) == PAGE_SIZE_SAMPLE


def test_fastapi_file_runtime_sample_matches_endpoint_catalog(
    auth_client,
    test_user_with_role,
    tmp_path: Path,
    monkeypatch,
):
    """文件上传和删除运行时闭环必须遵守目录中的 path 字段和 filePath 参数契约。"""
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    contracts = contracts_by_key()

    files = {"file": ("runtime-contract.txt", BytesIO(b"runtime contract"), "text/plain")}
    upload_data = assert_success_payload(
        auth_client.post(contracts["files_upload"].path, files=files),
        contracts["files_upload"],
    )
    assert_response_fields(upload_data, contracts["files_upload"].response_fields)
    assert upload_data["path"].startswith(f"files/{test_user_with_role['id']}/")

    uploaded_file = tmp_path / upload_data["path"]
    assert uploaded_file.exists()

    delete_response = auth_client.delete(
        contracts["files_delete"].path,
        params={"filePath": upload_data["path"]},
    )
    assert_success_payload(delete_response, contracts["files_delete"])
    assert not uploaded_file.exists()
