"""Apply the shared policy at every API password-write boundary."""

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from drf_admin.utils.password_policy import validate_new_password


class SharedPasswordValidator:
    def validate(self, password, user=None):
        try:
            validate_new_password(password, settings.PASSWORD_MIN_LENGTH, settings.PASSWORD_MAX_LENGTH)
        except ValueError as exc:
            raise DjangoValidationError(str(exc), code="password_policy") from exc

    def get_help_text(self):
        return f"新密码为 {settings.PASSWORD_MIN_LENGTH}-{settings.PASSWORD_MAX_LENGTH} 个字符，不得使用常见密码。"


def validate_password(value: str) -> str:
    try:
        return validate_new_password(
            value, settings.PASSWORD_MIN_LENGTH, settings.PASSWORD_MAX_LENGTH
        )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
