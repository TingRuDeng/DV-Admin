from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlencode

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Users


class FileApiTestCase(TestCase):
    """通用文件接口必须限制类型、大小、路径和删除所有权。"""

    def setUp(self):
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()
        self.client = APIClient()
        self.owner = Users.objects.create_user(
            username="file-owner",
            password="testpass123",
            name="文件所有者",
            is_active=1,
        )
        self.other_user = Users.objects.create_user(
            username="file-other",
            password="testpass123",
            name="其他用户",
            is_active=1,
        )

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()

    def test_file_api_requires_authentication(self):
        upload_response = self.client.post(
            "/api/v1/files/",
            {"file": self.uploaded_file()},
            format="multipart",
        )
        delete_response = self.client.delete(self.delete_url("files/1/contract.txt"))

        self.assertEqual(upload_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_upload_and_delete_file_by_returned_path(self):
        response = self.upload_as_owner()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertEqual(data["name"], "contract.txt")
        self.assertTrue(data["path"].startswith(f"files/{self.owner.id}/"))
        self.assertTrue(data["url"].endswith(f"/media/{data['path']}"))
        stored_file = Path(self.media_root.name) / data["path"]
        self.assertEqual(stored_file.read_bytes(), b"shared file contract")

        delete_response = self.client.delete(self.delete_url(data["path"]))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.json()["code"], 20000)
        self.assertFalse(stored_file.exists())

    def test_other_user_cannot_delete_owner_file(self):
        data = self.upload_as_owner().json()["data"]
        stored_file = Path(self.media_root.name) / data["path"]
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.delete_url(data["path"]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("无权删除该文件", str(response.json()["errors"]))
        self.assertTrue(stored_file.exists())

    def test_delete_rejects_full_url_and_path_traversal(self):
        data = self.upload_as_owner().json()["data"]
        stored_file = Path(self.media_root.name) / data["path"]

        for invalid_path in (data["url"], f"files/{self.owner.id}/../contract.txt"):
            with self.subTest(file_path=invalid_path):
                response = self.client.delete(self.delete_url(invalid_path))
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("非法的文件路径", str(response.json()["errors"]))
                self.assertTrue(stored_file.exists())

    def test_upload_rejects_unsupported_and_oversized_files_without_residue(self):
        self.client.force_authenticate(user=self.owner)

        unsupported = self.client.post(
            "/api/v1/files/",
            {"file": self.uploaded_file(name="payload.svg", content=b"<svg></svg>")},
            format="multipart",
        )
        self.assertEqual(unsupported.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("不支持的文件类型", str(unsupported.json()["errors"]))

        with override_settings(MAX_UPLOAD_SIZE=4):
            oversized = self.client.post(
                "/api/v1/files/",
                {"file": self.uploaded_file(content=b"too large")},
                format="multipart",
            )
        self.assertEqual(oversized.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("文件大小不能超过", str(oversized.json()["errors"]))
        self.assertFalse(any(path.is_file() for path in Path(self.media_root.name).rglob("*")))

    def upload_as_owner(self):
        self.client.force_authenticate(user=self.owner)
        return self.client.post(
            "/api/v1/files/",
            {"file": self.uploaded_file()},
            format="multipart",
        )

    @staticmethod
    def delete_url(file_path: str) -> str:
        return f"/api/v1/files/?{urlencode({'filePath': file_path})}"

    @staticmethod
    def uploaded_file(name: str = "contract.txt", content: bytes = b"shared file contract"):
        return SimpleUploadedFile(name, content, content_type="text/plain")
