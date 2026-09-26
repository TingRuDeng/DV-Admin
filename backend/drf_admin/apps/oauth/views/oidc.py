# -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework.exceptions import ParseError, UnsupportedMediaType, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_admin.apps.oauth.oidc_policy import OidcError
from drf_admin.apps.oauth.services import oidc as oidc_service
from drf_admin.apps.oauth.utils import get_request_ip


class OidcAuthorizeView(APIView):
    """
    post:
    单点登录--发起授权

    生成一次性 state/nonce/PKCE, status: 200(成功), return: 授权地址、state 和 flowSecret
    """

    # 公开接口：不需要认证和权限检查
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            data = oidc_service.start_authorization(get_request_ip(request))
        except OidcError as error:
            raise ValidationError(error.message) from None
        return Response(data)


class OidcLoginView(APIView):
    """
    post:
    单点登录--回调登录

    用授权码换取并校验 ID Token, status: 200(成功), return: 与密码登录相同的本地 Token
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            user = oidc_service.complete_login(_request_data(request), get_request_ip(request))
        except OidcError as error:
            raise ValidationError(error.message) from None
        refresh = RefreshToken.for_user(user)
        data = {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "tokenType": "bearer",
            "expiresIn": int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        }
        return Response(data)


def _request_data(request):
    # 请求体格式错误统一走 flow invalid，不让框架返回另一种错误文案
    try:
        return request.data
    except (ParseError, UnsupportedMediaType):
        return {}
