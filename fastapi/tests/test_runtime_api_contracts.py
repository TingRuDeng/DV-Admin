"""基于关键端点目录的 FastAPI 运行时契约抽样测试。"""

import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Mapping

import pytest_asyncio
from scripts.api_contracts import (
    assert_page_payload,
    assert_success_envelope,
    iter_critical_endpoint_contracts,
)

from app.db.models.system import Departments, OperationLog, Permissions, Roles

HTTP_OK = 200
PAGE_SIZE_SAMPLE = 1
READ_SAMPLE_KEYS = (
    "auth_info",
    "auth_routes",
    "users_page",
    "roles_page",
    "depts_tree",
    "menus_tree",
    "dicts_page",
    "dict_items_page",
    "notices_page",
    "logs_page",
)
USER_WRITE_SAMPLE_KEYS = ("users_create", "users_update", "users_delete")
ROLE_WRITE_SAMPLE_KEYS = ("roles_create", "roles_update", "roles_delete", "roles_menu_assign")
DEPT_WRITE_SAMPLE_KEYS = ("depts_create", "depts_update", "depts_delete")


@dataclass(frozen=True)
class UserWriteContext:
    """用户写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]
    role_id: int
    role_name: str
    dept_id: int


@dataclass(frozen=True)
class RoleWriteContext:
    """角色写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]
    permission_id: int


@dataclass(frozen=True)
class DeptWriteContext:
    """部门写接口运行时契约所需上下文。"""

    client: Any
    contracts: dict[str, Any]


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


@pytest_asyncio.fixture
async def runtime_contract_logs(db):
    """创建运行时日志样本，用于证明日志分页参数真实生效。"""
    logs = []
    for index in range(2):
        log = await OperationLog.create(
            user_id=1,
            username=f"runtime_log_user_{index}",
            name=f"运行时日志用户{index}",
            operation=f"运行时日志操作{index}",
            method="GET",
            path=f"/api/v1/runtime/logs/{index}",
            status=1,
            execution_time=100 + index,
        )
        logs.append(log)
    return logs


@pytest_asyncio.fixture
async def runtime_contract_roles(db):
    """创建运行时角色样本，用于证明角色分页参数真实生效。"""
    roles = []
    role_suffix = uuid.uuid4().hex[:6]
    for index in range(2):
        role = await Roles.create(
            name=f"运行时角色{index}_{role_suffix}",
            code=f"runtime_role_{index}_{role_suffix}",
            status=1,
            sort=index + 10,
        )
        roles.append(role)
    return roles


@pytest_asyncio.fixture
async def runtime_contract_departments(db):
    """创建运行时部门样本，用于证明部门树查询参数真实生效。"""
    suffix = uuid.uuid4().hex[:6]
    visible = await Departments.create(name=f"运行时契约部门_{suffix}", status=1, sort=1)
    await Departments.create(name=f"运行时过滤部门_{suffix}", status=0, sort=2)
    return visible


@pytest_asyncio.fixture
async def runtime_contract_permission(db):
    """创建运行时权限样本，用于证明角色权限分配真实落库。"""
    suffix = uuid.uuid4().hex[:6]
    return await Permissions.create(
        name=f"运行时角色权限_{suffix}",
        type="MENU",
        perm=f"runtime:role:{suffix}",
        sort=30,
    )


def test_fastapi_read_runtime_samples_match_endpoint_catalog(
    auth_client, test_user, runtime_contract_logs, runtime_contract_roles, runtime_contract_departments
):
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

    roles_data = assert_success_payload(
        auth_client.get(contracts["roles_page"].path, params={"page": 1, "pageSize": PAGE_SIZE_SAMPLE}),
        contracts["roles_page"],
    )
    assert len(roles_data["list"]) == PAGE_SIZE_SAMPLE

    depts_data = assert_success_payload(
        auth_client.get(
            contracts["depts_tree"].path,
            params={"search": runtime_contract_departments.name, "status": runtime_contract_departments.status},
        ),
        contracts["depts_tree"],
    )
    assert len(depts_data) == 1
    assert depts_data[0]["name"] == runtime_contract_departments.name
    assert depts_data[0]["status"] == runtime_contract_departments.status

    logs_data = assert_success_payload(
        auth_client.get(contracts["logs_page"].path, params={"page": 1, "pageSize": PAGE_SIZE_SAMPLE}),
        contracts["logs_page"],
    )
    assert len(logs_data["list"]) == PAGE_SIZE_SAMPLE
    assert_log_row_matches_frontend_contract(logs_data["list"][0])


