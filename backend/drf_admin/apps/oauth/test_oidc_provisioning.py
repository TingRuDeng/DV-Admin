# -*- coding: utf-8 -*-
"""
单点登录本地账号解析测试：自动开通、邮箱匹配、用户名生成与并发首登
"""

from unittest.mock import patch

from django.db import IntegrityError
from django.test import override_settings

from drf_admin.apps.oauth import oidc_policy as policy
from drf_admin.apps.oauth.models import OidcIdentity
from drf_admin.apps.oauth.services import oidc as oidc_service
from drf_admin.apps.oauth.test_oidc_helpers import ISSUER, SUBJECT, OidcFlowTestCase
from drf_admin.apps.system.models import Roles, Users

IDENTITY_DIGEST = policy.sha256_hex(f"{ISSUER}|{SUBJECT}")


def create_local_user(username, email="alice@example.com", **extra):
    return Users.objects.create_user(
        username=username, password="local-password-123", name=username, email=email, **extra
    )


def linked_user():
    return OidcIdentity.objects.select_related("user").get(issuer=ISSUER, subject=SUBJECT).user


class OidcProvisioningTests(OidcFlowTestCase):
    def test_provisioned_user_gets_default_role_and_unusable_password(self):
        default_role = Roles.objects.create(name="默认角色", code="default", status=1, is_default=1)
        self.assert_login_ok(self.sso_login())

        user = linked_user()
        self.assertEqual((user.username, user.name, user.email), ("alice", "Alice", "alice@example.com"))
        self.assertEqual(user.is_active, 1)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(list(user.roles.all()), [default_role])

        response = self.client.post(
            "/api/v1/oauth/login/", {"username": "alice", "password": "any-password"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 40000)
        self.assertIn("用户名或密码错误", str(response.json()["errors"]))

    def test_linked_disabled_user_is_rejected(self):
        self.assert_login_ok(self.sso_login())
        Users.objects.filter(pk=linked_user().pk).update(is_active=0)
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_USER_DISABLED)

    @override_settings(OIDC_AUTO_PROVISION=False)
    def test_auto_provision_off_rejects_unknown_identity(self):
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_NOT_PROVISIONED)
        self.assertFalse(Users.objects.exists())

    def test_allowed_email_domains(self):
        with self.settings(OIDC_ALLOWED_EMAIL_DOMAINS="corp.example.com, other.example.com"):
            self.assert_oidc_error(self.sso_login(), policy.MESSAGE_NOT_PROVISIONED)
            unverified = self.sso_login(email="bob@corp.example.com", email_verified=False)
            self.assert_oidc_error(unverified, policy.MESSAGE_NOT_PROVISIONED)
            self.assertFalse(Users.objects.exists())
            self.assert_login_ok(self.sso_login(email="Bob@Corp.Example.com"))
        self.assertEqual(linked_user().email, "bob@corp.example.com")

    def test_name_falls_back_to_username(self):
        self.assert_login_ok(self.sso_login(name=None, preferred_username=None, email=None))
        user = linked_user()
        self.assertEqual(user.username, f"oidc_{IDENTITY_DIGEST[:12]}")
        self.assertEqual(user.name, user.username[: policy.NAME_MAX_LENGTH])
        self.assertEqual(user.email, "")


class OidcUsernameTests(OidcFlowTestCase):
    def test_taken_username_gets_identity_suffix(self):
        create_local_user("alice", email="someone@example.com")
        self.assert_login_ok(self.sso_login())
        self.assertEqual(linked_user().username, f"alice_{IDENTITY_DIGEST[:6]}")

    def test_numeric_and_mobile_like_usernames_are_skipped(self):
        self.assert_login_ok(self.sso_login(preferred_username="12345678", email="bob@example.com"))
        self.assertEqual(linked_user().username, "bob")

    def test_mobile_like_preferred_and_numeric_email_fall_back_to_hash(self):
        self.assert_login_ok(self.sso_login(preferred_username="13800138000", email="123456@example.com"))
        self.assertEqual(linked_user().username, f"oidc_{IDENTITY_DIGEST[:12]}")


@override_settings(OIDC_MATCH_EXISTING_BY_EMAIL=True)
class OidcEmailMatchTests(OidcFlowTestCase):
    def test_single_verified_match_is_linked_without_overwriting_profile(self):
        existing = create_local_user("local-alice", email="Alice@Example.com")
        user_count = Users.objects.count()
        self.assert_login_ok(self.sso_login(name="From IdP"))

        self.assertEqual(Users.objects.count(), user_count)
        user = linked_user()
        self.assertEqual(user.pk, existing.pk)
        self.assertEqual((user.name, user.email), (existing.name, existing.email))

    def test_unverified_email_provisions_new_user(self):
        existing = create_local_user("local-alice")
        self.assert_login_ok(self.sso_login(email_verified=False))
        self.assertNotEqual(linked_user().pk, existing.pk)

    @override_settings(OIDC_AUTO_PROVISION=False)
    def test_unverified_email_without_auto_provision_is_rejected(self):
        create_local_user("local-alice")
        self.assert_oidc_error(self.sso_login(email_verified=False), policy.MESSAGE_NOT_PROVISIONED)

    def test_multiple_matches_are_ambiguous(self):
        create_local_user("local-alice")
        create_local_user("other-alice", email="ALICE@example.com")
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_EMAIL_AMBIGUOUS)
        self.assertFalse(OidcIdentity.objects.exists())

    def test_superuser_is_never_matched(self):
        admin = create_local_user("admin", is_superuser=True, is_staff=True)
        self.assert_login_ok(self.sso_login())
        self.assertNotEqual(linked_user().pk, admin.pk)
        self.assertFalse(admin.oidc_identities.exists())

    def test_match_already_bound_to_same_issuer_is_rejected(self):
        existing = create_local_user("local-alice")
        OidcIdentity.objects.create(issuer=ISSUER, subject="another-subject", user=existing)
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_NOT_PROVISIONED)

    def test_inactive_match_is_linked_but_login_rejected(self):
        existing = create_local_user("local-alice", is_active=0)
        self.assert_oidc_error(self.sso_login(), policy.MESSAGE_USER_DISABLED)
        self.assertEqual(linked_user().pk, existing.pk)


class OidcConcurrentFirstLoginTests(OidcFlowTestCase):
    def test_integrity_error_reuses_identity_written_by_concurrent_login(self):
        winner = create_local_user("winner", email="winner@example.com")
        original = oidc_service._existing_user

        def concurrent_insert(config, issuer, profile):
            OidcIdentity.objects.create(issuer=issuer, subject=profile["subject"], user=winner)
            return original(config, issuer, profile)

        with patch.object(oidc_service, "_existing_user", side_effect=concurrent_insert):
            self.assert_login_ok(self.sso_login())

        self.assertEqual(OidcIdentity.objects.count(), 1)
        self.assertEqual(linked_user().pk, winner.pk)
        self.assertFalse(Users.objects.filter(username="alice").exists())
        self.assertIsNotNone(OidcIdentity.objects.get().last_login_at)

    def test_integrity_error_without_identity_is_provider_error(self):
        with patch.object(oidc_service, "_create_user", side_effect=IntegrityError("race")):
            self.assert_oidc_error(self.sso_login(), policy.MESSAGE_PROVIDER_FAILED)
        self.assertFalse(OidcIdentity.objects.exists())
