# -*- coding: utf-8 -*-

from rest_framework import serializers
from drf_admin.apps.system.models import Dicts, DictItems


class DictsSerializer(serializers.ModelSerializer):
    """
    字典增删改查序列化器
    """
    class Meta:
        model = Dicts
        fields = '__all__'


class DictItemsSerializer(serializers.ModelSerializer):
    """
    字典项序列化器
    """
    dict_name = serializers.CharField(source='dict.name', read_only=True)

    class Meta:
        model = DictItems
        fields = '__all__'
