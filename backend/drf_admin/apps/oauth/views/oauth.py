# -*- coding: utf-8 -*-

import json
import logging

from django.conf import settings
from rest_framework import status
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_admin.apps.system.models import Permissions, Users
from drf_admin.apps.oauth.serializers.token_serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger("info")


class UserLoginView(TokenObtainPairView):
    """
    post:
    用户登录

    用户登录, status: 200(成功), return: Token信息
    """

    throttle_classes = [AnonRateThrottle]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # 重写父类方法, 定义响应字段内容
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = {
                "accessToken": response.data["access"],
                "refreshToken": response.data["refresh"],  # 可选
            }
            # 检查Redis配置是否存在
            if (
                hasattr(settings, "REDIS_HOST")
                and hasattr(settings, "REDIS_PORT")
                and settings.REDIS_HOST
                and settings.REDIS_PORT
            ):
                try:
                    conn = get_redis_connection("user_info")
                    conn.incr("visits")
                except Exception as e:
                    logger.error(f"Redis connection error: {str(e)}")
            else:
                # 使用Django缓存代替Redis特定功能
                cache_key = "visits"
                current_count = cache.get(cache_key, 0)
                cache.set(cache_key, current_count + 1)
            return Response(data)
        else:
            if response.data.get("non_field_errors"):
                # 日后将增加用户多次登录错误,账户锁定功能(待完善)
                if (
                    isinstance(response.data.get("non_field_errors"), list)
                    and len(response.data.get("non_field_errors")) > 0
                ):
                    if (
                        response.data.get("non_field_errors")[0].strip()
                        == "无法使用提供的认证信息登录。"
                    ):
                        return Response(
                            data={"detail": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST
                        )
            raise ValidationError(response.data)


class UserInfoView(APIView):
    """
    get:
    当前用户信息和权限

    当前用户信息, status: 200(成功), return: 用户信息和权限
    """

    def get(self, request):
        user = (
            Users.objects.select_related("dept")
            .prefetch_related("roles__permissions")
            .get(id=request.user.id)
        )
        user_info = user.get_user_info()
        http_host = request.get_host()
        http_port = request.get_port()
        if http_port in http_host:
            host_url = f"{request.scheme}://{http_host}"
        else:
            host_url = f"{request.scheme}://{http_host}:{http_port}"
        if (
            hasattr(settings, "REDIS_HOST")
            and hasattr(settings, "REDIS_PORT")
            and settings.REDIS_HOST
            and settings.REDIS_PORT
        ):
            try:
                conn = get_redis_connection("user_info")
                if request.user.is_superuser and "admin" not in user_info["perms"]:
                    user_info["perms"].append("admin")
                user_info["perms"] = json.dumps(user_info["perms"])
                user_info["avatar"] = f"{host_url}{user_info.get('avatar')}"
                conn.hmset(f"user_info_{request.user.id}", user_info)
                conn.expire(f"user_info_{request.user.id}", 60 * 60 * 24)
                user_info["perms"] = json.loads(user_info["perms"])
            except Exception as e:
                logger.error(f"Redis connection error: {str(e)}")
        else:
            if request.user.is_superuser and "admin" not in user_info["perms"]:
                user_info["perms"].append("admin")
            user_info["avatar"] = f"{host_url}{user_info.get('avatar')}"
            cache_key = f"user_info_{request.user.id}"
            cache.set(cache_key, user_info, 60 * 60 * 24)
        return Response(user_info, status=status.HTTP_200_OK)


class RoutesAPIView(APIView):
    """
    get:
    菜单--获取用户拥有菜单列表，由前端组合成动态路由

    获取用户拥有菜单列表, status: 200(成功), return: 用户拥有菜单列表
    """

    def get(self, request):
        try:
            user = (
                Users.objects.select_related()
                .prefetch_related("roles__permissions")
                .get(id=request.user.id, is_active=True)
            )
        except Users.DoesNotExist:
            raise ValidationError("用户已被禁用，请联系管理员")
        except Users.MultipleObjectsReturned:
            raise ValidationError("用户数据异常，请联系管理员")
        return Response(data=user.get_menus())


class LogoutAPIView(APIView):
    """
    post:
    退出登录

    退出登录, status: 200(成功), return: None
    """

    def post(self, request):
        try:
            refresh_token = request.data.get("refreshToken")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            logger.warning(f"Token blacklist failed: {str(e)}")
        return Response({"message": "退出成功"}, status=status.HTTP_200_OK)


class RefreshTokenAPIView(APIView):
    """
    post:
    刷新访问令牌

    使用刷新令牌获取新的访问令牌, status: 200(成功), return: Token信息
    """

    # 不需要认证和权限检查
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # 支持两种参数格式：
        # 1. query parameter: refreshToken (会被 CamelCaseMiddleWare 转换为 refresh_token)
        # 2. body: {"refresh": "xxx"} 或 {"refreshToken": "xxx"}
        
        refresh_token = (
            request.query_params.get("refresh_token")  # CamelCaseMiddleWare 转换后
            or request.query_params.get("refreshToken")  # 原始参数
            or request.data.get("refresh")
            or request.data.get("refreshToken")
            or request.data.get("refresh_token")  # CamelCaseMiddleWare 转换后
        )

        if not refresh_token:
            return Response(
                {"detail": "缺少刷新令牌"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 验证并解码刷新令牌
            token = RefreshToken(refresh_token)

            # 生成新的访问令牌
            access_token = token.access_token

            # 返回新的令牌（兼容 FastAPI 格式）
            data = {
                "accessToken": str(access_token),
                "refreshToken": str(token),
                "tokenType": "bearer",
                "expiresIn": settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", 300).total_seconds(),
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return Response(
                {"detail": "无效的刷新令牌", "code": "token_not_valid"},
                status=status.HTTP_401_UNAUTHORIZED
            )
