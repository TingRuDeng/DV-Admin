# -*- coding: utf-8 -*-
"""字段读取权限与脱敏规则。"""

from typing import Any

from drf_admin.utils.permissions import RBACPermission

USER_FIELD_PLAIN_PERMISSION = "system:users:field:plain"
USER_FIELD_WRITE_PERMISSION = "system:users:field:write"
LOG_FIELD_PLAIN_PERMISSION = "system:logs:field:plain"
NOTICE_TARGET_WRITE_PERMISSION = "system:notices:target:write"
MASKED_TEXT = "[已脱敏]"


def can_view_plain_fields(user, permission_code: str) -> bool:
    """判断当前用户是否可以查看指定资源的敏感字段原文。"""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return permission_code in RBACPermission.get_user_permissions(user)


def can_write_sensitive_user_fields(user) -> bool:
    """判断当前用户是否可以写入用户敏感字段。"""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return USER_FIELD_WRITE_PERMISSION in RBACPermission.get_user_permissions(user)


def can_write_notice_target_fields(user) -> bool:
    """判断当前用户是否可以写入通知指定用户目标字段。"""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return NOTICE_TARGET_WRITE_PERMISSION in RBACPermission.get_user_permissions(user)


def has_sensitive_user_write(attrs: dict[str, Any]) -> bool:
    """判断请求是否显式写入了非空用户敏感字段。"""
    return any(attrs.get(field) not in (None, "") for field in ("mobile", "email"))


def has_notice_target_write(attrs: dict[str, Any]) -> bool:
    """判断请求是否显式写入了非空通知指定用户目标字段。"""
    target_user_ids = attrs.get("target_user_ids")
    return target_user_ids not in (None, "", [])


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


def apply_user_field_permissions(data: dict[str, Any], user) -> dict[str, Any]:
    """按用户字段读取权限处理用户输出数据。"""
    if can_view_plain_fields(user, USER_FIELD_PLAIN_PERMISSION):
        return data
    data["mobile"] = mask_mobile(data.get("mobile"))
    data["email"] = mask_email(data.get("email"))
    return data


def apply_log_field_permissions(data: dict[str, Any], user) -> dict[str, Any]:
    """按日志字段读取权限处理操作日志输出数据。"""
    if can_view_plain_fields(user, LOG_FIELD_PLAIN_PERMISSION):
        return data
    data["request_body"] = mask_payload(data.get("request_body"))
    data["response_body"] = mask_payload(data.get("response_body"))
    data["ip"] = mask_ip(data.get("ip"))
    return data
