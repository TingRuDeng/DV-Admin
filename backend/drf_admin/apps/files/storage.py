from __future__ import annotations

import os
import re
import uuid
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

ALLOWED_EXTENSIONS = frozenset(
    {
        ".7z",
        ".avi",
        ".bmp",
        ".doc",
        ".docx",
        ".gif",
        ".gz",
        ".jpeg",
        ".jpg",
        ".mov",
        ".mp3",
        ".mp4",
        ".pdf",
        ".png",
        ".ppt",
        ".pptx",
        ".rar",
        ".tar",
        ".txt",
        ".webp",
        ".wmv",
        ".xls",
        ".xlsx",
        ".zip",
    }
)
USER_FILE_ROOT = "files"


def allowed_file(filename: str) -> bool:
    """只允许与 FastAPI 通用上传一致的扩展名。"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def secure_filename(filename: str) -> str:
    """移除路径与危险字符，仅把清理后的名称用于展示前缀。"""
    safe_name = re.sub(r"[^\w\-_.]", "_", Path(filename).name)
    if len(safe_name) <= 100:
        return safe_name
    stem, suffix = os.path.splitext(safe_name)
    return f"{stem[: 100 - len(suffix)]}{suffix}"


def format_file_size(size: int) -> str:
    """生成与 FastAPI 一致的可读大小错误信息。"""
    display_size = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if display_size < 1024.0:
            return f"{display_size:.1f} {unit}"
        display_size /= 1024.0
    return f"{display_size:.1f} PB"


def user_upload_subdir(user_id: int) -> str:
    """按用户隔离上传目录，为删除所有权提供稳定边界。"""
    return f"{USER_FILE_ROOT}/{user_id}"


def normalize_file_path(file_path: str) -> str:
    """只接受上传响应返回的相对 POSIX 路径。"""
    if not file_path or file_path != file_path.strip():
        raise ValidationError("非法的文件路径")
    if "://" in file_path or file_path.startswith("/") or "\\" in file_path:
        raise ValidationError("非法的文件路径")

    relative_path = PurePosixPath(file_path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValidationError("非法的文件路径")
    return relative_path.as_posix()


def ensure_file_owner(file_path: str, user_id: int) -> None:
    """删除前确认文件位于当前用户目录。"""
    if not file_path.startswith(f"{user_upload_subdir(user_id)}/"):
        raise PermissionDenied("无权删除该文件")


def resolve_upload_path(file_path: str) -> Path:
    """把相对路径限制在媒体根目录内。"""
    media_root = Path(settings.MEDIA_ROOT).resolve()
    full_path = (media_root / file_path).resolve()
    try:
        full_path.relative_to(media_root)
    except ValueError as exc:
        raise ValidationError("非法的文件路径") from exc
    return full_path


def save_upload_file(upload, user_id: int) -> str:
    """分块写入临时文件，成功后原子替换到最终随机文件名。"""
    max_size = settings.MAX_UPLOAD_SIZE
    if upload.size > max_size:
        raise ValidationError(f"文件大小不能超过 {format_file_size(max_size)}")

    original_name = secure_filename(upload.name)
    stem, suffix = os.path.splitext(original_name)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    final_name = f"{stem}_{timestamp}_{uuid.uuid4().hex[:8]}{suffix.lower()}"
    relative_dir = user_upload_subdir(user_id)
    save_dir = resolve_upload_path(relative_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    final_path = save_dir / final_name
    temporary_path = save_dir / f".{final_name}.{uuid.uuid4().hex}.part"

    written = 0
    try:
        with temporary_path.open("xb") as destination:
            for chunk in upload.chunks():
                written += len(chunk)
                if written > max_size:
                    raise ValidationError(f"文件大小不能超过 {format_file_size(max_size)}")
                destination.write(chunk)
        os.replace(temporary_path, final_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise

    return f"{relative_dir}/{final_name}"
