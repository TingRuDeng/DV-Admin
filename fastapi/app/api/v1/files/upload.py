"""
文件上传 API 路由

提供文件上传、删除等接口。
"""

from pathlib import Path, PurePosixPath

from fastapi import APIRouter, File, Query, Request, UploadFile

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.exceptions import PermissionDenied, ValidationError
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.utils.file import allowed_file, save_upload_file

router = APIRouter()
USER_FILE_ROOT = "files"


def user_upload_subdir(user_id: int) -> str:
    """按用户隔离上传目录，避免不同用户共享同一删除边界。"""
    return f"{USER_FILE_ROOT}/{user_id}"


def normalize_file_path(file_path: str) -> str:
    """校验并规范化上传文件相对路径。"""
    if not file_path or file_path != file_path.strip():
        raise ValidationError("非法的文件路径")
    if "://" in file_path or file_path.startswith("/") or "\\" in file_path:
        raise ValidationError("非法的文件路径")

    relative_path = PurePosixPath(file_path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValidationError("非法的文件路径")
    return relative_path.as_posix()


def ensure_file_owner(file_path: str, user_id: int) -> None:
    """删除前确认文件路径属于当前用户目录。"""
    if not file_path.startswith(f"{user_upload_subdir(user_id)}/"):
        raise PermissionDenied("无权删除该文件")


def resolve_upload_path(file_path: str) -> Path:
    """把相对路径解析到上传根目录，并阻止越权目录穿透。"""
    upload_dir = Path(settings.upload_dir).resolve()
    full_path = (upload_dir / file_path).resolve()
    try:
        full_path.relative_to(upload_dir)
    except ValueError as exc:
        raise ValidationError("非法的文件路径") from exc
    return full_path


@router.post("/", response_model=ResponseModel[dict])
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: Users = CurrentUser,
) -> ResponseModel[dict]:
    """
    上传文件
    """
    if not file.filename:
        raise ValidationError("文件名不能为空")
    if not allowed_file(file.filename):
        raise ValidationError("不支持的文件类型")

    # 上传文件按用户目录保存，删除时可用相同边界做归属校验。
    relative_path = await save_upload_file(
        file,
        user_upload_subdir(current_user.id),
        max_size=settings.max_upload_size,
    )
    if not relative_path:
        raise ValidationError("文件上传失败")

    # 构建完整URL
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/media/{relative_path}"

    return ResponseModel.success(
        data={
            "name": file.filename,
            "url": file_url,
            "path": relative_path,
        },
        message="文件上传成功"
    )


@router.delete("/", response_model=ResponseModel[None])
async def delete_file(
    request: Request,
    filePath: str = Query(..., alias="filePath"),
    current_user: Users = CurrentUser,
) -> ResponseModel[None]:
    """
    删除文件
    """
    normalized_path = normalize_file_path(filePath)
    ensure_file_owner(normalized_path, current_user.id)
    full_path = resolve_upload_path(normalized_path)

    if full_path.exists() and full_path.is_file():
        full_path.unlink()
        return ResponseModel.success(message="文件删除成功")
    raise ValidationError("文件不存在")
