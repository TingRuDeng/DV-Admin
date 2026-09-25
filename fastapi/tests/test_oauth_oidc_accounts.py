"""OIDC 外部身份到本地账号的解析：绑定复用、邮箱关联、自动开通、禁用与并发幂等。"""

import pytest
from oidc_fixtures import ISSUER, assert_oidc_error, sso_login

from app.core.config import Settings, settings
from app.core.oidc_policy import (
    MESSAGE_EMAIL_AMBIGUOUS,
    MESSAGE_NOT_PROVISIONED,
    MESSAGE_PROVIDER_FAILED,
    MESSAGE_USER_DISABLED,
    username_candidates,
)
from app.core.security import decode_token, get_password_hash
from app.db.models.oauth import OidcIdentity, Users
from app.db.models.system import Roles
from app.services import oidc_accounts

pytest_plugins = ["oidc_fixtures", "token_blacklist_fixtures"]

LOCAL_PASSWORD = "Local-account-passphrase-2026"


def create_user(run, username: str, **fields) -> Users:
    values = {
        "password": get_password_hash(LOCAL_PASSWORD),
        "name": "本地用户",
        "email": None,
        "is_active": 1,
    }
    values.update(fields)
    return run(Users.create(username=username, **values))


def token_user_id(response) -> int:
    assert response.status_code == 200, response.text
    return int(decode_token(response.json()["data"]["accessToken"])["sub"])


def enable_email_matching(monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_match_existing_by_email", True)


def test_linked_disabled_user_is_rejected(client, db, fake_idp, run):
    user = create_user(run, "disabled", is_active=0)
    run(OidcIdentity.create(issuer=ISSUER, subject="idp-user-1", user=user))

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_USER_DISABLED)
    assert run(Users.all().count()) == 1


def test_linked_user_profile_is_never_overwritten(client, db, fake_idp, run):
    user = create_user(run, "legacy", name="原姓名", email="old@example.com")
    run(OidcIdentity.create(issuer=ISSUER, subject="idp-user-1", user=user))

    assert token_user_id(sso_login(client, fake_idp)) == user.id
    reloaded = run(Users.get(id=user.id))
    assert (reloaded.name, reloaded.email) == ("原姓名", "old@example.com")


def test_auto_provision_disabled_rejects_unknown_identity(client, db, fake_idp, monkeypatch, run):
    monkeypatch.setattr(settings, "oidc_auto_provision", False)

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_NOT_PROVISIONED)
    assert run(Users.all().count()) == 0


@pytest.mark.parametrize(
    ("domains", "claims", "allowed"),
    [
        ("corp.example", {}, False),
        ("corp.example, example.com", {}, True),
        ("EXAMPLE.COM", {}, True),
        ("example.com", {"email_verified": False}, False),
    ],
)
def test_allowed_email_domains_gate_provisioning(
    client, db, fake_idp, monkeypatch, run, domains, claims, allowed
):
    monkeypatch.setattr(settings, "oidc_allowed_email_domains", domains)
    fake_idp.claims.update(claims)

    response = sso_login(client, fake_idp)

    if allowed:
        assert token_user_id(response) == run(Users.get(username="alice")).id
    else:
        assert_oidc_error(response, MESSAGE_NOT_PROVISIONED)
        assert run(Users.all().count()) == 0


