# -*- coding: utf-8 -*-

import re

from django.conf import settings
from rest_framework import serializers
from drf_admin.apps.system.models import Users
from drf_admin.utils.views import OptionsSerializer


class UsersSerializer(serializers.ModelSerializer):
    """
    用户增删改查序列化器
    """
    roles_list = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    dept_name = serializers.ReadOnlyField(source='dept.name')
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'username', 'name', 'mobile', 'email', 'is_active', 'dept', 'dept_name',
                  'date_joined', 'roles', 'roles_list', 'is_superuser']

    def validate(self, attrs):
        # 数据验证
        if attrs.get('username'):
            if attrs.get('username').isdigit():
                raise serializers.ValidationError('用户名不能为纯数字')
        if attrs.get('mobile'):
            if not re.match(r'^1[3-9]\d{9}$', attrs.get('mobile')):
                raise serializers.ValidationError('手机格式不正确')
        if attrs.get('mobile') == '':
            attrs['mobile'] = None
        return attrs

    def get_roles_list(self, obj):
        return [{'id': role.id, 'desc': role.desc} for role in obj.roles.all()]

    def create(self, validated_data):
        user = super().create(validated_data)
        # 添加默认密码
        user.set_password(settings.DEFAULT_PWD)
        user.save()
        return user


class UsersPartialSerializer(serializers.ModelSerializer):
    """
    用户局部更新(激活/锁定)序列化器
    """

    class Meta:
        model = Users
        fields = ['id', 'is_active']


class ResetPasswordSerializer(serializers.ModelSerializer):
    """
    重置密码序列化器
    """
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['id', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, attrs):
        # partial_update, 局部更新required验证无效, 手动验证数据
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if not password:
            raise serializers.ValidationError('字段password为必填项')
        if not confirm_password:
            raise serializers.ValidationError('字段confirm_password为必填项')
        if password != confirm_password:
            raise serializers.ValidationError('两次密码不一致')
        return attrs

    def save(self, **kwargs):
        # 重写save方法, 保存密码
        self.instance.set_password(self.validated_data.get('password'))
        self.instance.save()
        return self.instance


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """
    更新个人信息序列化器（包含基本信息和密码）
    """
    current_password = serializers.CharField(write_only=True, help_text="当前密码", required=False)
    new_password = serializers.CharField(write_only=True, help_text="新密码", required=False)
    confirm_password = serializers.CharField(write_only=True, help_text="确认新密码", required=False)

    class Meta:
        model = Users
        fields = ['name', 'current_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        """验证数据"""
        # 验证手机格式
        # if attrs.get('mobile'):
        #     if not re.match(r'^1[3-9]\d{9}$', attrs.get('mobile')):
        #         raise serializers.ValidationError('手机格式不正确')
        #     # 检查手机号是否已存在
        #     user_id = self.instance.id if self.instance else None
        #     if Users.objects.filter(mobile=attrs.get('mobile')).exclude(id=user_id).exists():
        #         raise serializers.ValidationError('手机号已被使用')
        #
        # # 验证邮箱格式（简单验证）
        # if attrs.get('email'):
        #     if not re.match(r'^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$', attrs.get('email')):
        #         raise serializers.ValidationError('邮箱格式不正确')
        #
        # 验证密码相关字段
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # 如果提供了新密码，必须提供当前密码和确认密码
        if new_password:
            if not current_password:
                raise serializers.ValidationError('修改密码时必须提供当前密码')
            if not confirm_password:
                raise serializers.ValidationError('修改密码时必须提供确认密码')
            
            # 验证当前密码是否正确
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError('当前密码不正确')
            
            # 验证新密码和确认密码是否一致
            if new_password != confirm_password:
                raise serializers.ValidationError('两次输入的新密码不一致')
            
            # 密码强度验证
            if len(new_password) < 6:
                raise serializers.ValidationError('密码长度不能少于6位')
        
        return attrs

    def save(self, **kwargs):
        """保存用户信息和密码"""
        # 更新基本信息
        if 'name' in self.validated_data:
            self.instance.name = self.validated_data.get('name')
        # if 'mobile' in self.validated_data:
        #     self.instance.mobile = self.validated_data.get('mobile')
        # if 'email' in self.validated_data:
        #     self.instance.email = self.validated_data.get('email')
            
        # 更新密码
        if 'new_password' in self.validated_data:
            self.instance.set_password(self.validated_data.get('new_password'))
        
        self.instance.save()
        return self.instance


class UsersOptionsSerializer(OptionsSerializer):
    """
    用户数据序列化器(Options类型)
    """
    class Meta:
        model = Users
        fields = ['id', 'label']
