"""FastAPI 个人中心与通知读取运行时契约测试。"""

from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path

import pytest_asyncio
from runtime_api_contracts.helpers import (
    assert_response_fields,
    assert_success_payload,
    contracts_by_key,
)

from app.db.models.system import Notices


@pytest_asyncio.fixture
async def runtime_notice_read_samples(db, test_user_with_role):
    """创建当前用户可见的通知读取样本。"""
    user_id = test_user_with_role["id"]
    suffix = uuid.uuid4().hex[:8]
    visible = await Notices.create(
        title=f"运行时可见通知_{suffix}",
        content="运行时通知正文",
        target_type=1,
        publish_status=1,
        publisher_id=user_id,
        publisher_name=test_user_with_role["username"],
    )
    targeted = await Notices.create(
        title=f"运行时定向通知_{suffix}",
        content="运行时定向正文",
        target_type=2,
        target_user_ids=[user_id],
        publish_status=1,
        publisher_id=user_id,
        publisher_name=test_user_with_role["username"],
    )
    return visible, targeted


def test_fastapi_information_runtime_samples_match_endpoint_catalog(
    auth_client,
    test_user_with_role,
    tmp_path: Path,
    monkeypatch,
):
    """个人中心前端契约必须由 FastAPI 真实路由完整实现。"""
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    contracts = contracts_by_key()

    profile_contract = contracts["information_profile"]
    profile = assert_success_payload(auth_client.get(profile_contract.path), profile_contract)
    assert_response_fields(profile, profile_contract.response_fields)

    update_contract = contracts["information_profile_update"]
    updated = assert_success_payload(
        auth_client.put(
            update_contract.path,
            json={
                "name": "运行时资料已更新",
                "email": "runtime-profile@example.com",
                "gender": 2,
            },
        ),
        update_contract,
    )
    assert_response_fields(updated, update_contract.response_fields)
    assert updated["name"] == "运行时资料已更新"

    password_contract = contracts["information_password"]
    assert_success_payload(
        auth_client.put(
            password_contract.path,
            json={
                "oldPassword": test_user_with_role["password"],
                "newPassword": "runtime456",
                "confirmPassword": "runtime456",
            },
        ),
        password_contract,
    )

    assert auth_client.get(profile_contract.path).status_code == 401
    login_contract = contracts["auth_login"]
    login = assert_success_payload(
        auth_client.post(
            login_contract.path,
            json={
                "username": test_user_with_role["username"],
                "password": "runtime456",
            },
        ),
        login_contract,
    )
    auth_client.headers["Authorization"] = f"Bearer {login['accessToken']}"

    avatar_contract = contracts["information_avatar"]
    avatar = assert_success_payload(
        auth_client.post(
            avatar_contract.path,
            files={
                "file": (
                    "runtime-avatar.png",
                    BytesIO(b"\x89PNG\r\n\x1a\nruntime"),
                    "image/png",
                ),
            },
        ),
        avatar_contract,
    )
    assert_response_fields(avatar, avatar_contract.response_fields)
    assert avatar["url"].startswith("/media/avatar/")


def test_fastapi_notice_read_runtime_samples_match_endpoint_catalog(
    auth_client,
    test_user_with_role,
    runtime_notice_read_samples,
):
    """通知读取、详情和已读状态必须由 FastAPI 真实路由完整实现。"""
    visible, targeted = runtime_notice_read_samples
    contracts = contracts_by_key()

    form_contract = contracts["notices_form"]
    form = assert_success_payload(
        auth_client.get(form_contract.path.replace("{id}", str(visible.id))),
        form_contract,
    )
    assert_response_fields(form, form_contract.response_fields)

    page_contract = contracts["notices_my_page"]
    page = assert_success_payload(
        auth_client.get(page_contract.path, params={"pageNum": 1, "pageSize": 10}),
        page_contract,
    )
    assert_response_fields(page, page_contract.response_fields)
    assert {item["id"] for item in page["list"]} >= {visible.id, targeted.id}
    invalid_filter = auth_client.get(page_contract.path, params={"isRead": 2})
    assert invalid_filter.status_code == 422

    detail_contract = contracts["notices_detail"]
    detail = assert_success_payload(
        auth_client.get(detail_contract.path.replace("{id}", str(visible.id))),
        detail_contract,
    )
    assert_response_fields(detail, detail_contract.response_fields)

    read_all_contract = contracts["notices_read_all"]
    assert_success_payload(
        auth_client.put(read_all_contract.path),
        read_all_contract,
    )