def test_email_match_links_single_existing_user(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    existing = create_user(run, "alice.local", name="本地姓名", email="Alice@Example.com")

    assert token_user_id(sso_login(client, fake_idp)) == existing.id
    identity = run(OidcIdentity.get(issuer=ISSUER, subject="idp-user-1"))
    assert identity.user_id == existing.id
    reloaded = run(Users.get(id=existing.id))
    assert (reloaded.name, reloaded.email) == ("本地姓名", "Alice@Example.com")
    assert run(Users.all().count()) == 1


def test_email_match_ignores_unverified_email(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    existing = create_user(run, "alice.local", email="alice@example.com")
    fake_idp.claims["email_verified"] = False

    new_user_id = token_user_id(sso_login(client, fake_idp))
    assert new_user_id != existing.id
    assert run(Users.get(id=new_user_id)).username == "alice"


def test_email_match_unverified_without_provisioning_is_rejected(
    client, db, fake_idp, monkeypatch, run
):
    enable_email_matching(monkeypatch)
    monkeypatch.setattr(settings, "oidc_auto_provision", False)
    create_user(run, "alice.local", email="alice@example.com")
    fake_idp.claims["email_verified"] = False

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_NOT_PROVISIONED)


def test_email_match_with_two_users_is_ambiguous(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    create_user(run, "alice.one", email="alice@example.com")
    create_user(run, "alice.two", email="ALICE@example.com")

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_EMAIL_AMBIGUOUS)
    assert run(OidcIdentity.all().count()) == 0


def test_email_match_ignores_superuser(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    admin = create_user(run, "root", email="alice@example.com", is_superuser=True)

    user_id = token_user_id(sso_login(client, fake_idp))
    assert user_id != admin.id
    assert not run(Users.get(id=user_id)).is_superuser


def test_email_match_already_linked_to_issuer_is_rejected(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    existing = create_user(run, "alice.local", email="alice@example.com")
    run(OidcIdentity.create(issuer=ISSUER, subject="another-subject", user=existing))

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_NOT_PROVISIONED)
    assert run(OidcIdentity.all().count()) == 1


def test_email_match_links_disabled_user_then_rejects(client, db, fake_idp, monkeypatch, run):
    enable_email_matching(monkeypatch)
    existing = create_user(run, "alice.local", email="alice@example.com", is_active=0)

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_USER_DISABLED)
    assert run(OidcIdentity.get(issuer=ISSUER, subject="idp-user-1")).user_id == existing.id


def test_username_collision_uses_suffixed_candidate(client, db, fake_idp, run):
    create_user(run, "alice")

    user = run(Users.get(id=token_user_id(sso_login(client, fake_idp))))
    profile = {"subject": "idp-user-1", "preferred_username": "alice", "email": "alice@example.com"}
    assert user.username == username_candidates(profile, ISSUER)[1]
    assert user.username.startswith("alice_") and len(user.username) == len("alice_") + 6


def test_numeric_and_mobile_like_usernames_are_skipped(client, db, fake_idp, run):
    fake_idp.claims.update(
        {"preferred_username": "20260925", "email": "13800138000@example.com", "name": ""}
    )

    user = run(Users.get(id=token_user_id(sso_login(client, fake_idp))))
    assert user.username.startswith("oidc_") and len(user.username) == len("oidc_") + 12
    assert user.name == "20260925"
    assert user.email == "13800138000@example.com"


def test_name_falls_back_to_username_when_claims_have_none(client, db, fake_idp, run):
    fake_idp.claims.update({"preferred_username": "", "email": "", "name": ""})

    user = run(Users.get(id=token_user_id(sso_login(client, fake_idp))))
    assert user.username.startswith("oidc_")
    assert user.name == user.username[:20]
    assert user.email == ""


def test_provisioned_user_has_default_role_and_unusable_password(client, db, fake_idp, run):
    default_role = run(Roles.create(name="默认角色", code="default", is_default=1, status=1))
    run(Roles.create(name="普通角色", code="plain", is_default=0, status=1))

    tokens = sso_login(client, fake_idp).json()["data"]
    user = run(Users.get(username="alice"))
    run(user.fetch_related("roles"))
    assert [role.id for role in user.roles] == [default_role.id]
    assert user.password.startswith("!") and len(user.password) > 32
    assert (user.name, user.email, user.is_active, user.is_superuser) == (
        "Alice", "alice@example.com", 1, False
    )

    for password in ("", "!", user.password, LOCAL_PASSWORD):
        response = client.post(
            "/api/v1/oauth/login/", json={"username": "alice", "password": password}
        )
        assert response.status_code == 401
        assert response.json() == {"code": 40000, "message": "用户名或密码错误", "data": None}

    change = client.put(
        "/api/v1/information/password",
        json={
            "oldPassword": "anything",
            "newPassword": "Brand-new-passphrase-2026",
            "confirmPassword": "Brand-new-passphrase-2026",
        },
        headers={"Authorization": f"Bearer {tokens['accessToken']}"},
    )
    assert change.status_code == 400
    assert change.json()["message"] == "旧密码错误"


def test_disabled_default_role_is_not_assigned(client, db, fake_idp, run):
    run(Roles.create(name="停用默认角色", code="default", is_default=1, status=0))

    token_user_id(sso_login(client, fake_idp))
    user = run(Users.get(username="alice"))
    run(user.fetch_related("roles"))
    assert list(user.roles) == []


def test_concurrent_identity_creation_reuses_committed_identity(
    client, db, fake_idp, monkeypatch, run
):
    winner = create_user(run, "winner")
    original = oidc_accounts._match_by_email

    async def racing_match(profile, issuer):
        # 另一个请求在本次查找之后、插入之前完成了同一外部身份的绑定。
        await OidcIdentity.create(issuer=issuer, subject=profile["subject"], user=winner)
        return await original(profile, issuer)

    monkeypatch.setattr(oidc_accounts, "_match_by_email", racing_match)

    assert token_user_id(sso_login(client, fake_idp)) == winner.id
    assert run(Users.all().count()) == 1
    assert run(OidcIdentity.all().count()) == 1


def test_username_race_without_identity_fails_closed(client, db, fake_idp, monkeypatch, run):
    create_user(run, "taken")

    async def stale_username(profile, issuer):
        return "taken"

    monkeypatch.setattr(oidc_accounts, "_available_username", stale_username)

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_PROVIDER_FAILED)
    assert run(Users.all().count()) == 1
    assert run(OidcIdentity.all().count()) == 0


