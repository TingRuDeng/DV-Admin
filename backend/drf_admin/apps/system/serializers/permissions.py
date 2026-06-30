# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Permissions
from drf_admin.utils.views import TreeSerializer


class MenusSerializer(serializers.ModelSerializer):
    """
    菜单管理序列化器
    """
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=Permissions.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Permissions
        fields = [
            'id',
            'name',
            'type',
            'route_name',
            'route_path',
            'component',
            'sort',
            'visible',
            'icon',
            'redirect',
            'perm',
            'keepAlive',
            'alwaysShow',
            'params',
            'parent_id',
            'desc',
            'create_time',
            'update_time',
        ]

    # def validate(self, attrs):
    #     if attrs.get('menu') is True:
    #         if attrs.get('method', '') != '' or attrs.get('path', '') != '':
    #             raise serializers.ValidationError('菜单权限, 方法与路径必须为空')
    #     else:
    #         if attrs.get('method', '') == '' or attrs.get('path', '') == '':
    #             raise serializers.ValidationError('接口权限, 方法与路径为必传参数')
    #         path = str(attrs.get('path'))
    #         if not all([path.startswith('/'), path.endswith('/')]):
    #             raise serializers.ValidationError('请求路径必须以"/"开头及结尾')
    #     return attrs

    # def update(self, instance, validated_data):
    #     if validated_data.get('menu') is False:
    #         if Permissions.objects.filter(pid=instance.id, menu=True):
    #             raise serializers.ValidationError('菜单权限存在子菜单, 请先修改子菜单')
    #     if validated_data.get('pid'):
    #         if Permissions.objects.filter(id=validated_data.get('pid').id, menu=False):
    #             raise serializers.ValidationError('菜单父权限必须为菜单权限')
    #         permissions_id = get_child_ids(instance.id, Permissions)
    #         if validated_data.get('pid').id in permissions_id:
    #             raise serializers.ValidationError('父权限不能为其本身或其子权限')
    #     return super().update(instance, validated_data)

    # def create(self, validated_data):
    #     if validated_data.get('pid'):
    #         if Permissions.objects.filter(id=validated_data.get('pid').id, menu=False):
    #             raise serializers.ValidationError('菜单父权限必须为菜单权限')
    #     return super().create(validated_data)



class MenusTreeSerializer(TreeSerializer):
    """
    菜单数据序列化器(Element Tree)
    """
    parent_id = serializers.PrimaryKeyRelatedField(source='parent', read_only=True)
    children = serializers.ListField(read_only=True, required=False)

    class Meta:
        model = Permissions
        fields = [
            'id',
            'label',
            'children',
            'name',
            'type',
            'route_name',
            'route_path',
            'component',
            'sort',
            'visible',
            'icon',
            'redirect',
            'perm',
            'keepAlive',
            'alwaysShow',
            'params',
            'parent_id',
            'desc',
            'create_time',
            'update_time',
        ]


class MenusOptionsSerializer(TreeSerializer):
    """
    菜单选项序列化器(下拉框)
    """
    class Meta:
        model = Permissions
        fields = ['id', 'label', 'parent']
