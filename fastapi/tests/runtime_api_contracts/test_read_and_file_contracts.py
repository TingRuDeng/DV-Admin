"""FastAPI 读接口与文件接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path
from typing import Any, Mapping

import pytest_asyncio
from runtime_api_contracts.helpers import (
    PAGE_SIZE_SAMPLE,
    READ_SAMPLE_KEYS,
    assert_response_fields,
    assert_success_payload,
    contracts_by_key,
    sample_query_params,
)

from app.db.models.system import Departments, OperationLog, Roles


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


def test_fastapi_read_runtime_samples_match_endpoint_catalog(
    auth_client,
    test_user,
    runtime_contract_logs,
    runtime_contract_roles,
    runtime_contract_departments,
):
    """关键读接口运行时响应必须满足端点目录声明的信封、分页和字段契约。"""
    contracts = contracts_by_key()
    for key in READ_SAMPLE_KEYS:
        contract = contracts[key]
        response = auth_client.get(contract.path, params=sample_query_params(contract))
        data = assert_success_payload(response, contract)
        assert_response_fields(data, contract.response_fields)

    assert_page_size(auth_client, contracts, "users_page")
    assert_page_size(auth_client, contracts, "roles_page")
    assert_dept_filter(auth_client, contracts, runtime_contract_departments)
    assert_log_page(auth_client, contracts)


def test_fastapi_page_num_reaches_second_page(
    auth_client,
    runtime_contract_logs,
    runtime_contract_roles,
    runtime_contract_page_samples,
):
    """分页接口必须使用前端真实发送的 pageNum 参数访问第二页。"""
    contracts = contracts_by_key()
    suffix = runtime_contract_page_samples["suffix"]

    assert_second_page_item(
        auth_client,
        contracts,
        "users_page",
        {"pageNum": 2, "pageSize": 1, "search": suffix},
        "username",
        runtime_contract_page_samples["users"][1].username,
    )
    assert_second_page_item(
        auth_client,
        contracts,
        "roles_page",
        {"pageNum": 2, "pageSize": 1, "search": "运行时角色"},
        "id",
        runtime_contract_roles[1].id,
    )
    assert_second_page_item(
        auth_client,
        contracts,
        "dicts_page",
        {"pageNum": 2, "pageSize": 1, "search": runtime_contract_page_samples["dict_suffix"]},
        "dictCode",
        runtime_contract_page_samples["dicts"][0].dict_code,
    )
    assert_second_page_item(
        auth_client,
        contracts,
        "dict_items_page",
        {
            "pageNum": 2,
            "pageSize": 1,
            "dictCode": runtime_contract_page_samples["item_dict_code"],
        },
        "value",
        runtime_contract_page_samples["dict_items"][1].value,
    )
    assert_second_page_item(
        auth_client,
        contracts,
        "notices_page",
        {"pageNum": 2, "pageSize": 1, "title": runtime_contract_page_samples["notice_suffix"]},
        "id",
        runtime_contract_page_samples["notices"][0].id,
    )
    assert_second_page_item(
        auth_client,
        contracts,
        "logs_page",
        {"pageNum": 2, "pageSize": 1, "operation": "运行时日志操作"},
        "id",
        runtime_contract_logs[0].id,
    )


def assert_page_size(auth_client, contracts: dict[str, Any], key: str) -> None:
    """验证分页接口真实使用 pageSize 参数。"""
    data = assert_success_payload(
        auth_client.get(contracts[key].path, params={"pageNum": 1, "pageSize": PAGE_SIZE_SAMPLE}),
        contracts[key],
    )
    assert len(data["list"]) == PAGE_SIZE_SAMPLE


def assert_second_page_item(
    auth_client,
    contracts: dict[str, Any],
    key: str,
    params: dict[str, Any],
    field: str,
    expected_value: Any,
) -> None:
    """验证 pageNum 能驱动接口返回第二页数据。"""
    data = assert_success_payload(
        auth_client.get(contracts[key].path, params=params),
        contracts[key],
    )
    assert data["total"] >= 2
    assert len(data["list"]) == 1
    assert data["list"][0][field] == expected_value


def assert_dept_filter(auth_client, contracts: dict[str, Any], department) -> None:
    """验证部门树真实使用前端查询参数。"""
    data = assert_success_payload(
        auth_client.get(
            contracts["depts_tree"].path,
            params={"search": department.name, "status": department.status},
        ),
        contracts["depts_tree"],
    )
    assert len(data) == 1
    assert data[0]["name"] == department.name
    assert data[0]["status"] == department.status


def assert_log_page(auth_client, contracts: dict[str, Any]) -> None:
    """验证日志分页字段使用前端真实依赖的 camelCase 响应契约。"""
    data = assert_success_payload(
        auth_client.get(contracts["logs_page"].path, params={"pageNum": 1, "pageSize": PAGE_SIZE_SAMPLE}),
        contracts["logs_page"],
    )
    assert len(data["list"]) == PAGE_SIZE_SAMPLE
    assert_log_row_matches_frontend_contract(data["list"][0])


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