def test_all_username_candidates_taken_fails_closed(client, db, fake_idp, run):
    profile = {"subject": "idp-user-1", "preferred_username": "alice", "email": "alice@example.com"}
    for candidate in username_candidates(profile, ISSUER):
        create_user(run, candidate)

    assert_oidc_error(sso_login(client, fake_idp), MESSAGE_PROVIDER_FAILED)
    assert run(OidcIdentity.all().count()) == 0


def test_identity_is_removed_with_its_user(client, db, fake_idp, run):
    user_id = token_user_id(sso_login(client, fake_idp))

    run(Users.filter(id=user_id).delete())
    assert run(OidcIdentity.all().count()) == 0


def build_settings(**values) -> Settings:
    base = {
        "_env_file": None,
        "DEFAULT_PASSWORD": "ChangeMe!2026-strong-default",
        "SECRET_KEY": "oidc-settings-Test-key-0123456789-abcdefghijklmnopqrstuvwxyz-ABCDEFGH",
    }
    base.update(values)
    return Settings(**base)


@pytest.mark.parametrize(
    "overrides",
    [
        {"OIDC_ISSUER": ""},
        {"OIDC_CLIENT_ID": ""},
        {"OIDC_REDIRECT_URI": ""},
        {"OIDC_ISSUER": "http://idp.example.test"},
        {"OIDC_REDIRECT_URI": "http://admin.example.test/oidc/callback"},
    ],
)
def test_production_rejects_invalid_oidc_settings(overrides):
    values = {
        "APP_ENV": "production",
        "DEBUG": False,
        "OIDC_ENABLED": True,
        "OIDC_ISSUER": "https://idp.example.test",
        "OIDC_CLIENT_ID": "dv-admin",
        "OIDC_REDIRECT_URI": "https://admin.example.test/oidc/callback",
    }
    values.update(overrides)

    with pytest.raises(ValueError, match="OIDC"):
        build_settings(**values)


def test_oidc_settings_defaults_and_valid_production_config():
    defaults = build_settings()
    assert defaults.oidc_enabled is False
    assert defaults.oidc_scopes == "openid profile email"
    assert defaults.oidc_auto_provision is True
    assert defaults.oidc_match_existing_by_email is False
    assert defaults.oidc_config_errors == []

    production = build_settings(
        APP_ENV="production",
        DEBUG=False,
        OIDC_ENABLED=True,
        OIDC_ISSUER="https://idp.example.test",
        OIDC_CLIENT_ID="dv-admin",
        OIDC_REDIRECT_URI="https://admin.example.test/oidc/callback",
    )
    assert production.oidc_config_errors == []
    assert build_settings(APP_ENV="production", DEBUG=False).oidc_config_errors == []


def test_non_production_invalid_oidc_settings_only_fail_requests():
    development = build_settings(OIDC_ENABLED=True, OIDC_ISSUER="http://localhost:8080/realms/dv")

    assert development.oidc_config_errors == ["OIDC_CLIENT_ID 未配置", "OIDC_REDIRECT_URI 未配置"]
