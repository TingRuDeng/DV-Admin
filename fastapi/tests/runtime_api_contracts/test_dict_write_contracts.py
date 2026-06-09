"""FastAPI 字典写接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid

from runtime_api_contracts.helpers import (
    DICT_ITEM_WRITE_SAMPLE_KEYS,
    DICT_WRITE_SAMPLE_KEYS,
    SimpleWriteContext,
    assert_success_payload,
    contracts_by_key,
)


def test_fastapi_dict_write_runtime_samples_match_endpoint_catalog(auth_client):
    """字典写接口必须接受前端字段，并满足共享端点目录。"""
    context = SimpleWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in DICT_WRITE_SAMPLE_KEYS)

    dict_id = assert_dict_create_contract(context)
    assert_dict_update_contract(context, dict_id)
    assert_dict_delete_contract(context, dict_id)


def test_fastapi_dict_item_write_runtime_samples_match_endpoint_catalog(auth_client):
    """字典项写接口必须接受前端字段，并满足共享端点目录。"""
    context = SimpleWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in DICT_ITEM_WRITE_SAMPLE_KEYS)

    dict_id = assert_dict_create_contract(context)
    item_id = assert_dict_item_create_contract(context, dict_id)
    assert_dict_item_update_contract(context, item_id, dict_id)
    assert_dict_item_delete_contract(context, item_id)
    assert_dict_delete_contract(context, dict_id)


def unique_code(prefix: str) -> str:
    """生成短字典编码，避免唯一索引在重复运行时冲突。"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def assert_dict_create_contract(context: SimpleWriteContext) -> int:
    """验证字典创建接口接受前端 dictCode/remark 字段。"""
    contract = context.contracts["dicts_create"]
    response = context.client.post(
        contract.path,
        json={
            "name": unique_code("运行时FastAPI字典"),
            "dictCode": unique_code("runtime_fastapi_dict"),
            "status": 1,
            "remark": "运行时字典写接口契约",
        },
    )
    data = assert_success_payload(response, contract)
    assert data["dictCode"].startswith("runtime_fastapi_dict_")
    assert data["remark"] == "运行时字典写接口契约"
    return data["id"]


def assert_dict_update_contract(context: SimpleWriteContext, dict_id: int) -> None:
    """验证字典更新接口接受共享路径和前端字段。"""
    contract = context.contracts["dicts_update"]
    updated_code = unique_code("runtime_fastapi_dict_updated")
    response = context.client.put(
        contract.path.replace("{id}", str(dict_id)),
        json={
            "name": "运行时 FastAPI 字典已更新",
            "dictCode": updated_code,
            "status": 1,
            "remark": "已更新",
        },
    )
    data = assert_success_payload(response, contract)
    assert data["name"] == "运行时 FastAPI 字典已更新"
    assert data["dictCode"] == updated_code
    assert data["remark"] == "已更新"


def assert_dict_delete_contract(context: SimpleWriteContext, dict_id: int) -> None:
    """验证字典批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["dicts_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [dict_id]})
    assert_success_payload(response, contract)


def assert_dict_item_create_contract(context: SimpleWriteContext, dict_id: int) -> int:
    """验证字典项创建接口接受前端 dict 字段。"""
    contract = context.contracts["dict_items_create"]
    response = context.client.post(
        contract.path,
        json={"dict": dict_id, "label": "FastAPI 标签", "value": "fastapi", "status": 1, "sort": 11},
    )
    data = assert_success_payload(response, contract)
    assert data["dict"] == dict_id
    assert data["label"] == "FastAPI 标签"
    return data["id"]


def assert_dict_item_update_contract(context: SimpleWriteContext, item_id: int, dict_id: int) -> None:
    """验证字典项更新接口接受共享路径和前端字段。"""
    contract = context.contracts["dict_items_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(item_id)),
        json={
            "dict": dict_id,
            "label": "FastAPI 标签已更新",
            "value": "fastapi_updated",
            "status": 1,
            "sort": 12,
        },
    )
    data = assert_success_payload(response, contract)
    assert data["label"] == "FastAPI 标签已更新"
    assert data["sort"] == 12


def assert_dict_item_delete_contract(context: SimpleWriteContext, item_id: int) -> None:
    """验证字典项批量删除接口接受共享契约声明的 ids 请求体。"""
    contract = context.contracts["dict_items_delete"]
    response = context.client.request("DELETE", contract.path, json={"ids": [item_id]})
    assert_success_payload(response, contract)
