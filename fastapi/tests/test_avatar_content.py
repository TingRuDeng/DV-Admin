from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image


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


@pytest.mark.parametrize(
    "content,name",
    [
        (b"not an image", "spoof.png"),
        (picture(), "mismatch.jpg"),
        (picture((4097, 1)), "wide.png"),
        (picture()[:45], "broken.png"),
        (picture(frames=101), "frames.gif"),
        (picture((4096, 4096), 2), "pixels.gif"),
    ],
    ids=["spoof", "extension", "dimension", "truncated", "frames", "pixels"],
)
def test_invalid_avatar_preserves_user_and_leaves_no_file(
    auth_client, tmp_path, monkeypatch, content, name
):
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    before = auth_client.get("/api/v1/information/profile/").json()["data"]["avatar"]
    response = auth_client.post(
        "/api/v1/information/change-avatar/",
        files={"file": (name, content, "image/png")},
    )
    assert response.status_code == 400
    assert not any(path.is_file() for path in tmp_path.rglob("*"))
    assert (
        auth_client.get("/api/v1/information/profile/").json()["data"]["avatar"]
        == before
    )


@pytest.mark.parametrize(
    "format,extension",
    [
        ("PNG", "png"),
        ("JPEG", "jpg"),
        ("JPEG", "jpeg"),
        ("GIF", "gif"),
        ("BMP", "bmp"),
        ("WEBP", "webp"),
    ],
)
def test_supported_image_formats_are_fully_decoded(format, extension):
    from app.core.avatar_validation import validate_avatar_content

    buffer = BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, format=format)
    validate_avatar_content(buffer.getvalue(), f"avatar.{extension}")


def test_avatar_boundaries_and_packaged_policy_parity():
    from app.core.avatar_validation import validate_avatar_content

    validate_avatar_content(picture((4096, 1)), "edge.png")
    validate_avatar_content(picture(frames=100), "edge.gif")
    validate_avatar_content(picture((4000, 4000), 2), "pixels.gif")
    content = picture()
    validate_avatar_content(
        content + b"x" * (2 * 1024 * 1024 - len(content)), "size.png"
    )
    root = Path(__file__).resolve().parents[2]
    assert (root / "fastapi/app/core/avatar_validation.py").read_bytes() == (
        root / "backend/drf_admin/utils/avatar_validation.py"
    ).read_bytes()


def test_avatar_save_failure_rolls_back_database_and_file(
    auth_client, tmp_path, monkeypatch
):
    from app.core.config import settings
    from app.db.models.oauth import Users

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    before = auth_client.get("/api/v1/information/profile/").json()["data"]["avatar"]
    original = Users.save

    async def fail_after_save(instance, *args, **kwargs):
        await original(instance, *args, **kwargs)
        raise RuntimeError("database transaction failed")

    with patch.object(Users, "save", fail_after_save), pytest.raises(RuntimeError):
        auth_client.post(
            "/api/v1/information/change-avatar/",
            files={"file": ("valid.png", picture(), "image/png")},
        )
    assert (
        auth_client.get("/api/v1/information/profile/").json()["data"]["avatar"]
        == before
    )
    assert not any(path.is_file() for path in tmp_path.rglob("*"))
