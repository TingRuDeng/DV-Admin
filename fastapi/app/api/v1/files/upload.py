# -*- coding: utf-8 -*-
"""
文件上传 API 路由

提供文件上传、删除等接口。
"""

import os
from fastapi import APIRouter, UploadFile, File, Request, Query

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.schemas.base import ResponseModel
from app.utils.file import save_upload_file

router = APIRouter()


@router.post("/", response_model=ResponseModel[dict])
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
) -> ResponseModel[dict]:
    """
    上传文件
    """
    # 保存文件
    relative_path = await save_upload_file(file, "files")
    if not relative_path:
        raise ValidationError("文件上传失败")

    # 构建完整URL
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/media/{relative_path}"

    return ResponseModel.success(
        data={
            "name": file.filename,
            "url": file_url,
        },
        message="文件上传成功"
    )


@router.delete("/", response_model=ResponseModel[None])
async def delete_file(
    request: Request,
    filePath: str = Query(..., alias="filePath"),
) -> ResponseModel[None]:
    """
    删除文件
    """
    # 安全检查：确保文件路径在 uploads 目录下
    if ".." in filePath or filePath.startswith("/"):
        raise ValidationError("非法的文件路径")

    # 构建完整路径
    full_path = os.path.join(settings.upload_dir, filePath)
    full_path = os.path.abspath(full_path)
    upload_dir = os.path.abspath(settings.upload_dir)

    # 确保文件在 uploads 目录下
    if not full_path.startswith(upload_dir):
        raise ValidationError("非法的文件路径")

    # 删除文件
    if os.path.exists(full_path):
        os.remove(full_path)
        return ResponseModel.success(message="文件删除成功")
    else:
        raise ValidationError("文件不存在")
