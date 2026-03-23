"""
个人中心 API 路由

提供个人信息、修改密码、修改头像等接口。
"""

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.security import get_password_hash, verify_password
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import ChangePassword, UpdateProfile, UserInfo, UserProfile
from app.utils.file import allowed_file, secure_filename

router = APIRouter()


async def get_user_info_response(current_user: Users) -> UserInfo:
    """获取用户信息响应"""
    dept_name = None
    if current_user.dept_id:
        from app.db.models.system import Departments
        dept = await Departments.get_or_none(id=current_user.dept_id)
        if dept:
            dept_name = dept.name

    await current_user.fetch_related("roles")
    role_names = "、".join([role.name for role in current_user.roles])
    roles_json = json.dumps([role.name for role in current_user.roles])

    permissions = await current_user.get_permissions()

    avatar = current_user.avatar
    if avatar and not avatar.startswith(("http", "/media")):
        avatar = f"/media/{avatar}"

    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email if current_user.email else "",
        mobile=current_user.mobile if current_user.mobile else "",
        avatar=avatar,
        gender=current_user.gender,
        is_active=current_user.is_active,
        dept_id=current_user.dept_id,
        dept_name=dept_name if dept_name else "",
        role_names=role_names,
        roles=roles_json,
        perms=permissions,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get("/profile/", response_model=ResponseModel[UserProfile])
async def get_user_profile(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[UserProfile]:
    """获取用户个人资料"""
    dept_name = None
    if current_user.dept_id:
        from app.db.models.system import Departments
        dept = await Departments.get_or_none(id=current_user.dept_id)
        if dept:
            dept_name = dept.name

    await current_user.fetch_related("roles")
    role_names = ",".join([role.name for role in current_user.roles])
    roles = [{"id": role.id, "name": role.name, "code": role.code} for role in current_user.roles]
    permissions = await current_user.get_permissions()

    avatar = current_user.avatar
    if avatar and not avatar.startswith(("http", "/media")):
        avatar = f"/media/{avatar}"

    user_profile = UserProfile(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email,
        mobile=current_user.mobile,
        avatar=avatar,
        gender=current_user.gender,
        is_active=current_user.is_active,
        dept_id=current_user.dept_id,
        dept_name=dept_name,
        role_names=role_names,
        permissions=permissions,
        roles=roles,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
    return ResponseModel.success(data=user_profile)


@router.put("/profile/", response_model=ResponseModel[UserInfo])
async def update_profile(
    request: Request,
    data: UpdateProfile,
    current_user: Users = CurrentUser,
) -> ResponseModel[UserInfo]:
    """修改个人信息"""
    if data.name is not None:
        current_user.name = data.name
    if data.email is not None:
        current_user.email = data.email
    if data.mobile is not None and data.mobile != current_user.mobile:
        if await Users.filter(mobile=data.mobile).exists():
            raise ValidationError("手机号已存在")
        current_user.mobile = data.mobile
    if data.gender is not None:
        current_user.gender = data.gender
    if data.avatar is not None:
        current_user.avatar = data.avatar

    await current_user.save()

    user_info = await get_user_info_response(current_user)
    return ResponseModel.success(data=user_info)


@router.put("/password", response_model=ResponseModel[None])
async def change_password(
    request: Request,
    data: ChangePassword,
    current_user: Users = CurrentUser,
) -> ResponseModel[None]:
    """修改密码"""
    if not verify_password(data.old_password, current_user.password):
        raise ValidationError("旧密码错误")

    current_user.password = get_password_hash(data.new_password)
    await current_user.save()

    return ResponseModel.success(message="密码修改成功")


@router.post("/change-avatar/", response_model=ResponseModel[dict])
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: Users = CurrentUser,
) -> ResponseModel[dict]:
    """上传头像"""
    if not file.filename:
        raise ValidationError("文件名不能为空")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValidationError("只能上传图片文件")

    if not allowed_file(file.filename):
        raise ValidationError("不支持的图片格式")

    file_content = await file.read()

    if len(file_content) > 2 * 1024 * 1024:
        raise ValidationError("头像文件大小不能超过2MB")

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = filename.rsplit('.', 1)
    unique_filename = f"avatar_{current_user.id}_{timestamp}.{ext}"

    upload_path = Path(settings.upload_dir) / "avatar"
    upload_path.mkdir(parents=True, exist_ok=True)

    file_path = upload_path / unique_filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    if current_user.avatar and current_user.avatar.startswith("avatar_"):
        old_avatar_path = upload_path / current_user.avatar
        if old_avatar_path.exists():
            old_avatar_path.unlink()

    current_user.avatar = unique_filename
    await current_user.save()

    avatar_url = f"/media/avatar/{unique_filename}"

    return ResponseModel.success(
        data={
            "avatar": unique_filename,
            "url": avatar_url
        },
        message="头像上传成功"
    )
