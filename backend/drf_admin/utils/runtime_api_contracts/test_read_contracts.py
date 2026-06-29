"""Django 读接口运行时契约抽样测试。"""

from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from drf_admin.utils.runtime_api_contracts.helpers import (
    PAGE_SIZE_SAMPLE,
    READ_SAMPLE_KEYS,
    assert_response_fields,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_departments,
    create_runtime_contract_dicts,
    create_runtime_contract_user,
    sample_query_params,
)


class DjangoRuntimeReadApiContractTestCase(TestCase):
    """Django 关键读端点运行时响应必须满足共享端点目录。"""

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
            self.client.get(contracts["users_page"].path, {"pageNum": 1, "pageSize": PAGE_SIZE_SAMPLE}),
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
            self.client.get(contract.path, {"pageNum": 1, "pageSize": 10, "dictCode": "runtime_contract"}),
            contract,
        )

        values = {item["value"] for item in data["list"]}
        assert data["total"] == 2
        assert values == {"enabled", "disabled"}
