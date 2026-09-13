"""Email verification code delivery with a local capture adapter."""

from __future__ import annotations

import asyncio
import secrets
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path
from threading import Lock

from app.core.cache_backend import CacheBackend
from app.core.cache_memory import MemoryCache
from app.core.cache_redis import RedisCache
from app.core.config import settings


class EmailCodeError(RuntimeError):
    """Email delivery or throttling failure."""

    def __init__(self, message: str, *, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class EmailCodeService:
    ttl_seconds = 600
    resend_seconds = 60
    max_attempts = 5

    def __init__(self) -> None:
        self._codes: dict[str, tuple[str, float, int]] = {}
        self._last_sent: dict[str, float] = {}
        self._captured: dict[str, str] = {}
        self._lock = Lock()
        self._cache: CacheBackend | None = None
        self._async_lock = asyncio.Lock()

    def _get_cache(self) -> CacheBackend:
        if self._cache is None:
            if settings.is_production and settings.redis_url:
                self._cache = RedisCache()
            else:
                self._cache = MemoryCache()
        return self._cache

    def _key(self, purpose: str, email: str) -> str:
        return f"{purpose}:{email.strip().lower()}"

    def send(self, *, purpose: str, email: str) -> None:
        key = self._key(purpose, email)
        now = time.time()
        with self._lock:
            last = self._last_sent.get(key, 0)
            if now - last < self.resend_seconds:
                raise EmailCodeError("验证码发送过于频繁", retry_after=self.resend_seconds)
            code = f"{secrets.randbelow(1_000_000):06d}"
            self._codes[key] = (code, now + self.ttl_seconds, 0)
            self._last_sent[key] = now
            self._captured[key] = code

        email_host = settings.email_host
        if settings.is_development or email_host is None:
            return
        message = EmailMessage()
        message["Subject"] = "DV-Admin verification code"
        message["From"] = getattr(settings, "email_from", "no-reply@example.com")
        message["To"] = email
        message.set_content(f"Your verification code is {code}. It expires in 10 minutes.")
        email_username = settings.email_username
        with smtplib.SMTP(email_host, settings.email_port, timeout=10) as smtp:
            if getattr(settings, "email_use_tls", False):
                smtp.starttls()
            if email_username:
                smtp.login(email_username, settings.email_password or "")
            smtp.send_message(message)

    def verify(self, *, purpose: str, email: str, code: str) -> bool:
        key = self._key(purpose, email)
        with self._lock:
            entry = self._codes.get(key)
            if not entry:
                return False
            expected, expires_at, attempts = entry
            if time.time() > expires_at or attempts >= self.max_attempts:
                self._codes.pop(key, None)
                return False
            if expected != code.strip():
                self._codes[key] = (expected, expires_at, attempts + 1)
                return False
            self._codes.pop(key, None)
            self._last_sent.pop(key, None)
            return True

    def captured(self, *, purpose: str, email: str) -> str | None:
        """Return the last local code for tests and development tooling."""
        return self._captured.get(self._key(purpose, email))

    def _capture_for_local_test(self, *, purpose: str, email: str, code: str) -> None:
        capture_file = getattr(settings, "email_capture_file", None)
        if not capture_file or settings.is_production:
            return
        path = Path(capture_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as capture:
            capture.write(f"{purpose}:{email.strip().lower()}={code}\n")

    async def asend(self, *, purpose: str, email: str) -> None:
        """Store codes in the configured cache; use Redis for production."""
        async with self._async_lock:
            key = self._key(purpose, email)
            cache = self._get_cache()
            if await cache.exists(f"{key}:cooldown"):
                raise EmailCodeError("验证码发送过于频繁", retry_after=self.resend_seconds)
            code = f"{secrets.randbelow(1_000_000):06d}"
            expires_at = time.time() + self.ttl_seconds
            if not await cache.set(key, {"code": code, "attempts": 0, "expiresAt": expires_at}, self.ttl_seconds):
                raise EmailCodeError("验证码服务暂不可用")
            await cache.set(f"{key}:cooldown", True, self.resend_seconds)
            self._captured[key] = code
            self._capture_for_local_test(purpose=purpose, email=email, code=code)
            email_host = settings.email_host
            if settings.is_development or email_host is None:
                return
            message = EmailMessage()
            message["Subject"] = "DV-Admin verification code"
            message["From"] = getattr(settings, "email_from", "no-reply@example.com")
            message["To"] = email
            message.set_content(f"Your verification code is {code}. It expires in 10 minutes.")
            email_username = settings.email_username
            with smtplib.SMTP(email_host, settings.email_port, timeout=10) as smtp:
                if getattr(settings, "email_use_tls", False):
                    smtp.starttls()
                if email_username:
                    smtp.login(email_username, settings.email_password or "")
                smtp.send_message(message)

    async def averify(self, *, purpose: str, email: str, code: str) -> bool:
        """Verify and consume a cached code, enforcing the five-attempt limit."""
        key = self._key(purpose, email)
        cache = self._get_cache()
        async with self._async_lock:
            entry = await cache.get(key)
            if not isinstance(entry, dict):
                return False
            expires_at = float(entry.get("expiresAt", 0))
            remaining = max(1, int(expires_at - time.time())) if expires_at else self.ttl_seconds
            attempts = int(entry.get("attempts", 0))
            if attempts >= self.max_attempts or remaining <= 0:
                await cache.delete(key)
                return False
            if str(entry.get("code", "")) != code.strip():
                entry["attempts"] = attempts + 1
                await cache.set(key, entry, remaining)
                return False
            await cache.delete(key)
            await cache.delete(f"{key}:cooldown")
            return True


email_code_service = EmailCodeService()
