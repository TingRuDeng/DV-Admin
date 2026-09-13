"""Public registration, captcha and password recovery endpoints."""

import base64
import io
import secrets

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from PIL import Image, ImageDraw
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from drf_admin.apps.oauth.email_code import EmailCodeError, send_code, verify_code
from drf_admin.apps.system.models import Roles, Users
from drf_admin.utils.password_validation import validate_password


def _value(data, *names, default=""):
    for name in names:
        if name in data:
            return data[name]
    return default


def _error(message, code=400):
    return Response({"detail": message}, status=code if code >= 400 else 200)


def _captcha(request):
    code = f"{secrets.randbelow(10000):04d}"
    key = secrets.token_urlsafe(18)
    cache.set(f"oauth:captcha:{key}", code, 300)
    image = Image.new("RGB", (140, 48), "#10151f")
    draw = ImageDraw.Draw(image)
    draw.text((42, 14), code, fill="#ff6b57")
    output = io.BytesIO()
    image.save(output, format="PNG")
    payload = {
        "captchaKey": key,
        "captchaBase64": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode(),
    }
    return Response(payload)


def _verify_captcha(data, *, consume=True):
    key = _value(data, "captcha_key", "captchaKey")
    code = _value(data, "captcha_code", "captchaCode")
    if getattr(settings, "ENVIRONMENT", "").lower() in {"dev", "development", "test"} and not key and not code:
        return True
    expected = cache.get(f"oauth:captcha:{key}") if key and code else None
    if not expected or str(expected).lower() != str(code).strip().lower():
        return False
    if consume:
        cache.delete(f"oauth:captcha:{key}")
    return True


class CaptchaAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return _captcha(request)


class EmailCodeAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        purpose = _value(data, "purpose", default="register")
        email = str(_value(data, "email")).strip().lower()
        try:
            validate_email(email)
        except DjangoValidationError:
            return _error("邮箱无效")
        if purpose not in {"register", "reset_password"} or not _verify_captcha(data, consume=False):
            return _error("验证码无效")
        try:
            send_code(purpose=purpose, email=email)
        except EmailCodeError as exc:
            if exc.retry_after is not None:
                raise Throttled(wait=exc.retry_after, detail=str(exc)) from exc
            return _error(str(exc))
        return Response({})


class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        username = str(_value(data, "username")).strip()
        email = str(_value(data, "email")).strip().lower()
        password = str(_value(data, "password"))
        confirm = str(_value(data, "confirm_password", "confirmPassword"))
        if not username or not email or "@" not in email:
            return _error("用户名和邮箱不能为空")
        if password != confirm:
            return _error("两次输入的密码不一致")
        if not _verify_captcha(data):
            return _error("验证码无效")
        if not verify_code(purpose="register", email=email, code=str(_value(data, "email_code", "emailCode"))):
            return _error("邮箱验证码无效")
        if Users.objects.filter(username=username).exists():
            return _error("用户名已存在", status.HTTP_409_CONFLICT)
        if Users.objects.filter(email=email).exists():
            return _error("邮箱已存在", status.HTTP_409_CONFLICT)
        try:
            validate_password(password)
        except Exception as exc:
            return _error(str(exc))
        user = Users.objects.create_user(username=username, email=email, password=password, is_active=1)
        default_role = Roles.objects.filter(is_default=1, status=1).first()
        if default_role:
            user.roles.add(default_role)
        return Response({})


class PasswordResetAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        username = str(_value(data, "username")).strip()
        email = str(_value(data, "email")).strip().lower()
        password = str(_value(data, "new_password", "newPassword"))
        confirm = str(_value(data, "confirm_password", "confirmPassword"))
        if not username or not email or password != confirm:
            return _error("账号信息或密码无效")
        if not _verify_captcha(data):
            return _error("验证码无效")
        if not verify_code(purpose="reset_password", email=email, code=str(_value(data, "email_code", "emailCode"))):
            return _error("邮箱验证码无效")
        user = Users.objects.filter(username=username, email=email).first()
        if not user:
            return _error("账号信息或验证码无效")
        try:
            validate_password(password)
        except Exception as exc:
            return _error(str(exc))
        user.set_password(password)
        user.save(update_fields=["password"])
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        return Response({})
