# -*- coding: utf-8 -*-
"""
自定义Token序列化器，实现细粒度的登录校验规则
"""
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch

from drf_admin.apps.system.models import Users


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义Token获取序列化器
    """

    def validate(self, attrs):
        # 提取用户名和密码
        username = attrs.get('username')
        password = attrs.get('password')

        # 验证密码
        if not authenticate(username=username, password=password):
            # 密码错误
            raise serializers.ValidationError('用户名或密码错误')

        # 先检查用户是否存在
        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')

        # 检查用户是否活跃
        if not user.is_active:
            raise serializers.ValidationError('用户已被禁用，请联系管理员')

        # 调用父类的validate方法生成token
        data = super().validate(attrs)
        return data


class SingleUseTokenRefreshSerializer(serializers.Serializer):
    """原子消费并轮换 Refresh Token，阻止并发重放。"""

    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)

    default_error_messages = {
        "no_active_account": "未找到与刷新令牌对应的可用账户。",
    }

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user = Users.objects.filter(
            **{api_settings.USER_ID_FIELD: user_id}
        ).first()
        if user is None or not api_settings.USER_AUTHENTICATION_RULE(user):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        jti = refresh.payload[api_settings.JTI_CLAIM]
        expires_at = datetime_from_epoch(refresh.payload["exp"])

        with transaction.atomic():
            outstanding, _ = OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "user": user,
                    "created_at": refresh.current_time,
                    "token": str(refresh),
                    "expires_at": expires_at,
                },
            )
            outstanding = OutstandingToken.objects.select_for_update().get(
                pk=outstanding.pk
            )
            if BlacklistedToken.objects.filter(token=outstanding).exists():
                raise TokenError("Token is blacklisted")
            BlacklistedToken.objects.create(token=outstanding)

            data = {"access": str(refresh.access_token)}
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()
            data["refresh"] = str(refresh)

        return data
