from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from drf_admin.apps.oauth.email_code import captured_code, send_code, verify_code
from drf_admin.apps.oauth.test_helpers import create_oauth_user
from drf_admin.apps.system.models import Roles, Users


class EmailCodeTests(TestCase):
    def tearDown(self):
        cache.clear()

    @patch("drf_admin.apps.oauth.email_code.send_mail")
    def test_code_is_one_time_and_captured_without_smtp(self, send_mail):
        send_code(purpose="register", email="user@example.com")
        code = captured_code(purpose="register", email="user@example.com")
        assert code
        assert verify_code(purpose="register", email="user@example.com", code=code)
        assert not verify_code(purpose="register", email="user@example.com", code=code)
        send_mail.assert_not_called()

    def test_public_captcha_route_returns_shared_fields(self):
        response = APIClient().get("/api/v1/oauth/captcha/")
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 20000
        assert "captchaKey" in body["data"]
        assert body["data"]["captchaBase64"].startswith("data:image/png;base64,")

    @patch("drf_admin.apps.oauth.email_code.send_mail")
    def test_registration_creates_active_default_role_user(self, send_mail):
        role = Roles.objects.create(name="Public default", code="public-default", is_default=1, status=1)
        client = APIClient()
        captcha = client.get("/api/v1/oauth/captcha/").json()["data"]
        captcha_code = cache.get(f"oauth:captcha:{captcha['captchaKey']}")
        send_code(purpose="register", email="new@example.com")
        email_code = captured_code(purpose="register", email="new@example.com")
        response = client.post("/api/v1/oauth/register/", {
            "username": "new-user",
            "email": "new@example.com",
            "password": "a sufficiently long passphrase",
            "confirmPassword": "a sufficiently long passphrase",
            "captchaKey": captcha["captchaKey"],
            "captchaCode": captcha_code,
            "emailCode": email_code,
        }, format="json")
        assert response.status_code == 200, response.content
        user = Users.objects.get(username="new-user")
        assert user.is_active == 1
        assert user.roles.filter(pk=role.pk).exists()
        send_mail.assert_not_called()

    @patch("drf_admin.apps.oauth.email_code.send_mail")
    def test_email_code_resend_returns_retry_after(self, send_mail):
        client = APIClient()
        payload = {"purpose": "register", "email": "throttle@example.com"}
        assert client.post("/api/v1/oauth/email-code/", payload, format="json").status_code == 200
        response = client.post("/api/v1/oauth/email-code/", payload, format="json")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response["Retry-After"] == "60"
        assert response.json()["code"] == 429
        send_mail.assert_not_called()

    @patch("drf_admin.apps.oauth.email_code.send_mail")
    def test_password_reset_revokes_existing_refresh_token(self, send_mail):
        user = create_oauth_user(username="reset-user", password="old sufficiently long passphrase")
        user.email = "reset@example.com"
        user.save(update_fields=["email"])
        login = self.client.post(
            "/api/v1/oauth/login/",
            {"username": user.username, "password": "old sufficiently long passphrase"},
            format="json",
        )
        assert login.status_code == 200
        refresh_token = login.data["data"]["refreshToken"]
        captcha = self.client.get("/api/v1/oauth/captcha/").json()["data"]
        captcha_code = cache.get(f"oauth:captcha:{captcha['captchaKey']}")
        send_code(purpose="reset_password", email=user.email)
        email_code = captured_code(purpose="reset_password", email=user.email)
        response = self.client.post("/api/v1/oauth/password/reset/", {
            "username": user.username,
            "email": user.email,
            "newPassword": "new sufficiently long passphrase",
            "confirmPassword": "new sufficiently long passphrase",
            "captchaKey": captcha["captchaKey"],
            "captchaCode": captcha_code,
            "emailCode": email_code,
        }, format="json")
        assert response.status_code == 200, response.content
        replay = self.client.post("/api/v1/oauth/refresh-token/", {"refreshToken": refresh_token}, format="json")
        assert replay.status_code == status.HTTP_401_UNAUTHORIZED
        send_mail.assert_not_called()
