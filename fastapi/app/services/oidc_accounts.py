"""单点登录外部身份到本地用户的解析：已绑定、按邮箱关联或自动开通。"""

from datetime import datetime, timezone

from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from app.core.config import settings
from app.core.oidc_policy import (
    MESSAGE_EMAIL_AMBIGUOUS,
    MESSAGE_NOT_PROVISIONED,
    MESSAGE_USER_DISABLED,
    NAME_MAX_LENGTH,
    OidcError,
    email_domain_allowed,
    random_secret,
    split_setting,
    username_candidates,
)
from app.db.models.oauth import OidcIdentity, Users
from app.db.models.system import Roles

# 以 "!" 开头的哈希任何口令都无法匹配，开通账号只能通过单点登录或管理员重置密码登录。
UNUSABLE_PASSWORD_PREFIX = "!"


async def _find_identity(issuer: str, subject: str) -> OidcIdentity | None:
    return await OidcIdentity.get_or_none(issuer=issuer, subject=subject).prefetch_related("user")


async def _match_by_email(profile: dict, issuer: str) -> Users | None:
    """只在邮箱已验证时按邮箱关联非超级管理员账号，多个匹配或已绑定同一提供方都拒绝。"""
    if not settings.oidc_match_existing_by_email or not profile["email_verified"]:
        return None
    matches = await Users.filter(is_superuser=False, email__iexact=profile["email"]).limit(2)
    if len(matches) > 1:
        raise OidcError(MESSAGE_EMAIL_AMBIGUOUS)
    if not matches:
        return None
    if await OidcIdentity.filter(issuer=issuer, user_id=matches[0].id).exists():
        raise OidcError(MESSAGE_NOT_PROVISIONED)
    return matches[0]


async def _available_username(profile: dict, issuer: str) -> str:
    # 逐个交给数据库判断占用，保证与唯一索引的大小写规则一致。
    for candidate in username_candidates(profile, issuer):
        if not await Users.filter(username=candidate).exists():
            return candidate
    raise OidcError()


async def _provision_user(profile: dict, issuer: str) -> Users:
    """创建不可用密码的本地账号，并与普通新增用户一样分配默认角色。"""
    username = await _available_username(profile, issuer)
    default_role = await Roles.filter(is_default=1, status=1).select_for_update().first()
    user = await Users.create(
        username=username,
        password=UNUSABLE_PASSWORD_PREFIX + random_secret(),
        name=profile["name"] or username[:NAME_MAX_LENGTH],
        email=profile["email"],
        is_active=1,
    )
    if default_role:
        await user.roles.add(default_role)
    return user


async def _link_identity(profile: dict, issuer: str) -> Users:
    user = await _match_by_email(profile, issuer)
    if user is None:
        allowed_domains = split_setting(settings.oidc_allowed_email_domains)
        if not settings.oidc_auto_provision or not email_domain_allowed(profile, allowed_domains):
            raise OidcError(MESSAGE_NOT_PROVISIONED)
    try:
        async with in_transaction():
            if user is None:
                user = await _provision_user(profile, issuer)
            await OidcIdentity.create(
                issuer=issuer,
                subject=profile["subject"],
                user=user,
                email=profile["email"],
            )
    except IntegrityError:
        # 并发的同一身份已先完成绑定：沿用已提交的绑定，本次创建的账号随事务回滚。
        identity = await _find_identity(issuer, profile["subject"])
        if identity is None:
            raise OidcError() from None
        return identity.user
    return user


async def resolve_oidc_user(profile: dict, issuer: str) -> Users:
    """返回登录用户；从不覆盖已有账号的姓名和邮箱。"""
    identity = await _find_identity(issuer, profile["subject"])
    user = identity.user if identity else await _link_identity(profile, issuer)
    if not user.is_active:
        raise OidcError(MESSAGE_USER_DISABLED)
    return user


async def record_oidc_login(user: Users, issuer: str, subject: str) -> None:
    """只更新登录时间列，避免整行保存覆盖并发修改（例如管理员刚禁用账号）。"""
    now = datetime.now(timezone.utc)
    await OidcIdentity.filter(issuer=issuer, subject=subject).update(last_login_at=now)
    await Users.filter(id=user.id).update(last_login=now)
