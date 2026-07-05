# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Departments, Roles
from drf_admin.utils.views import OptionsSerializer


class RolesSerializer(serializers.ModelSerializer):
    """
    角色管理序列化器
    """
    # create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    data_scope = serializers.IntegerField(required=False, write_only=True)
    dataScope = serializers.IntegerField(source="data_scope", read_only=True)
    dept_ids = serializers.PrimaryKeyRelatedField(
        source="data_depts",
        many=True,
        queryset=Departments.objects.all(),
        required=False,
        write_only=True,
    )
    deptIds = serializers.SerializerMethodField()
    is_default = serializers.IntegerField(required=False, write_only=True)
    isDefault = serializers.IntegerField(source="is_default", read_only=True)
    createTime = serializers.DateTimeField(source="create_time", read_only=True)
    updateTime = serializers.DateTimeField(source="update_time", read_only=True)

    class Meta:
        model = Roles
        fields = [
            'id',
            'name',
            'code',
            'permissions',
            'data_scope',
            'dataScope',
            'dept_ids',
            'deptIds',
            'status',
            'sort',
            'desc',
            'is_default',
            'isDefault',
            'createTime',
            'updateTime',
        ]
        extra_kwargs = {
            'permissions': {
                'read_only': True,
            },
        }

    def get_deptIds(self, obj):
        return list(obj.data_depts.values_list("id", flat=True))


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
