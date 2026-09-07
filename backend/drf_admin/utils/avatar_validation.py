"""Bounded avatar decoding shared by both backend packages."""

import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image

MAX_AVATAR_BYTES = 2 * 1024 * 1024
MAX_AVATAR_DIMENSION = 4096
MAX_AVATAR_FRAMES = 100
MAX_AVATAR_PIXELS = 32_000_000


def validate_avatar_content(content: bytes, filename: str) -> None:
    """Verify the declared format and decode each frame before any persistent write."""
    if not content or len(content) > MAX_AVATAR_BYTES:
        raise ValueError("Avatar size must be between 1 byte and 2 MiB")
    expected_format = Image.registered_extensions().get(Path(filename).suffix.lower())
    if expected_format is None:
        raise ValueError("Unsupported image extension")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as image:
                if image.format != expected_format:
                    raise ValueError("Image content does not match its extension")
                if max(image.size) > MAX_AVATAR_DIMENSION:
                    raise ValueError("Avatar dimensions exceed 4096 pixels")
                image.verify()
            # verify() is not a full decode; reopen and load within the cumulative budget.
            with Image.open(BytesIO(content)) as image:
                pixels = 0
                for frame in range(MAX_AVATAR_FRAMES + 1):
                    try:
                        image.seek(frame)
                    except EOFError:
                        return
                    if frame == MAX_AVATAR_FRAMES:
                        raise ValueError("Avatar exceeds 100 frames")
                    width, height = image.size
                    if min(width, height) <= 0 or max(width, height) > MAX_AVATAR_DIMENSION:
                        raise ValueError("Avatar dimensions exceed 4096 pixels")
                    pixels += width * height
                    if pixels > MAX_AVATAR_PIXELS:
                        raise ValueError("Avatar exceeds 32 million decoded pixels")
                    image.load()
    except (OSError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("Image is damaged or exceeds the decoding budget") from exc

