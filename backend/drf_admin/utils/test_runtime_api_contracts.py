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
        "system:roles:query",
        "system:roles:add",
        "system:roles:edit",
        "system:roles:delete",
        "system:departments:query",
        "system:departments:add",
        "system:departments:edit",
        "system:departments:delete",
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


def create_runtime_contract_departments() -> Departments:
    """创建部门树查询样本，覆盖 search/status 查询参数契约。"""
    visible = Departments.objects.create(name="运行时契约部门", status=1, sort=1)
    Departments.objects.create(name="运行时过滤部门", status=0, sort=2)
    return visible


class DjangoRuntimeApiContractTestCase(TestCase):
    """Django 关键端点运行时响应必须满足共享端点目录。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        create_runtime_contract_dicts()
        self.department = create_runtime_contract_departments()
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

        depts_data = assert_success_payload(
            self.client.get(
                contracts["depts_tree"].path,
                {"search": self.department.name, "status": self.department.status},
            ),
            contracts["depts_tree"],
        )
        assert len(depts_data) == 1
        assert depts_data[0]["name"] == self.department.name
        assert depts_data[0]["status"] == self.department.status

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

    def test_django_role_write_runtime_samples_match_endpoint_catalog(self):
        """角色写接口运行时响应必须满足端点目录声明的前端请求契约。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in ROLE_WRITE_SAMPLE_KEYS)

        permission = Permissions.objects.create(name="运行时角色权限", type="MENU", perm="runtime:role:assign")
        created_role_id = self.assert_role_create_contract(contracts["roles_create"])
        self.assert_role_update_contract(contracts["roles_update"], created_role_id)
        self.assert_role_menu_assign_contract(contracts, created_role_id, permission.id)
        self.assert_role_delete_contract(contracts["roles_delete"], created_role_id)

    def assert_role_create_contract(self, contract) -> int:
        """验证角色创建接口成功信封，并返回新角色 ID。"""
        response = self.client.post(
            contract.path,
            {
                "name": "运行时 Django 角色",
                "code": "runtime_django_role",
                "status": 1,
                "sort": 20,
                "isDefault": 0,
                "desc": "运行时角色写接口契约",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["name"] == "运行时 Django 角色"
        assert data["code"] == "runtime_django_role"
        return data["id"]

    def assert_role_update_contract(self, contract, role_id: int) -> None:
        """验证角色更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(role_id)),
            {"name": "运行时 Django 角色已更新", "status": 1, "sort": 21},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["name"] == "运行时 Django 角色已更新"
        assert data["sort"] == 21

    def assert_role_menu_assign_contract(self, contracts, role_id: int, permission_id: int) -> None:
        """验证角色权限分配接口接受前端 menuIds 请求体，并真实更新角色权限。"""
        contract = contracts["roles_menu_assign"]
        response = self.client.put(
            contract.path.replace("{id}", str(role_id)),
            {"menuIds": [permission_id]},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data == [permission_id]

        menu_ids_data = assert_success_payload(
            self.client.get(contracts["roles_menu_ids"].path.replace("{id}", str(role_id))),
            contracts["roles_menu_ids"],
        )
        assert menu_ids_data == [permission_id]

    def assert_role_delete_contract(self, contract, role_id: int) -> None:
        """验证角色批量删除接口接受共享契约声明的 ids 请求体。"""
        response = self.client.delete(contract.path, {"ids": [role_id]}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Roles.objects.filter(id=role_id).exists()

    def test_django_dept_write_runtime_samples_match_endpoint_catalog(self):
        """部门写接口运行时响应必须满足端点目录声明的前端请求契约。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in DEPT_WRITE_SAMPLE_KEYS)

        created_dept_id = self.assert_dept_create_contract(contracts["depts_create"])
        self.assert_dept_update_contract(contracts["depts_update"], created_dept_id)
        self.assert_dept_delete_contract(contracts["depts_delete"], created_dept_id)

    def assert_dept_create_contract(self, contract) -> int:
        """验证部门创建接口成功信封，并返回新部门 ID。"""
        response = self.client.post(
            contract.path,
            {"name": "运行时 Django 部门", "status": 1, "sort": 31},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["name"] == "运行时 Django 部门"
        assert data["status"] == 1
        return data["id"]

    def assert_dept_update_contract(self, contract, dept_id: int) -> None:
        """验证部门更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(dept_id)),
            {"name": "运行时 Django 部门已更新", "status": 1, "sort": 32},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["name"] == "运行时 Django 部门已更新"
        assert data["sort"] == 32

    def assert_dept_delete_contract(self, contract, dept_id: int) -> None:
        """验证部门批量删除接口接受共享契约声明的 ids 请求体。"""
        response = self.client.delete(contract.path, {"ids": [dept_id]}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Departments.objects.filter(id=dept_id).exists()
