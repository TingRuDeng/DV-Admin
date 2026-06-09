"""Django 写接口运行时契约抽样测试。"""

from __future__ import annotations

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Permissions, Roles, Users
from drf_admin.utils.runtime_api_contracts.helpers import (
    DEPT_WRITE_SAMPLE_KEYS,
    MENU_WRITE_SAMPLE_KEYS,
    ROLE_WRITE_SAMPLE_KEYS,
    USER_WRITE_SAMPLE_KEYS,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_departments,
    create_runtime_contract_dicts,
    create_runtime_contract_user,
)


class DjangoRuntimeWriteApiContractTestCase(TestCase):
    """Django 关键写端点运行时响应必须满足共享端点目录。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        create_runtime_contract_dicts()
        create_runtime_contract_departments()
        self.client.force_authenticate(user=self.user)

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

    def test_django_menu_write_runtime_samples_match_endpoint_catalog(self):
        """菜单写接口运行时响应必须满足端点目录声明的前端请求契约。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in MENU_WRITE_SAMPLE_KEYS)

        created_menu_id = self.assert_menu_create_contract(contracts["menus_create"])
        self.assert_menu_update_contract(contracts["menus_update"], created_menu_id)
        self.assert_menu_delete_contract(contracts["menus_delete"], created_menu_id)

    def assert_menu_create_contract(self, contract) -> int:
        """验证菜单创建接口成功信封，并返回新菜单 ID。"""
        response = self.client.post(
            contract.path,
            {"name": "运行时 Django 菜单", "type": "MENU", "visible": 1, "sort": 41},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["name"] == "运行时 Django 菜单"
        assert data["type"] == "MENU"
        return data["id"]

    def assert_menu_update_contract(self, contract, menu_id: int) -> None:
        """验证菜单更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(menu_id)),
            {"name": "运行时 Django 菜单已更新", "type": "MENU", "visible": 1, "sort": 42},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["name"] == "运行时 Django 菜单已更新"
        assert data["sort"] == 42

    def assert_menu_delete_contract(self, contract, menu_id: int) -> None:
        """验证菜单删除接口接受共享契约路径参数。"""
        response = self.client.delete(contract.path.replace("{id}", str(menu_id)))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Permissions.objects.filter(id=menu_id).exists()

