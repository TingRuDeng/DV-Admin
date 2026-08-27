"""Django 个人中心与通知读取运行时契约测试。"""

from __future__ import annotations

import base64
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from drf_admin.apps.system.models import NoticeReads, Notices
from drf_admin.utils.runtime_api_contracts.helpers import (
    assert_response_fields,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_user,
)


class DjangoRuntimeInformationApiContractTestCase(TestCase):
    """个人中心前端契约必须由 Django 真实路由完整实现。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        self.client.force_authenticate(user=self.user)
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()

    def test_django_information_runtime_samples_match_endpoint_catalog(self):
        contracts = contracts_by_key()

        profile_contract = contracts["information_profile"]
        profile = assert_success_payload(
            self.client.get(profile_contract.path),
            profile_contract,
        )
        assert_response_fields(profile, profile_contract.response_fields)

        update_contract = contracts["information_profile_update"]
        updated = assert_success_payload(
            self.client.put(
                update_contract.path,
                {
                    "name": "运行时资料已更新",
                    "email": "runtime-profile@example.com",
                    "gender": 2,
                },
                format="json",
            ),
            update_contract,
        )
        assert_response_fields(updated, update_contract.response_fields)
        assert updated["name"] == "运行时资料已更新"

        password_contract = contracts["information_password"]
        assert_success_payload(
            self.client.put(
                password_contract.path,
                {
                    "oldPassword": "testpass123",
                    "newPassword": "runtime456",
                    "confirmPassword": "runtime456",
                },
                format="json",
            ),
            password_contract,
        )
        self.user.refresh_from_db()
        assert self.user.check_password("runtime456")

        avatar_contract = contracts["information_avatar"]
        image = SimpleUploadedFile(
            "runtime-avatar.gif",
            base64.b64decode("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="),
            content_type="image/gif",
        )
        avatar = assert_success_payload(
            self.client.post(
                avatar_contract.path,
                {"file": image},
                format="multipart",
            ),
            avatar_contract,
        )
        assert_response_fields(avatar, avatar_contract.response_fields)
        assert "/media/avatar/" in avatar["url"]


class DjangoRuntimeNoticeReadApiContractTestCase(TestCase):
    """通知读取、详情和已读状态必须由 Django 真实路由完整实现。"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        self.client.force_authenticate(user=self.user)
        self.notice = Notices.objects.create(
            title="运行时可见通知",
            content="运行时通知正文",
            target_type=1,
            publish_status=1,
            publisher_id=self.user.id,
            publisher_name=self.user.username,
        )
        self.targeted_notice = Notices.objects.create(
            title="运行时定向通知",
            content="运行时定向正文",
            target_type=2,
            target_user_ids=[self.user.id],
            publish_status=1,
            publisher_id=self.user.id,
            publisher_name=self.user.username,
        )

    def test_django_notice_read_runtime_samples_match_endpoint_catalog(self):
        contracts = contracts_by_key()

        form_contract = contracts["notices_form"]
        form = assert_success_payload(
            self.client.get(form_contract.path.replace("{id}", str(self.notice.id))),
            form_contract,
        )
        assert_response_fields(form, form_contract.response_fields)

        page_contract = contracts["notices_my_page"]
        page = assert_success_payload(
            self.client.get(page_contract.path, {"pageNum": 1, "pageSize": 10}),
            page_contract,
        )
        assert_response_fields(page, page_contract.response_fields)
        assert {item["id"] for item in page["list"]} == {
            self.notice.id,
            self.targeted_notice.id,
        }

        detail_contract = contracts["notices_detail"]
        detail = assert_success_payload(
            self.client.get(
                detail_contract.path.replace("{id}", str(self.notice.id)),
            ),
            detail_contract,
        )
        assert_response_fields(detail, detail_contract.response_fields)
        assert NoticeReads.objects.filter(
            notice=self.notice,
            user_id=self.user.id,
        ).exists()

        read_all_contract = contracts["notices_read_all"]
        assert_success_payload(
            self.client.put(read_all_contract.path),
            read_all_contract,
        )
        assert NoticeReads.objects.filter(
            notice=self.targeted_notice,
            user_id=self.user.id,
        ).exists()
