"""Django 字典写接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import DictItems, Dicts
from drf_admin.utils.runtime_api_contracts.helpers import (
    DICT_ITEM_WRITE_SAMPLE_KEYS,
    DICT_WRITE_SAMPLE_KEYS,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_user,
)


class DjangoRuntimeDictWriteApiContractTestCase(TestCase):
    """Django 字典写端点运行时响应必须满足共享端点目录。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        self.client.force_authenticate(user=self.user)

    def test_django_dict_write_runtime_samples_match_endpoint_catalog(self):
        """字典写接口必须接受前端字段，并满足共享端点目录。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in DICT_WRITE_SAMPLE_KEYS)

        dict_id = self.assert_dict_create_contract(contracts["dicts_create"])
        self.assert_dict_update_contract(contracts["dicts_update"], dict_id)
        self.assert_dict_delete_contract(contracts["dicts_delete"], dict_id)

    def test_django_dict_item_write_runtime_samples_match_endpoint_catalog(self):
        """字典项写接口必须接受前端字段，并满足共享端点目录。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in DICT_ITEM_WRITE_SAMPLE_KEYS)

        dict_id = self.assert_dict_create_contract(contracts["dicts_create"])
        item_id = self.assert_dict_item_create_contract(contracts["dict_items_create"], dict_id)
        self.assert_dict_item_update_contract(contracts["dict_items_update"], item_id, dict_id)
        self.assert_dict_item_delete_contract(contracts["dict_items_delete"], item_id)
        self.assert_dict_delete_contract(contracts["dicts_delete"], dict_id)

    def unique_code(self, prefix: str) -> str:
        """生成短字典编码，避免唯一索引在重复运行时冲突。"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def assert_dict_create_contract(self, contract) -> int:
        """验证字典创建接口成功信封，并返回新字典 ID。"""
        response = self.client.post(
            contract.path,
            {
                "name": self.unique_code("运行时Django字典"),
                "dictCode": self.unique_code("runtime_django_dict"),
                "status": 1,
                "remark": "运行时字典写接口契约",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["dictCode"].startswith("runtime_django_dict_")
        assert data["remark"] == "运行时字典写接口契约"
        return data["id"]

    def assert_dict_update_contract(self, contract, dict_id: int) -> None:
        """验证字典更新接口成功信封和关键字段落库。"""
        updated_code = self.unique_code("rt_django_dict_upd")
        response = self.client.put(
            contract.path.replace("{id}", str(dict_id)),
            {
                "name": "运行时 Django 字典已更新",
                "dictCode": updated_code,
                "status": 1,
                "remark": "已更新",
            },
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["name"] == "运行时 Django 字典已更新"
        assert data["dictCode"] == updated_code
        assert data["remark"] == "已更新"

    def assert_dict_delete_contract(self, contract, dict_id: int) -> None:
        """验证字典批量删除接口接受共享契约声明的 ids 请求体。"""
        response = self.client.delete(contract.path, {"ids": [dict_id]}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Dicts.objects.filter(id=dict_id).exists()

    def assert_dict_item_create_contract(self, contract, dict_id: int) -> int:
        """验证字典项创建接口成功信封，并返回新字典项 ID。"""
        response = self.client.post(
            contract.path,
            {"dict": dict_id, "label": "Django 标签", "value": "django", "status": 1},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["dict"] == dict_id
        assert data["label"] == "Django 标签"
        return data["id"]

    def assert_dict_item_update_contract(self, contract, item_id: int, dict_id: int) -> None:
        """验证字典项更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(item_id)),
            {"dict": dict_id, "label": "Django 标签已更新", "value": "django_updated", "status": 1},
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["label"] == "Django 标签已更新"
        assert data["value"] == "django_updated"

    def assert_dict_item_delete_contract(self, contract, item_id: int) -> None:
        """验证字典项批量删除接口接受共享契约声明的 ids 请求体。"""
        response = self.client.delete(contract.path, {"ids": [item_id]}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DictItems.objects.filter(id=item_id).exists()
