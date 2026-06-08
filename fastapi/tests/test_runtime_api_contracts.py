"""基于关键端点目录的 FastAPI 运行时契约抽样测试。"""

from dataclasses import dataclass
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
USER_WRITE_SAMPLE_KEYS = ("users_create", "users_update", "users_delete")


@dataclass(frozen=True)
class UserWriteContext:
    """用户写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]
    role_id: int
    role_name: str
    dept_id: int


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


def test_fastapi_user_write_runtime_samples_match_endpoint_catalog(auth_client, test_role, test_dept):
    """用户写接口运行时响应必须满足端点目录声明的路径、方法和请求体契约。"""
    context = UserWriteContext(
        client=auth_client,
        contracts=contracts_by_key(),
        role_id=test_role["id"],
        role_name=test_role["name"],
        dept_id=test_dept["id"],
    )
    assert all(key in context.contracts for key in USER_WRITE_SAMPLE_KEYS)

    created_user_id = assert_user_create_contract(context)
    assert_user_update_contract(context, created_user_id)
    assert_user_delete_contract(context, created_user_id)


def assert_user_create_contract(context: UserWriteContext) -> int:
    """验证用户创建接口接受前端契约请求体，并返回成功信封。"""
    contract = context.contracts["users_create"]
    response = context.client.post(
        contract.path,
        json={
            "username": "runtime-fastapi-writer",
            "password": "testpass123",
            "name": "FastAPI 写入用户",
            "email": "runtime-fastapi-writer@example.com",
            "mobile": "13800139999",
            "deptId": context.dept_id,
            "roles": [context.role_id],
        },
    )
    data = assert_success_payload(response, contract)
    assert data["username"] == "runtime-fastapi-writer"
    assert data["deptId"] == context.dept_id
    assert data["roleNames"] == context.role_name
    return data["id"]


def assert_user_update_contract(context: UserWriteContext, user_id: int) -> None:
    """验证用户更新接口接受共享契约路径，并返回更新后的关键字段。"""
    contract = context.contracts["users_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(user_id)),
        json={
            "name": "FastAPI 写入用户已更新",
            "deptId": context.dept_id,
            "roles": [context.role_id],
        },
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "FastAPI 写入用户已更新"
    assert data["deptId"] == context.dept_id


def assert_user_delete_contract(context: UserWriteContext, user_id: int) -> None:
    """验证用户批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["users_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [user_id]})
    assert_success_payload(response, contract)

    users_data = assert_success_payload(
        context.client.get(context.contracts["users_page"].path, params={"page": 1, "pageSize": 100}),
        context.contracts["users_page"],
    )
    usernames = {user["username"] for user in users_data["list"]}
    assert "runtime-fastapi-writer" not in usernames
