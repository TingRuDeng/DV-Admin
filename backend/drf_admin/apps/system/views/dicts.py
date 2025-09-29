# -*- coding: utf-8 -*-

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from drf_admin.utils.views import AdminViewSet
from drf_admin.apps.system.models import Dicts, DictItems
from drf_admin.apps.system.serializers.dicts import DictsSerializer, DictItemsSerializer


class DictsViewSet(AdminViewSet):
    """
    create:
    字典--新增

    字典新增, status: 201(成功), return: 新增字典信息

    destroy:
    字典--删除

    字典删除, status: 204(成功), return: None

    multiple_delete:
    字典--批量删除

    字典批量删除, status: 204(成功), return: None

    update:
    字典--修改

    字典修改, status: 200(成功), return: 修改后的字典信息

    partial_update:
    字典--局部修改

    字典局部修改, status: 200(成功), return: 修改后的字典信息

    list:
    字典--获取列表

    字典列表信息, status: 200(成功), return: 字典信息列表

    retrieve:
    字典--详情
    
    字典详情信息, status: 200(成功), return: 单个字典信息详情
    """
    queryset = Dicts.objects.all()
    serializer_class = DictsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    ordering_fields = ('dict_code',)
    search_fields = ('name', 'dict_code')


class DictItemsViewSet(AdminViewSet):
    """
    create:
    字典项--新增

    字典项新增, status: 201(成功), return: 新增字典项信息

    destroy:
    字典项--删除

    字典项删除, status: 204(成功), return: None

    multiple_delete:
    字典项--批量删除

    字典项批量删除, status: 204(成功), return: None

    update:
    字典项--修改

    字典项修改, status: 200(成功), return: 修改后的字典项信息

    partial_update:
    字典项--局部修改

    字典项局部修改, status: 200(成功), return: 修改后的字典项信息

    list:
    字典项--获取列表

    字典项列表信息, status: 200(成功), return: 字典项信息列表

    retrieve:
    字典项--详情

    字典项详情信息, status: 200(成功), return: 单个字典项信息详情
    """
    queryset = DictItems.objects.all()
    serializer_class = DictItemsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    filterset_fields = ['dict', 'dict__dict_code']

    search_fields = ('label', 'value')
