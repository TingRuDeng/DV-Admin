"""Public registration and password recovery routes."""

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.exceptions import DuplicateError, RateLimitError, ValidationError
from app.core.security import hash_new_password
from app.db.models.oauth import Users
from app.db.models.system import Roles
from app.schemas.base import ResponseModel
from app.services.captcha_service import verify_captcha
from app.services.email_code_service import EmailCodeError, email_code_service
from app.services.token_blacklist import token_blacklist_service

router = APIRouter()


class _Payload:
    def __init__(self, data: dict):
        self.data = {str(k): v for k, v in data.items()}

    def get(self, key: str, default=None):
        return self.data.get(key, default)


async def _require_captcha(payload: _Payload, *, consume: bool = True) -> None:
    key = payload.get("captcha_key") or payload.get("captchaKey")
    code = payload.get("captcha_code") or payload.get("captchaCode")
    if settings.is_development and not key and not code:
        return
    if not key or not code or not await verify_captcha(key, code, delete=consume):
        raise ValidationError("图形验证码无效")


@router.post("/email-code/", response_model=ResponseModel[None])
async def send_email_code(request: Request) -> ResponseModel[None]:
    payload = _Payload(await request.json())
    purpose = str(payload.get("purpose", "register"))
    email = str(payload.get("email", "")).strip().lower()
    if purpose not in {"register", "reset_password"} or not email or "@" not in email:
        raise ValidationError("邮箱和用途无效")
    await _require_captcha(payload, consume=False)
    try:
        await email_code_service.asend(purpose=purpose, email=email)
    except EmailCodeError as exc:
        if exc.retry_after is not None:
            raise RateLimitError(str(exc), retry_after=exc.retry_after) from exc
        raise ValidationError(str(exc)) from exc
    return ResponseModel.success()


@router.post("/register/", response_model=ResponseModel[None])
async def register(request: Request) -> ResponseModel[None]:
    payload = _Payload(await request.json())
    username = str(payload.get("username", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    confirm = str(payload.get("confirm_password", payload.get("confirmPassword", "")))
    if not username or not email or "@" not in email:
        raise ValidationError("用户名和邮箱不能为空")
    if password != confirm:
        raise ValidationError("两次输入的密码不一致")
    await _require_captcha(payload)
    if not await email_code_service.averify(purpose="register", email=email, code=str(payload.get("email_code", payload.get("emailCode", "")))):
        raise ValidationError("邮箱验证码无效")
    if await Users.get_or_none(username=username):
        raise DuplicateError("用户名已存在")
    if await Users.get_or_none(email=email):
        raise DuplicateError("邮箱已存在")
    user = await Users.create(
        username=username,
        email=email,
        password=await hash_new_password(password),
        is_active=1,
    )
    role = await Roles.filter(is_default=1, status=1).first()
    if role:
        await user.roles.add(role)
    return ResponseModel.success(message="注册成功")


@router.post("/password/reset/", response_model=ResponseModel[None])
async def reset_password(request: Request) -> ResponseModel[None]:
    payload = _Payload(await request.json())
    username = str(payload.get("username", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("new_password", payload.get("newPassword", "")))
    confirm = str(payload.get("confirm_password", payload.get("confirmPassword", "")))
    if not username or not email or password != confirm:
        raise ValidationError("账号信息或密码无效")
    await _require_captcha(payload)
    if not await email_code_service.averify(purpose="reset_password", email=email, code=str(payload.get("email_code", payload.get("emailCode", "")))):
        raise ValidationError("邮箱验证码无效")
    user = await Users.get_or_none(username=username, email=email)
    if not user:
        raise ValidationError("账号信息或验证码无效")
    user.password = await hash_new_password(password)
    await user.save(update_fields=["password"])
    await token_blacklist_service.revoke_all_user_tokens(user.id, reason="password_reset")
    return ResponseModel.success(message="密码已重置")
