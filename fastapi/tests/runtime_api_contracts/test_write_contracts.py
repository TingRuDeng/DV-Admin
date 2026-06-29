"""FastAPI 写接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid

import pytest_asyncio
from runtime_api_contracts.helpers import (
    DEPT_WRITE_SAMPLE_KEYS,
    MENU_WRITE_SAMPLE_KEYS,
    ROLE_WRITE_SAMPLE_KEYS,
    USER_WRITE_SAMPLE_KEYS,
    RoleWriteContext,
    SimpleWriteContext,
    UserWriteContext,
    assert_success_payload,
    contracts_by_key,
)

from app.db.models.system import Permissions


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
    context = SimpleWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in DEPT_WRITE_SAMPLE_KEYS)

    created_dept_id = assert_dept_create_contract(context)
    assert_dept_update_contract(context, created_dept_id)
    assert_dept_delete_contract(context, created_dept_id)


def test_fastapi_menu_write_runtime_samples_match_endpoint_catalog(auth_client):
    """菜单写接口运行时响应必须满足端点目录声明的前端请求契约。"""
    context = SimpleWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in MENU_WRITE_SAMPLE_KEYS)

    created_menu_id = assert_menu_create_contract(context)
    assert_menu_update_contract(context, created_menu_id)
    assert_menu_delete_contract(context, created_menu_id)


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
        json={"name": "FastAPI 写入用户已更新", "deptId": context.dept_id, "roles": [context.role_id]},
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
        context.client.get(context.contracts["users_page"].path, params={"pageNum": 1, "pageSize": 100}),
        context.contracts["users_page"],
    )
    usernames = {user["username"] for user in users_data["list"]}
    assert "runtime-fastapi-writer" not in usernames


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


def assert_dept_create_contract(context: SimpleWriteContext) -> int:
    """验证部门创建接口接受前端部门表单请求体，并返回成功信封。"""
    contract = context.contracts["depts_create"]
    response = context.client.post(contract.path, json={"name": "运行时 FastAPI 部门", "status": 1, "sort": 31})
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 部门"
    assert data["status"] == 1
    return data["id"]


def assert_dept_update_contract(context: SimpleWriteContext, dept_id: int) -> None:
    """验证部门更新接口接受共享契约路径，并返回更新后的关键字段。"""
    contract = context.contracts["depts_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(dept_id)),
        json={"name": "运行时 FastAPI 部门已更新", "status": 1, "sort": 32},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 部门已更新"
    assert data["sort"] == 32


def assert_dept_delete_contract(context: SimpleWriteContext, dept_id: int) -> None:
    """验证部门批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["depts_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [dept_id]})
    assert_success_payload(response, contract)


def assert_menu_create_contract(context: SimpleWriteContext) -> int:
    """验证菜单创建接口接受前端菜单表单请求体，并返回成功信封。"""
    contract = context.contracts["menus_create"]
    response = context.client.post(
        contract.path,
        json={"name": "运行时 FastAPI 菜单", "type": "MENU", "visible": 1, "sort": 41},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 菜单"
    assert data["type"] == "MENU"
    return data["id"]


def assert_menu_update_contract(context: SimpleWriteContext, menu_id: int) -> None:
    """验证菜单更新接口接受共享契约路径，并返回更新后的关键字段。"""
    contract = context.contracts["menus_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(menu_id)),
        json={"name": "运行时 FastAPI 菜单已更新", "type": "MENU", "visible": 1, "sort": 42},
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 菜单已更新"
    assert data["sort"] == 42


def assert_menu_delete_contract(context: SimpleWriteContext, menu_id: int) -> None:
    """验证菜单删除接口接受共享契约路径参数。"""
    contract = context.contracts["menus_delete"]
    response = context.client.delete(contract.path.replace("{id}", str(menu_id)))
    assert_success_payload(response, contract)
