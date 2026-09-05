"""Django 运行时 API 契约测试共享工具。"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Mapping

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from scripts.api_contracts import (
    assert_page_payload,
    assert_success_envelope,
    iter_critical_endpoint_contracts,
)

from drf_admin.apps.system.models import Departments, DictItems, Dicts, Permissions, Roles, Users

HTTP_OK = status.HTTP_200_OK
PAGE_SIZE_SAMPLE = 1
READ_SAMPLE_KEYS = (
    "auth_info",
    "auth_routes",
    "users_page",
    "depts_tree",
    "menus_tree",
    "dicts_page",
    "dict_items_page",
)
USER_WRITE_SAMPLE_KEYS = ("users_create", "users_update", "users_delete")
ROLE_WRITE_SAMPLE_KEYS = ("roles_create", "roles_update", "roles_delete", "roles_menu_assign")
DEPT_WRITE_SAMPLE_KEYS = ("depts_create", "depts_update", "depts_delete")
MENU_WRITE_SAMPLE_KEYS = ("menus_create", "menus_update", "menus_delete")
DICT_WRITE_SAMPLE_KEYS = ("dicts_create", "dicts_update", "dicts_delete")
DICT_ITEM_WRITE_SAMPLE_KEYS = ("dict_items_create", "dict_items_update", "dict_items_delete")
NOTICE_WRITE_SAMPLE_KEYS = (
    "notices_create",
    "notices_update",
    "notices_delete",
    "notices_publish",
    "notices_revoke",
)
LOG_DELETE_REQUEST_ID = "real-backend-log-delete"
LOG_KEEP_REQUEST_ID = "real-backend-log-keep"
LOG_CLEAR_REQUEST_ID = "real-backend-log-clear"


def contracts_by_key() -> dict[str, Any]:
    """按 key 索引关键端点契约，避免测试重复维护端点清单细节。"""
    return {contract.key: contract for contract in iter_critical_endpoint_contracts()}


def assert_success_payload(response, contract, expected_status=HTTP_OK) -> Any:
    """断言运行时响应满足 Django 成功信封，并返回 data 载荷。"""
    assert response.status_code == expected_status
    payload = response.json()
    assert_success_envelope(payload, backend="django")
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
    if "pageNum" in contract.query_params:
        params["pageNum"] = 1
    if "pageSize" in contract.query_params:
        params["pageSize"] = PAGE_SIZE_SAMPLE
    if "dictCode" in contract.query_params:
        params["dictCode"] = "runtime_contract"
    return params


def create_runtime_contract_user() -> Users:
    """创建覆盖运行时契约所需权限、菜单和列表数据的 Django 用户。"""
    role = Roles.objects.create(name="运行时契约角色", code="runtime-contract", status=1, sort=1)
    role.permissions.add(*create_runtime_contract_permissions())
    user = Users.objects.create_user(
        username="runtime-admin",
        password="testpass123",
        name="运行时契约管理员",
        is_active=1,
    )
    user.roles.add(role)
    cache.delete(f"user_info_{user.id}_perms")
    Users.objects.create_user(
        username="runtime-extra",
        password="testpass123",
        name="运行时契约分页用户",
        is_active=1,
    )
    return user


def create_runtime_contract_permissions() -> list[Permissions]:
    """创建按钮权限和菜单层级，覆盖授权接口与动态路由字段契约。"""
    button_codes = [
        "system:users:query",
        "system:users:add",
        "system:users:edit",
        "system:users:delete",
        "system:users:password:reset",
        "system:users:import",
        "system:users:export",
        "system:roles:query",
        "system:roles:add",
        "system:roles:edit",
        "system:roles:delete",
        "system:departments:query",
        "system:departments:add",
        "system:departments:edit",
        "system:departments:delete",
        "system:permissions:query",
        "system:permissions:add",
        "system:permissions:edit",
        "system:permissions:delete",
        "system:dicts:query",
        "system:dicts:add",
        "system:dicts:edit",
        "system:dicts:delete",
        "system:dictitems:query",
        "system:dictitems:add",
        "system:dictitems:edit",
        "system:dictitems:delete",
        "system:notices:query",
        "system:notices:add",
        "system:notices:edit",
        "system:notices:delete",
        "system:notices:publish",
        "system:notices:revoke",
        "system:logs:query",
        "system:logs:delete",
    ]
    buttons = [
        Permissions.objects.create(name=code, perm=code, type="BUTTON", sort=index)
        for index, code in enumerate(button_codes, start=10)
    ]
    catalog = Permissions.objects.create(
        name="契约目录",
        perm="runtime:catalog",
        type="CATALOG",
        route_name="RuntimeContract",
        route_path="/runtime-contract",
        component="Layout",
        sort=1,
    )
    user_menu = Permissions.objects.create(
        name="用户管理",
        perm="runtime:menu",
        type="MENU",
        route_name="RuntimeContractUser",
        route_path="user",
        component="system/user/index",
        parent=catalog,
        sort=2,
    )
    notice_menu = Permissions.objects.create(
        name="通知公告",
        perm="runtime:notice:menu",
        type="MENU",
        route_name="RuntimeContractNotice",
        route_path="notices",
        component="system/notice/index",
        parent=catalog,
        sort=3,
    )
    log_menu = Permissions.objects.create(
        name="日志管理",
        perm="system:logs:query",
        type="MENU",
        route_name="RuntimeContractLog",
        route_path="log",
        component="system/log/index",
        parent=catalog,
        sort=4,
    )
    menu_management = Permissions.objects.create(
        name="菜单管理",
        perm="system:permissions:query",
        type="MENU",
        route_name="RuntimeContractMenus",
        route_path="menus",
        component="system/menu/index",
        parent=catalog,
        sort=5,
    )
    upload_menu = Permissions.objects.create(
        name="文件上传",
        perm="demo:upload:query",
        type="MENU",
        route_name="RuntimeContractUpload",
        route_path="upload",
        component="demo/upload",
        parent=catalog,
        sort=6,
    )
    return [catalog, user_menu, notice_menu, log_menu, menu_management, upload_menu, *buttons]


def create_runtime_contract_dicts() -> None:
    """创建字典和字典项列表数据，覆盖分页与 dictCode 查询参数契约。"""
    dict_data = Dicts.objects.create(dict_code="runtime_contract", name="运行时契约字典")
    extra_dict = Dicts.objects.create(dict_code="runtime_contract_extra", name="运行时契约分页字典")
    DictItems.objects.create(dict=dict_data, label="启用", value="enabled", status=1)
    DictItems.objects.create(dict=dict_data, label="禁用", value="disabled", status=1)
    DictItems.objects.create(dict=extra_dict, label="其他", value="other", status=1)


def create_runtime_contract_departments() -> Departments:
    """创建部门树查询样本，覆盖 search/status 查询参数契约。"""
    visible = Departments.objects.create(name="运行时契约部门", status=1, sort=1)
    Departments.objects.create(name="运行时过滤部门", status=0, sort=2)
    return visible


def create_runtime_contract_logs(user_id: int, username: str, name: str) -> None:
    """创建日志页真实烟雾所需的最近、保留和待清理样本。"""
    from drf_admin.apps.system.models import OperationLog

    OperationLog.objects.create(
        user_id=user_id,
        username=username,
        name=name,
        operation="真实浏览器日志删除目标",
        method="DELETE",
        path="/api/v1/runtime-contract/logs/delete-target",
        request_id=LOG_DELETE_REQUEST_ID,
        request_body='{"password":"delete-secret"}',
        response_status=200,
        response_body='{"token":"delete-response-secret"}',
        ip="10.0.0.10",
        browser="Chromium",
        os="macOS",
        execution_time=18,
        status=1,
    )
    OperationLog.objects.create(
        user_id=user_id,
        username=username,
        name=name,
        operation="真实浏览器日志保留目标",
        method="POST",
        path="/api/v1/runtime-contract/logs/keep-target",
        request_id=LOG_KEEP_REQUEST_ID,
        request_body='{"status":"keep"}',
        response_status=200,
        response_body='{"ok":true}',
        ip="10.0.0.11",
        browser="Chromium",
        os="macOS",
        execution_time=12,
        status=1,
    )
    old_log = OperationLog.objects.create(
        user_id=user_id,
        username=username,
        name=name,
        operation="真实浏览器日志清理目标",
        method="POST",
        path="/api/v1/runtime-contract/logs/clear-target",
        request_id=LOG_CLEAR_REQUEST_ID,
        request_body='{"password":"clear-secret"}',
        response_status=500,
        response_body='{"token":"clear-response-secret"}',
        ip="10.0.0.12",
        browser="Chromium",
        os="macOS",
        execution_time=21,
        status=0,
        error_msg="清理前历史样本",
    )
    old_created_at = timezone.now() - timedelta(days=10)
    OperationLog.objects.filter(id=old_log.id).update(
        created_at=old_created_at,
        updated_at=old_created_at,
    )
