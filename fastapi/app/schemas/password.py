"""Password fields override general text trimming, including legacy login values."""

from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from app.core.config import settings
from app.core.password_policy import validate_new_password


def validate_password(value: str) -> str:
    return validate_new_password(value, settings.password_min_length, settings.password_max_length)


Password = Annotated[str, StringConstraints(strip_whitespace=False)]
NewPassword = Annotated[Password, AfterValidator(validate_password)]
