import importlib

from scripts.api_field_contracts import (
    assert_api_field_contract_catalog,
    iter_api_field_contracts,
    iter_api_field_converge_items,
    iter_field_contract_exempt_read_endpoints,
    iter_read_endpoint_field_contracts,
)


def fastapi_output_keys(dotted_path: str) -> set[str]:
    """读取 FastAPI schema 的对外 alias 字段集合。"""
    module_name, class_name = dotted_path.rsplit(".", 1)
    schema_class = getattr(importlib.import_module(module_name), class_name)
    model = schema_class.model_construct(**{name: None for name in schema_class.model_fields})
    return set(model.model_dump(by_alias=True).keys())


def test_fastapi_output_keys_match_api_field_contracts():
    """FastAPI 响应字段不能出现未登记漂移。"""
    assert_api_field_contract_catalog()

    for contract in iter_api_field_contracts():
        actual = fastapi_output_keys(contract.fastapi_source)
        allowed = contract.canonical | contract.fastapi_only

        assert contract.canonical <= actual, f"{contract.key} FastAPI 缺少权威字段: {contract.canonical - actual}"
        assert actual <= allowed, f"{contract.key} FastAPI 出现未登记字段: {actual - allowed}"


def test_api_field_contracts_track_read_endpoint_coverage_and_converge_debt():
    """字段契约必须显式登记读端点覆盖关系和待收敛字段。"""
    assert_api_field_contract_catalog()

    coverage = dict(iter_read_endpoint_field_contracts())
    converge_items = iter_api_field_converge_items()
    exempt_endpoints = iter_field_contract_exempt_read_endpoints()

    assert "notices_page" in coverage
    assert coverage["roles_form"] == "roles_with_permissions"
    assert ("dict_items_out", "tagType") not in converge_items
    assert "logs_page" in exempt_endpoints
