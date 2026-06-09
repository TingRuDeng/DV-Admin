"""Django 通知公告写接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid

from django.apps import apps
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.utils.runtime_api_contracts.helpers import (
    NOTICE_WRITE_SAMPLE_KEYS,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_user,
)


class DjangoRuntimeNoticeWriteApiContractTestCase(TestCase):
    """Django 通知公告写端点运行时响应必须满足共享端点目录。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        self.client.force_authenticate(user=self.user)

    def test_django_notice_write_runtime_samples_match_endpoint_catalog(self):
        """通知公告写接口必须接受前端字段，并满足共享端点目录。"""
        contracts = contracts_by_key()
        assert all(key in contracts for key in NOTICE_WRITE_SAMPLE_KEYS)

        notice_id = self.assert_notice_create_contract(contracts["notices_create"])
        self.assert_notice_update_contract(contracts["notices_update"], notice_id)
        self.assert_notice_publish_contract(contracts["notices_publish"], notice_id)
        self.assert_notice_revoke_contract(contracts["notices_revoke"], notice_id)
        self.assert_notice_delete_contract(contracts["notices_delete"], notice_id)

    def unique_title(self) -> str:
        """生成唯一标题，避免重复运行时被历史数据干扰。"""
        return f"运行时Django通知_{uuid.uuid4().hex[:8]}"

    def notice_payload(self, title: str) -> dict:
        """构造前端通知表单字段，锁定 camelCase 请求契约。"""
        return {
            "title": title,
            "content": "运行时通知公告写接口契约",
            "type": 1,
            "level": "L",
            "targetType": 1,
        }

    def assert_notice_create_contract(self, contract) -> int:
        """验证通知创建接口成功信封，并返回新通知 ID。"""
        response = self.client.post(contract.path, self.notice_payload(self.unique_title()), format="json")
        data = assert_success_payload(response, contract, status.HTTP_201_CREATED)
        assert data["title"].startswith("运行时Django通知_")
        assert data["targetType"] == 1
        assert data["publishStatus"] == 0
        return data["id"]

    def assert_notice_update_contract(self, contract, notice_id: int) -> None:
        """验证通知更新接口成功信封和关键字段落库。"""
        response = self.client.put(
            contract.path.replace("{id}", str(notice_id)),
            self.notice_payload("运行时 Django 通知已更新"),
            format="json",
        )
        data = assert_success_payload(response, contract)
        assert data["title"] == "运行时 Django 通知已更新"
        assert data["targetType"] == 1

    def assert_notice_publish_contract(self, contract, notice_id: int) -> None:
        """验证通知发布接口使用共享路径。"""
        response = self.client.put(contract.path.replace("{id}", str(notice_id)), format="json")
        assert_success_payload(response, contract)

    def assert_notice_revoke_contract(self, contract, notice_id: int) -> None:
        """验证通知撤回接口使用共享路径。"""
        response = self.client.put(contract.path.replace("{id}", str(notice_id)), format="json")
        assert_success_payload(response, contract)

    def assert_notice_delete_contract(self, contract, notice_id: int) -> None:
        """验证通知删除接口使用共享路径中的逗号分隔 ID。"""
        response = self.client.delete(contract.path.replace("{ids}", str(notice_id)), format="json")
        assert_success_payload(response, contract)
        assert not self.notice_model().objects.filter(id=notice_id).exists()

    def notice_model(self):
        """延迟获取通知模型，确保 RED 阶段暴露当前 Django 缺模型的事实。"""
        return apps.get_model("system", "Notices")
