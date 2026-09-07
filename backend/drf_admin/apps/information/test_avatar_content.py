import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Users


def picture(size=(2, 2), frames=1):
    buffer = BytesIO()
    images = [Image.new("RGB", size, (i % 256, 100, 80)) for i in range(frames)]
    images[0].save(
        buffer,
        format="PNG" if frames == 1 else "GIF",
        save_all=frames > 1,
        append_images=images[1:],
        duration=20,
        loop=0,
    )
    return buffer.getvalue()


class AvatarContentTests(TestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            username="avatar-test", password="old password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_decode_and_resource_budgets_preserve_existing_avatar(self):
        cases = [
            (b"not image", "spoof.png"),
            (picture(), "mismatch.jpg"),
            (picture((4097, 1)), "wide.png"),
            (picture()[:45], "broken.png"),
            (picture(frames=101), "frames.gif"),
            (picture((4096, 4096), 2), "pixels.gif"),
            (picture() + b"x" * (2 * 1024 * 1024), "large.png"),
        ]
        for content, name in cases:
            with self.subTest(
                name=name
            ), tempfile.TemporaryDirectory() as folder, override_settings(
                MEDIA_ROOT=folder
            ):
                before = self.user.image.name
                response = self.client.post(
                    "/api/v1/information/change-avatar/",
                    {
                        "file": SimpleUploadedFile(
                            name, content, content_type="image/png"
                        )
                    },
                    format="multipart",
                )
                self.assertEqual(response.status_code, 400)
                self.user.refresh_from_db()
                self.assertEqual(self.user.image.name, before)
                self.assertFalse(any(p.is_file() for p in Path(folder).rglob("*")))

    def test_storage_write_is_removed_if_database_save_fails(self):
        original = Users.save

        def fail_after_file_save(instance, *args, **kwargs):
            original(instance, *args, **kwargs)
            raise RuntimeError("database transaction failed")

        with tempfile.TemporaryDirectory() as folder, override_settings(
            MEDIA_ROOT=folder
        ):
            before = self.user.image.name
            with patch.object(Users, "save", fail_after_file_save):
                response = self.client.post(
                    "/api/v1/information/change-avatar/",
                    {
                        "file": SimpleUploadedFile(
                            "valid.png", picture(), content_type="image/png"
                        )
                    },
                    format="multipart",
                )
            self.assertEqual(response.status_code, 400)
            self.user.refresh_from_db()
            self.assertEqual(self.user.image.name, before)
            self.assertFalse(any(p.is_file() for p in Path(folder).rglob("*")))
