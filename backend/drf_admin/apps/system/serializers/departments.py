# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Departments
from drf_admin.common.models import get_child_ids


class DepartmentsSerializer(serializers.ModelSerializer):
    """
    部门管理序列化器
    """
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Departments
        fields = [
            'id',
            'name',
            'status',
            'sort',
            'parent_id',
        ]

    def update(self, instance, validated_data):
        # 验证父部门不能为其本身或其子部门
        departments_id = get_child_ids(instance.id, Departments)
        parent_id = validated_data.get('parent_id', None)
        if parent_id is not None and parent_id in departments_id:
            raise serializers.ValidationError('父部门不能为其本身或其子部门')
        instance.name = validated_data.get('name', instance.name)
        instance.status = validated_data.get('status', instance.status)
        instance.sort = validated_data.get('sort', instance.sort)
        if parent_id is not None:
            instance.parent_id = parent_id
        instance.save()
        return instance

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        instance = super().create(validated_data)
        if parent_id is not None:
            instance.parent_id = parent_id
            instance.save()
        return instance


class DepartmentsTreeSerializer(serializers.ModelSerializer):
    """
    部门数据序列化器(Element Tree)
    """
    id = serializers.IntegerField()
    label = serializers.CharField(max_length=20, source='name')
    children = serializers.ListField(read_only=True, required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Departments
        fields = [
            'id',
            'label',
            'children',
            'name',
            'status',
            'sort',
            'parent_id',
        ]
