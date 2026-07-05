"""字段读取权限与脱敏规则。"""

from app.db.models.oauth import Users

USER_FIELD_PLAIN_PERMISSION = "system:users:field:plain"
USER_FIELD_WRITE_PERMISSION = "system:users:field:write"
LOG_FIELD_PLAIN_PERMISSION = "system:logs:field:plain"
NOTICE_TARGET_WRITE_PERMISSION = "system:notices:target:write"
MASKED_TEXT = "[已脱敏]"


async def can_view_plain_fields(
    user: Users | None,
    permission_code: str,
    default_when_anonymous: bool = True,
) -> bool:
    """判断当前用户是否可以查看指定资源的敏感字段原文。"""
    if user is None:
        return default_when_anonymous
    if user.is_superuser:
        return True
    permissions = await user.get_permissions()
    return permission_code in permissions


async def can_write_sensitive_user_fields(
    user: Users | None,
    default_when_anonymous: bool = True,
) -> bool:
    """判断当前用户是否可以写入用户敏感字段。"""
    if user is None:
        return default_when_anonymous
    if user.is_superuser:
        return True
    permissions = await user.get_permissions()
    return USER_FIELD_WRITE_PERMISSION in permissions


async def can_write_notice_target_fields(
    user: Users | None,
    default_when_anonymous: bool = True,
) -> bool:
    """判断当前用户是否可以写入通知指定用户目标字段。"""
    if user is None:
        return default_when_anonymous
    if user.is_superuser:
        return True
    permissions = await user.get_permissions()
    return NOTICE_TARGET_WRITE_PERMISSION in permissions


def has_sensitive_user_write(email: str | None, mobile: str | None) -> bool:
    """判断请求是否显式写入了非空用户敏感字段。"""
    return any(value not in (None, "") for value in (email, mobile))


def has_notice_target_write(target_user_ids: list[int] | None) -> bool:
    """判断请求是否显式写入了非空通知指定用户目标字段。"""
    return target_user_ids not in (None, [])


def mask_mobile(value: str | None) -> str | None:
    """手机号保留前三后四，中间脱敏。"""
    if not value:
        return value
    if len(value) < 7:
        return MASKED_TEXT
    return f"{value[:3]}****{value[-4:]}"


def mask_email(value: str | None) -> str | None:
    """邮箱保留首字符和域名，用户名其余部分脱敏。"""
    if not value:
        return value
    local, separator, domain = value.partition("@")
    if not separator or not local:
        return MASKED_TEXT
    return f"{local[0]}{'*' * max(len(local) - 1, 1)}@{domain}"


def mask_ip(value: str | None) -> str | None:
    """IPv4 保留前三段，最后一段脱敏。"""
    if not value:
        return value
    parts = value.split(".")
    if len(parts) != 4 or any(part == "" for part in parts):
        return MASKED_TEXT
    return ".".join([*parts[:3], "*"])


def mask_payload(value: str | None) -> str | None:
    """日志请求体和响应体统一隐藏，避免泄露 token、密码等内容。"""
    return MASKED_TEXT if value else value