def assert_log_row_matches_frontend_contract(log: Mapping[str, Any]) -> None:
    """验证日志行字段使用前端真实依赖的 camelCase 响应契约。"""
    assert log["username"].startswith("runtime_log_user_")
    assert log["operation"].startswith("运行时日志操作")
    assert log["path"].startswith("/api/v1/runtime/logs/")
    assert "createdAt" in log


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


def test_fastapi_role_write_runtime_samples_match_endpoint_catalog(auth_client, runtime_contract_permission):
    """角色写接口运行时响应必须满足端点目录声明的前端请求契约。"""
    context = RoleWriteContext(
        client=auth_client,
        contracts=contracts_by_key(),
        permission_id=runtime_contract_permission.id,
    )
    assert all(key in context.contracts for key in ROLE_WRITE_SAMPLE_KEYS)

    created_role_id = assert_role_create_contract(context)
    assert_role_update_contract(context, created_role_id)
    assert_role_menu_assign_contract(context, created_role_id)
    assert_role_delete_contract(context, created_role_id)


def test_fastapi_dept_write_runtime_samples_match_endpoint_catalog(auth_client):
    """部门写接口运行时响应必须满足端点目录声明的前端请求契约。"""
    context = DeptWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in DEPT_WRITE_SAMPLE_KEYS)

    created_dept_id = assert_dept_create_contract(context)
    assert_dept_update_contract(context, created_dept_id)
    assert_dept_delete_contract(context, created_dept_id)


def assert_dept_create_contract(context: DeptWriteContext) -> int:
    """验证部门创建接口接受前端部门表单请求体，并返回成功信封。"""
    contract = context.contracts["depts_create"]
    response = context.client.post(
        contract.path,
        json={"name": "运行时 FastAPI 部门", "status": 1, "sort": 31},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 部门"
    assert data["status"] == 1
    return data["id"]


def assert_dept_update_contract(context: DeptWriteContext, dept_id: int) -> None:
    """验证部门更新接口接受共享契约路径，并返回更新后的关键字段。"""
    contract = context.contracts["depts_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(dept_id)),
        json={"name": "运行时 FastAPI 部门已更新", "status": 1, "sort": 32},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 部门已更新"
    assert data["sort"] == 32


def assert_dept_delete_contract(context: DeptWriteContext, dept_id: int) -> None:
    """验证部门批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["depts_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [dept_id]})
    assert_success_payload(response, contract)


def assert_role_create_contract(context: RoleWriteContext) -> int:
    """验证角色创建接口接受前端角色表单请求体，并返回成功信封。"""
    contract = context.contracts["roles_create"]
    response = context.client.post(
        contract.path,
        json={
            "name": "运行时 FastAPI 角色",
            "code": "runtime_fastapi_role",
            "status": 1,
            "sort": 20,
            "isDefault": 0,
            "desc": "运行时角色写接口契约",
        },
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 角色"
    assert data["code"] == "runtime_fastapi_role"
    return data["id"]


def assert_role_update_contract(context: RoleWriteContext, role_id: int) -> None:
    """验证角色更新接口接受共享契约路径，并返回更新后的关键字段。"""
    contract = context.contracts["roles_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(role_id)),
        json={"name": "运行时 FastAPI 角色已更新", "status": 1, "sort": 21},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 角色已更新"
    assert data["sort"] == 21


def assert_role_menu_assign_contract(context: RoleWriteContext, role_id: int) -> None:
    """验证角色权限分配接口接受前端 menuIds 请求体，并真实更新角色权限。"""
    contract = context.contracts["roles_menu_assign"]
    response = context.client.put(
        contract.path.replace("{id}", str(role_id)),
        json={"menuIds": [context.permission_id]},
    )
    data = assert_success_payload(response, contract)
    assert data == [context.permission_id]

    menu_ids_data = assert_success_payload(
        context.client.get(context.contracts["roles_menu_ids"].path.replace("{id}", str(role_id))),
        context.contracts["roles_menu_ids"],
    )
    assert menu_ids_data == [context.permission_id]


def assert_role_delete_contract(context: RoleWriteContext, role_id: int) -> None:
    """验证角色批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["roles_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [role_id]})
    assert_success_payload(response, contract)


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
