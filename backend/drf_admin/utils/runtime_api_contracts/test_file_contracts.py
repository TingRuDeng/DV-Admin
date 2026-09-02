from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlencode

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from drf_admin.utils.runtime_api_contracts.helpers import (
    assert_response_fields,
    assert_success_payload,
    contracts_by_key,
    create_runtime_contract_user,
)


class DjangoRuntimeFileApiContractTestCase(TestCase):
    """Django 文件上传和删除必须满足共享端点目录。"""

    def setUp(self):
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()
        self.client = APIClient()
        self.user = create_runtime_contract_user()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()

    def test_django_file_runtime_sample_matches_endpoint_catalog(self):
        contracts = contracts_by_key()
        upload_contract = contracts["files_upload"]
        upload_data = assert_success_payload(
            self.client.post(
                upload_contract.path,
                {
                    "file": SimpleUploadedFile(
                        "runtime-contract.txt",
                        b"runtime contract",
                        content_type="text/plain",
                    )
                },
                format="multipart",
            ),
            upload_contract,
        )
        assert_response_fields(upload_data, upload_contract.response_fields)
        assert upload_data["path"].startswith(f"files/{self.user.id}/")

        uploaded_file = Path(self.media_root.name) / upload_data["path"]
        assert uploaded_file.exists()

        delete_contract = contracts["files_delete"]
        assert_success_payload(
            self.client.delete(
                f"{delete_contract.path}?{urlencode({'filePath': upload_data['path']})}"
            ),
            delete_contract,
        )
        assert not uploaded_file.exists()
