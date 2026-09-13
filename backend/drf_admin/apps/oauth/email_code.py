"""One-time email codes backed by Django's configured cache."""

from __future__ import annotations

import secrets
import time
from pathlib import Path
from threading import Lock

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail


class EmailCodeError(RuntimeError):
    def __init__(self, message: str, *, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


_lock = Lock()
_captured: dict[str, str] = {}


def _key(purpose: str, email: str) -> str:
    return f"oauth:email-code:{purpose}:{email.strip().lower()}"


def send_code(*, purpose: str, email: str) -> None:
    key = _key(purpose, email)
    cooldown_key = f"{key}:cooldown"
    if cache.get(cooldown_key):
        raise EmailCodeError("验证码发送过于频繁", retry_after=60)
    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(key, {"code": code, "attempts": 0, "expires_at": time.time() + 600}, 600)
    cache.set(cooldown_key, True, 60)
    with _lock:
        _captured[key] = code
    capture_file = getattr(settings, "EMAIL_CAPTURE_FILE", "")
    if capture_file and not getattr(settings, "ENVIRONMENT", "").lower() == "production":
        path = Path(capture_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as capture:
            capture.write(f"{purpose}:{email.strip().lower()}={code}\n")
    if getattr(settings, "EMAIL_HOST", ""):
        send_mail(
            "DV-Admin verification code",
            f"Your verification code is {code}. It expires in 10 minutes.",
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
            [email],
            fail_silently=False,
        )


def verify_code(*, purpose: str, email: str, code: str) -> bool:
    key = _key(purpose, email)
    entry = cache.get(key)
    if not isinstance(entry, dict):
        return False
    attempts = int(entry.get("attempts", 0))
    expires_at = float(entry.get("expires_at", 0))
    remaining = max(1, int(expires_at - time.time())) if expires_at else 600
    if attempts >= 5 or remaining <= 0:
        cache.delete(key)
        return False
    expected = str(entry.get("code", ""))
    if expected != code.strip():
        entry["attempts"] = attempts + 1
        cache.set(key, entry, remaining)
        return False
    cache.delete(key)
    cache.delete(f"{key}:cooldown")
    return True


def captured_code(*, purpose: str, email: str) -> str | None:
    return _captured.get(_key(purpose, email))
