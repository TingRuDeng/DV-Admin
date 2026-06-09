"""FastAPI 通知公告写接口运行时契约抽样测试。"""

from __future__ import annotations

import uuid

from runtime_api_contracts.helpers import (
    NOTICE_WRITE_SAMPLE_KEYS,
    SimpleWriteContext,
    assert_success_payload,
    contracts_by_key,
)


def test_fastapi_notice_write_runtime_samples_match_endpoint_catalog(auth_client):
    """通知公告写接口必须接受前端字段，并满足共享端点目录。"""
    context = SimpleWriteContext(client=auth_client, contracts=contracts_by_key())
    assert all(key in context.contracts for key in NOTICE_WRITE_SAMPLE_KEYS)

    notice_id = assert_notice_create_contract(context)
    assert_notice_update_contract(context, notice_id)
    assert_notice_publish_contract(context, notice_id)
    assert_notice_revoke_contract(context, notice_id)
    assert_notice_delete_contract(context, notice_id)


def unique_title() -> str:
    """生成唯一标题，避免重复运行时被历史数据干扰。"""
    return f"运行时通知_{uuid.uuid4().hex[:8]}"


def notice_payload(title: str) -> dict:
    """构造前端通知表单字段，锁定 camelCase 请求契约。"""
    return {
        "title": title,
        "content": "运行时通知公告写接口契约",
        "type": 1,
        "level": "L",
        "targetType": 1,
    }


def assert_notice_create_contract(context: SimpleWriteContext) -> int:
    """验证通知创建接口接受前端表单字段。"""
    contract = context.contracts["notices_create"]
    response = context.client.post(contract.path, json=notice_payload(unique_title()))
    data = assert_success_payload(response, contract)
    assert data["title"].startswith("运行时通知_")
    assert data["targetType"] == 1
    assert data["publishStatus"] == 0
    return data["id"]


def assert_notice_update_contract(context: SimpleWriteContext, notice_id: int) -> None:
    """验证通知更新接口接受共享路径和前端字段。"""
    contract = context.contracts["notices_update"]
    response = context.client.put(
        contract.path.replace("{id}", str(notice_id)),
        json=notice_payload("运行时通知已更新"),
    )
    data = assert_success_payload(response, contract)
    assert data["title"] == "运行时通知已更新"
    assert data["targetType"] == 1


def assert_notice_publish_contract(context: SimpleWriteContext, notice_id: int) -> None:
    """验证通知发布接口使用共享路径。"""
    contract = context.contracts["notices_publish"]
    response = context.client.put(contract.path.replace("{id}", str(notice_id)))
    assert_success_payload(response, contract)


def assert_notice_revoke_contract(context: SimpleWriteContext, notice_id: int) -> None:
    """验证通知撤回接口使用共享路径。"""
    contract = context.contracts["notices_revoke"]
    response = context.client.put(contract.path.replace("{id}", str(notice_id)))
    assert_success_payload(response, contract)


def assert_notice_delete_contract(context: SimpleWriteContext, notice_id: int) -> None:
    """验证通知删除接口使用共享路径中的逗号分隔 ID。"""
    contract = context.contracts["notices_delete"]
    response = context.client.delete(contract.path.replace("{ids}", str(notice_id)))
    assert_success_payload(response, contract)
