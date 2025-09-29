# -*- coding: utf-8 -*-
"""
自定义Token序列化器，实现细粒度的登录校验规则
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
