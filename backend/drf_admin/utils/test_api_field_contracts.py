import importlib

from djangorestframework_camel_case.util import camelize
from scripts.api_field_contracts import (
    assert_api_field_contract_catalog,
    iter_api_field_contracts,
)


def django_output_keys(dotted_path: str) -> set[str]:
    """读取 Django serializer 声明字段，并转换为对外驼峰 key。"""
    module_name, class_name = dotted_path.rsplit(".", 1)
    serializer_class = getattr(importlib.import_module(module_name), class_name)
    fields = serializer_class().fields.keys()
    return set(camelize({field: None for field in fields}).keys())


def test_django_output_keys_match_api_field_contracts():
    """Django 响应字段不能出现未登记漂移。"""
    assert_api_field_contract_catalog()

    for contract in iter_api_field_contracts():
        actual = django_output_keys(contract.django_source)
        allowed = contract.canonical | contract.django_only

        assert contract.canonical <= actual, f"{contract.key} Django 缺少权威字段: {contract.canonical - actual}"
        assert actual <= allowed, f"{contract.key} Django 出现未登记字段: {actual - allowed}"
