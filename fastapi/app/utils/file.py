# -*- coding: utf-8 -*-
"""
文件处理工具模块

包含文件上传相关的工具函数。
"""

import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from app.core.exceptions import ValidationError

UPLOAD_CHUNK_SIZE = 64 * 1024
MAX_AVATAR_UPLOAD_SIZE = 2 * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    # 图片文件
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp',
    # 文档文件
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
    # 压缩文件
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # 其他文件
    '.mp3', '.mp4', '.avi', '.mov', '.wmv'
}


def allowed_file(filename: str) -> bool:
    """
    检查文件扩展名是否被允许

    Args:
        filename: 文件名

    Returns:
        是否允许
    """
    if '.' not in filename:
        return False
    extension = '.' + filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def secure_filename(filename: str) -> str:
    """
    生成安全的文件名

    Args:
        filename: 原始文件名

    Returns:
        安全的文件名
    """
    # 移除路径部分
    filename = Path(filename).name

    # 移除危险字符
    filename = re.sub(r'[^\w\-_\.]', '_', filename)

    # 限制文件名长度
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext

    return filename


def get_file_size(file_path: str) -> int:
    """
    获取文件大小

    Args:
        file_path: 文件路径

    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_file_size(size: int) -> str:
    """
    格式化文件大小显示

    Args:
        size: 文件大小（字节）

    Returns:
        格式化后的大小字符串
    """
    display_size = float(size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if display_size < 1024.0:
            return f"{display_size:.1f} {unit}"
        display_size /= 1024.0
    return f"{display_size:.1f} PB"


async def copy_upload_file(
    file,
    destination: BinaryIO,
    *,
    max_size: int | None = None,
) -> int:
    """分块复制上传内容，并在写入过程中执行大小上限校验。"""
    total_size = 0
    while True:
        chunk = await file.read(UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if max_size is not None and total_size > max_size:
            raise ValidationError(f"文件大小不能超过 {format_file_size(max_size)}")
        destination.write(chunk)
    destination.flush()
    destination.seek(0)
    return total_size


async def save_upload_file(
    file,
    subdir: str = "",
    max_size: int | None = None,
    filename_prefix: str | None = None,
) -> str:
    """
    保存上传的文件

    Args:
        file: 上传的文件对象
        subdir: 子目录名称
        max_size: 最大文件大小（字节）
        filename_prefix: 自定义文件名前缀

    Returns:
        相对路径
    """
    from app.core.config import settings

    # 生成文件名
    filename = secure_filename(file.filename or "upload")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    name, ext = os.path.splitext(filename)
    safe_prefix = secure_filename(filename_prefix) if filename_prefix else name
    new_filename = f"{safe_prefix}_{timestamp}_{unique_id}{ext}"

    # 构建保存路径
    save_dir = Path(settings.upload_dir)
    if subdir:
        save_dir /= subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / new_filename
    temporary_path = save_dir / f".{new_filename}.{uuid.uuid4().hex}.part"
    try:
        with temporary_path.open("xb") as destination:
            await copy_upload_file(file, destination, max_size=max_size)
        os.replace(temporary_path, file_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise

    # 返回相对路径
    if subdir:
        return f"{subdir}/{new_filename}"
    return new_filename
