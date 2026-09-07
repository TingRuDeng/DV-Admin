"""Shared new-password policy; keep both backend copies byte-identical."""

import hashlib
import unicodedata
from functools import lru_cache
from pathlib import Path

MIN_LENGTH = 15
MAX_LENGTH = 128
BLOCKLIST_SHA256 = "4adb3f0afb4a10cf19ebe48d8c69a46f934bbc8d77c694c210564f9583e7f4ba"


def validate_bounds(min_length: int, max_length: int) -> None:
    if not MIN_LENGTH <= min_length <= max_length <= MAX_LENGTH:
        raise ValueError("Password bounds must satisfy 15 <= min <= max <= 128")


@lru_cache(maxsize=1)
def common_passwords() -> frozenset[str]:
    content = (Path(__file__).parent / "data" / "common-passwords.txt").read_bytes()
    if hashlib.sha256(content).hexdigest() != BLOCKLIST_SHA256:
        raise RuntimeError("Password blocklist integrity check failed")
    return frozenset(
        unicodedata.normalize("NFKC", line).strip().casefold()
        for line in content.decode("utf-8").splitlines()
    )


def validate_new_password(
    password: str, min_length: int = MIN_LENGTH, max_length: int = MAX_LENGTH
) -> str:
    validate_bounds(min_length, max_length)
    if not min_length <= len(password) <= max_length:
        raise ValueError(f"密码长度必须为 {min_length}–{max_length} 个字符")
    # Normalize only the deny-list lookup, never the password that will be hashed.
    candidate = unicodedata.normalize("NFKC", password).strip().casefold()
    if not candidate or candidate in common_passwords():
        raise ValueError("请勿使用常见密码")
    return password
