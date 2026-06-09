# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Roles
from drf_admin.utils.views import OptionsSerializer


class RolesSerializer(serializers.ModelSerializer):
    """
    角色管理序列化器
    """
    # create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Roles
        fields = ['id', 'name', 'code', 'permissions', 'status', 'sort', 'desc', 'is_default']
        extra_kwargs = {
            'permissions': {
                'read_only': True,
            },
        }


class RolesPartialSerializer(serializers.ModelSerializer):
    """
    用户局部更新序列化器(角色授权)
    """

    class Meta:
        model = Roles
        fields = ['id', 'permissions']

    # def validate(self, attrs):
    #     permissions = attrs.get('permissions')
    #     for permission in permissions:
    #         if permission.pid and permission.pid not in permissions:
    #             raise serializers.ValidationError('缺失父节点权限')
    #     return attrs


class RolesMenuAssignSerializer(serializers.Serializer):
    """
    角色菜单权限分配序列化器
    """
    menu_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)


class RolesOptionsSerializer(OptionsSerializer):
    """
    角色数据序列化器(Options类型)
    """
    class Meta:
        model = Roles
        fields = ['id', 'label']
