"""New-password policy must not alter legacy login input or truncate passphrases."""

import threading
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.security import get_password_hash, verify_password
from app.schemas.oauth import ChangePassword, UserLogin
from app.schemas.system_user import UserCreate, UserPasswordReset


@pytest.mark.parametrize("value", ["short123", "x" * 129, "    password    "])
def test_new_user_rejects_weak_password(value):
    with pytest.raises(ValidationError):
        UserCreate(username="account", password=value)


@pytest.mark.parametrize("value", ["夜晚沿着湖边散步然后回家喝热茶", " an unhurried walk beside the lake ", "z" * 128])
def test_all_new_password_schemas_allow_passphrases_without_trimming(value):
    assert UserCreate(username="account", password=value).password == value
    assert UserPasswordReset(password=value, confirm_password=value).password == value
    changed = ChangePassword(oldPassword=" old ", newPassword=value, confirmPassword=value)
    assert changed.new_password == value
    assert changed.old_password == " old "


def test_login_does_not_retroactively_apply_policy_or_strip_password():
    assert UserLogin(username="account", password=" old ").password == " old "
    assert UserLogin(username="account", password="x").password == "x"


def test_new_hash_uses_django_pbkdf2_without_bcrypt_byte_truncation():
    password = "中文长口令" * 20
    hashed = get_password_hash(password)
    assert hashed.startswith("pbkdf2_sha256$600000$")
    assert verify_password(password, hashed)
    assert not verify_password(password[:-1] + "别", hashed)


def test_authenticated_password_policy_endpoint(auth_client):
    response = auth_client.get("/api/v1/information/password-policy")
    assert response.status_code == 200
    assert response.json()["data"] == {"minLength": 15, "maxLength": 128}


def test_password_policy_requires_authentication(client):
    assert client.get("/api/v1/information/password-policy").status_code == 401


def test_rejected_password_is_not_echoed_in_validation_response(auth_client):
    value = "weak123"
    response = auth_client.put("/api/v1/information/password", json={
        "oldPassword": "old-secret", "newPassword": value, "confirmPassword": value,
    })
    assert response.status_code == 422
    assert value not in response.text and "old-secret" not in response.text


def test_backend_policy_and_licensed_data_copies_match():
    root = Path(__file__).resolve().parents[2]
    fastapi = root / "fastapi/app/core"
    django = root / "backend/drf_admin/utils"
    for name in ("password_policy.py", "data/common-passwords.txt", "data/common-passwords.source.json", "data/LICENSE.seclists"):
        assert (fastapi / name).read_bytes() == (django / name).read_bytes()


async def test_async_hash_and_verify_run_off_event_loop(monkeypatch):
    from app.core import security

    loop_thread = threading.get_ident()
    threads = []

    def hash_probe(password):
        threads.append(threading.get_ident())
        return "hash"

    def verify_probe(password, hashed):
        threads.append(threading.get_ident())
        return True

    monkeypatch.setattr(security, "get_password_hash", hash_probe)
    monkeypatch.setattr(security, "verify_password", verify_probe)
    assert await security.hash_new_password("an unhurried walk beside the lake") == "hash"
    assert await security.verify_password_async("old", "hash")
    assert len(threads) == 2 and all(thread != loop_thread for thread in threads)


def test_legacy_bcrypt_and_pbkdf2_verification():
    from passlib.hash import bcrypt, django_pbkdf2_sha256

    for hashed in (bcrypt.hash(" old "), django_pbkdf2_sha256.using(rounds=390000).hash(" old ")):
        assert verify_password(" old ", hashed)
        assert not verify_password("old", hashed)


async def test_invalid_configured_password_cannot_create_import_or_reset(db, monkeypatch):
    from test_user_service_import_export import build_import_file

    from app.core.config import settings
    from app.core.exceptions import ValidationError as BusinessValidationError
    from app.db.models.oauth import Users
    from app.services.system.user_service import user_service

    monkeypatch.setattr(settings, "default_password", "weak123")
    with pytest.raises(BusinessValidationError):
        await user_service.create(UserCreate(username="bad-default-create"))
    assert not await Users.filter(username="bad-default-create").exists()
    with pytest.raises(BusinessValidationError):
        await user_service.import_users(build_import_file([["bad-default-import"]]))
    assert not await Users.filter(username="bad-default-import").exists()
    user = await Users.create(username="old-policy-user", password=get_password_hash(" old "))
    old_hash = user.password
    with pytest.raises(BusinessValidationError):
        await user_service.reset_password(user.id)
    await user.refresh_from_db()
    assert user.password == old_hash


@pytest.mark.parametrize("value", ["x" * 14, "x" * 129, "    password    "])
def test_all_new_password_schemas_reject_invalid_values(value):
    for schema, values in (
        (UserPasswordReset, {"password": value, "confirm_password": value}),
        (ChangePassword, {"old_password": "old", "new_password": value, "confirm_password": value}),
    ):
        with pytest.raises(ValidationError):
            schema(**values)
