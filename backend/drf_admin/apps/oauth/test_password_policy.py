"""New passwords across canonical and compatibility Django serializers."""

from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from drf_admin.apps.information.serializers.centre import ChangePasswordSerializer
from drf_admin.apps.system.models import Users
from drf_admin.apps.system.serializers.users import (
    ResetPasswordSerializer,
    UpdateUserProfileSerializer,
    UsersSerializer,
)


class PasswordPolicyTests(TestCase):
    def test_policy_endpoint_is_authenticated(self):
        client = APIClient()
        url = "/api/v1/information/password-policy"
        self.assertEqual(client.get(url).status_code, 401)
        user = Users.objects.create_user(username="policy-reader", password="old")
        client.force_authenticate(user)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], {"minLength": 15, "maxLength": 128})

    def test_long_unicode_passphrase_and_spaces_survive_all_fields(self):
        user = Users.objects.create_user(username="policy-user", password=" old ")
        password = " 夜晚沿着湖边散步然后回家喝茶 "
        reset = ResetPasswordSerializer(instance=user, data={"password": password, "confirm_password": password})
        self.assertTrue(reset.is_valid(), reset.errors)
        self.assertEqual(reset.validated_data["password"], password)
        change = ChangePasswordSerializer(instance=user, data={
            "old_password": " old ", "new_password": password, "confirm_password": password,
        })
        self.assertTrue(change.is_valid(), change.errors)
        self.assertEqual(change.validated_data["new_password"], password)

    def test_short_password_is_not_accepted_for_reset(self):
        serializer = ResetPasswordSerializer(data={"password": "weak123", "confirm_password": "weak123"})
        self.assertFalse(serializer.is_valid())

    def test_all_write_serializers_reject_invalid_values_without_mutation(self):
        user = Users.objects.create_user(username="policy-old", password=" old ")
        old_hash = user.password
        for value in ("x" * 14, "x" * 129, "    password    "):
            for serializer in (
                ResetPasswordSerializer(instance=user, data={"password": value, "confirm_password": value}),
                ChangePasswordSerializer(instance=user, data={"old_password": " old ", "new_password": value, "confirm_password": value}),
                UpdateUserProfileSerializer(instance=user, data={"current_password": " old ", "new_password": value, "confirm_password": value}),
            ):
                with self.subTest(value_length=len(value), serializer=type(serializer).__name__):
                    self.assertFalse(serializer.is_valid())
        user.refresh_from_db()
        self.assertEqual(user.password, old_hash)

    @override_settings(DEFAULT_PWD="weak123")
    def test_invalid_default_prevents_create_and_import(self):
        from drf_admin.apps.system.models import Permissions
        from drf_admin.apps.system.services.user_import_export import import_users
        from drf_admin.apps.system.test_helpers import create_admin_user
        from drf_admin.apps.system.test_user_import_export import build_import_file

        serializer = UsersSerializer(data={"username": "bad-default-create"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()
        self.assertFalse(Users.objects.filter(username="bad-default-create").exists())
        actor = create_admin_user()
        actor.roles.first().permissions.add(Permissions.objects.create(name="Import", type="BUTTON", perm="system:users:import"))
        with self.assertRaises(ValidationError):
            import_users(build_import_file([["bad-default-import"]]), dept_id=None, current_user=actor)
        self.assertFalse(Users.objects.filter(username="bad-default-import").exists())

    def test_legacy_login_preserves_spaces(self):
        user = Users.objects.create_user(username="legacy-policy", password=" old ")
        response = APIClient().post("/api/v1/oauth/login/", {"username": user.username, "password": " old "}, format="json")
        self.assertEqual(response.status_code, 200)
