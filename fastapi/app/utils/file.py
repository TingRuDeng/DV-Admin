# -*- coding: utf-8 -*-
"""
文件处理工具模块

包含文件上传相关的工具函数。
"""

import os
import re
from pathlib import Path

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    # 图片文件
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg',
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
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


async def save_upload_file(file, subdir: str = "") -> str:
    """
    保存上传的文件

    Args:
        file: 上传的文件对象
        subdir: 子目录名称

    Returns:
        相对路径
    """
    import uuid
    from datetime import datetime

    from app.core.config import settings

    # 生成文件名
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}_{unique_id}{ext}"

    # 构建保存路径
    if subdir:
        save_dir = os.path.join(settings.upload_dir, subdir)
    else:
        save_dir = settings.upload_dir

    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, new_filename)

    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 返回相对路径
    if subdir:
        return f"{subdir}/{new_filename}"
    return new_filename
