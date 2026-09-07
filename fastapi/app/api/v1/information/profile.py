"""
个人中心 API 路由

提供个人信息、修改密码、修改头像等接口。
"""

import json
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from starlette.concurrency import run_in_threadpool
from tortoise.transactions import in_transaction

from app.api.deps import CurrentUser
from app.core.avatar_validation import validate_avatar_content
from app.core.config import settings
from app.core.exceptions import BusinessError, ValidationError
from app.core.security import hash_new_password, verify_password_async
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import (
    AvatarInfo,
    ChangePassword,
    PasswordPolicy,
    UpdateProfile,
    UserInfo,
    UserProfile,
)
from app.services.token_blacklist import token_blacklist_service
from app.utils.audit import set_audit_object
from app.utils.file import MAX_AVATAR_UPLOAD_SIZE, allowed_file, copy_upload_file, save_upload_file

router = APIRouter()


@router.get("/password-policy", response_model=ResponseModel[PasswordPolicy])
async def get_password_policy(current_user: Users = CurrentUser) -> ResponseModel[PasswordPolicy]:
    return ResponseModel.success(data=PasswordPolicy(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    ))


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
    set_audit_object(
        request,
        "system.users",
        current_user.id,
        changed_fields=list(data.model_dump(exclude_unset=True)),
    )
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
    set_audit_object(
        request,
        "system.users",
        current_user.id,
        changed_fields=["oldPassword", "newPassword", "confirmPassword"],
    )
    if not await verify_password_async(data.old_password, current_user.password):
        raise ValidationError("旧密码错误")

    hashed = await hash_new_password(data.new_password)
    revoked = await token_blacklist_service.revoke_all_user_tokens(
        current_user.id,
        reason="password_change",
    )
    if not revoked:
        raise BusinessError("旧令牌撤销失败，密码未更新")

    current_user.password = hashed
    await current_user.save()

    return ResponseModel.success(message="密码修改成功")


@router.post("/change-avatar/", response_model=ResponseModel[AvatarInfo])
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: Users = CurrentUser,
) -> ResponseModel[AvatarInfo]:
    """上传头像"""
    set_audit_object(request, "system.users", current_user.id, changed_fields=["file"])
    if not file.filename:
        raise ValidationError("文件名不能为空")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValidationError("只能上传图片文件")

    if not allowed_file(file.filename):
        raise ValidationError("不支持的图片格式")

    with BytesIO() as content:
        await copy_upload_file(file, content, max_size=MAX_AVATAR_UPLOAD_SIZE)
        try:
            await run_in_threadpool(validate_avatar_content, content.getvalue(), file.filename)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
    await file.seek(0)

    relative_path = await save_upload_file(
        file,
        subdir="avatar",
        max_size=MAX_AVATAR_UPLOAD_SIZE,
        filename_prefix=f"avatar_{current_user.id}",
    )
    unique_filename = Path(relative_path).name
    upload_path = Path(settings.upload_dir) / "avatar"
    new_avatar_path = upload_path / unique_filename
    old_avatar = current_user.avatar

    try:
        async with in_transaction() as connection:
            current_user.avatar = unique_filename
            await current_user.save(using_db=connection)
    except Exception:
        new_avatar_path.unlink(missing_ok=True)
        current_user.avatar = old_avatar
        raise

    if old_avatar and old_avatar.startswith("avatar_") and old_avatar != unique_filename:
        old_avatar_path = upload_path / Path(old_avatar).name
        old_avatar_path.unlink(missing_ok=True)

    avatar_url = f"/media/avatar/{unique_filename}"

    return ResponseModel.success(
        data=AvatarInfo(avatar=unique_filename, url=avatar_url),
        message="头像上传成功"
    )
