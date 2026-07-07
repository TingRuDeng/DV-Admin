import importlib

from djangorestframework_camel_case.util import camelize
from scripts.api_field_contracts import (
    assert_api_field_contract_catalog,
    iter_api_field_contracts,
    iter_api_field_converge_items,
    iter_endpoint_field_contracts,
    iter_field_contract_exempt_endpoints,
)
from scripts.api_field_source_introspection import extract_dict_output_keys
from scripts.api_frontend_field_contracts import iter_frontend_field_contract_exempt_endpoints


def django_output_keys(dotted_path: str) -> set[str]:
    """读取 Django serializer 声明字段，并转换为对外驼峰 key。"""
    dict_keys = extract_dict_output_keys(PROJECT_ROOT, dotted_path)
    if dict_keys:
        return dict_keys
    module_name, class_name = dotted_path.rsplit(".", 1)
    serializer_class = getattr(importlib.import_module(module_name), class_name)
    fields = serializer_class().fields.keys()
    return set(camelize({field: None for field in fields}).keys())


PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]


def test_django_output_keys_match_api_field_contracts():
    """Django 响应字段不能出现未登记漂移。"""
    assert_api_field_contract_catalog()

    for contract in iter_api_field_contracts():
        actual = django_output_keys(contract.django_source)
        allowed = contract.canonical | contract.django_only

        assert contract.canonical <= actual, f"{contract.key} Django 缺少权威字段: {contract.canonical - actual}"
        assert actual <= allowed, f"{contract.key} Django 出现未登记字段: {actual - allowed}"


def test_api_field_contracts_track_endpoint_coverage_and_converge_debt():
    """字段契约必须显式登记端点覆盖关系、豁免和待收敛字段。"""
    assert_api_field_contract_catalog()

    coverage = dict(iter_endpoint_field_contracts())
    converge_items = iter_api_field_converge_items()
    exempt_endpoints = iter_field_contract_exempt_endpoints()
    frontend_exempt_endpoints = iter_frontend_field_contract_exempt_endpoints()

    assert coverage["auth_info"] == "auth_info"
    assert coverage["auth_routes"] == "auth_routes"
    assert coverage["users_create"] == "users_out"
    assert coverage["roles_update"] == "roles_out"
    assert coverage["dict_items_update"] == "dict_items_out"
    assert "notices_page" in coverage
    assert coverage["roles_form"] == "roles_with_permissions"
    assert ("dict_items_out", "tagType") not in converge_items
    assert coverage["logs_page"] == "logs_out"
    assert "logs_page" not in exempt_endpoints
    assert "auth_login" in exempt_endpoints
    assert "auth_login" in frontend_exempt_endpoints
    assert "files_upload" in frontend_exempt_endpoints
    assert "logs_page" not in frontend_exempt_endpoints
