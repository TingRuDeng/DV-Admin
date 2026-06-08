"""基于关键端点目录的 Django 运行时契约抽样测试。"""

from typing import Any, Mapping

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from scripts.api_contracts import (
    assert_page_payload,
    assert_success_envelope,
    iter_critical_endpoint_contracts,
)

from drf_admin.apps.system.models import DictItems, Dicts, Permissions, Roles, Users

HTTP_OK = status.HTTP_200_OK
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
    if "page" in contract.query_params:
        params["page"] = 1
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
        "system:permissions:query",
        "system:dicts:query",
        "system:dictitems:query",
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
    menu = Permissions.objects.create(
        name="契约菜单",
        perm="runtime:menu",
        type="MENU",
        route_name="RuntimeContractUser",
        route_path="user",
        component="system/user/index",
        parent=catalog,
        sort=2,
    )
    return [catalog, menu, *buttons]


def create_runtime_contract_dicts() -> None:
    """创建字典和字典项列表数据，覆盖分页与 dictCode 查询参数契约。"""
    dict_data = Dicts.objects.create(dict_code="runtime_contract", name="运行时契约字典")
    extra_dict = Dicts.objects.create(dict_code="runtime_contract_extra", name="运行时契约分页字典")
    DictItems.objects.create(dict=dict_data, label="启用", value="enabled", status=1)
    DictItems.objects.create(dict=dict_data, label="禁用", value="disabled", status=1)
    DictItems.objects.create(dict=extra_dict, label="其他", value="other", status=1)


class DjangoRuntimeApiContractTestCase(TestCase):
    """Django 关键端点运行时响应必须满足共享端点目录。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        create_runtime_contract_dicts()
        self.client.force_authenticate(user=self.user)

    def test_django_read_runtime_samples_match_endpoint_catalog(self):
        """关键读接口运行时响应必须满足端点目录声明的信封、分页和字段契约。"""
        contracts = contracts_by_key()
        for key in READ_SAMPLE_KEYS:
            contract = contracts[key]
            response = self.client.get(contract.path, sample_query_params(contract))
            data = assert_success_payload(response, contract)
            assert_response_fields(data, contract.response_fields)

        users_data = assert_success_payload(
            self.client.get(
                contracts["users_page"].path,
                {"page": 1, "pageSize": PAGE_SIZE_SAMPLE},
            ),
            contracts["users_page"],
        )
        assert len(users_data["list"]) == PAGE_SIZE_SAMPLE

    def test_django_dict_items_runtime_sample_filters_by_frontend_dict_code(self):
        """字典项列表必须按前端 `dictCode` 参数过滤，避免跨后端查询语义漂移。"""
        contract = contracts_by_key()["dict_items_page"]
        data = assert_success_payload(
            self.client.get(
                contract.path,
                {"page": 1, "pageSize": 10, "dictCode": "runtime_contract"},
            ),
            contract,
        )

        values = {item["value"] for item in data["list"]}
        assert data["total"] == 2
        assert values == {"enabled", "disabled"}

    def test_django_user_write_runtime_samples_match_endpoint_catalog(self):
        """用户写接口运行时响应必须满足端点目录声明的路径、方法和请求体契约。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in USER_WRITE_SAMPLE_KEYS)

        created_user_id = self.assert_user_create_contract(contracts["users_create"])
        self.assert_user_update_contract(contracts["users_update"], created_user_id)
        self.assert_user_delete_contract(contracts["users_delete"], created_user_id)

    def assert_user_create_contract(self, contract) -> int:
        """验证用户创建接口成功信封，并返回新用户 ID。"""
        response = self.client.post(
            contract.path,
            {"username": "runtime-writer", "password": "testpass123", "name": "运行时写入用户"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["username"] == "runtime-writer"
        assert Users.objects.filter(id=data["id"]).exists()
        return data["id"]

    def assert_user_update_contract(self, contract, user_id: int) -> None:
        """验证用户更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(user_id)),
            {"username": "runtime-writer", "name": "运行时写入用户已更新"},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["name"] == "运行时写入用户已更新"
        assert Users.objects.get(id=user_id).name == "运行时写入用户已更新"

    def assert_user_delete_contract(self, contract, user_id: int) -> None:
        """验证用户批量删除接口接受共享契约声明的 ids 请求体。"""
        response = self.client.delete(contract.path, {"ids": [user_id]}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Users.objects.filter(id=user_id).exists()
