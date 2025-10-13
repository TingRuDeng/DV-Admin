# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView

from drf_admin.apps.system.models import Roles
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView
from drf_admin.apps.system.serializers.roles import RolesSerializer, RolesPartialSerializer, RolesOptionsSerializer


class RolesViewSet(AdminViewSet):
    """
    create:
    角色--新增

    角色新增, status: 201(成功), return: 新增角色信息

    destroy:
    角色--删除

    角色删除, status: 204(成功), return: None

    multiple_delete:
    角色--批量删除

    角色批量删除, status: 204(成功), return: None

    update:
    角色--修改

    角色修改, status: 200(成功), return: 修改后的角色信息

    partial_update:
    角色--局部修改(角色授权)

    角色局部修改, status: 200(成功), return: 修改后的角色信息

    list:
    角色--获取列表

    角色列表信息, status: 200(成功), return: 角色信息列表
    """
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'desc')

    # ordering_fields = ('id', 'name')

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return RolesPartialSerializer
        else:
            return RolesSerializer

    # def update(self, request, *args, **kwargs):
    #     if self.get_object().name == 'admin':
    #         return Response(data={'detail': 'admin角色不可修改'}, status=status.HTTP_400_BAD_REQUEST)
    #     return super().update(request, *args, **kwargs)

    # def destroy(self, request, *args, **kwargs):
    #     if self.get_object().name == 'admin':
    #         return Response(data={'detail': 'admin角色不可删除'}, status=status.HTTP_400_BAD_REQUEST)
    #     return super().destroy(request, *args, **kwargs)

    # def partial_update(self, request, *args, **kwargs):
    #     if self.get_object().name == 'admin':
    #         return Response(data={'detail': 'admin角色, 默认拥有所有权限'}, status=status.HTTP_400_BAD_REQUEST)
    #     return super().partial_update(request, *args, **kwargs)

    def multiple_delete(self, request, *args, **kwargs):
        delete_ids = request.data.get('ids')
        try:
            admin = Roles.objects.get(name='admin')
            if isinstance(delete_ids, list):
                if admin.id in delete_ids:
                    return Response(data={'detail': 'admin角色不可删除'}, status=status.HTTP_400_BAD_REQUEST)
        except Roles.DoesNotExist:
            pass
        return super().multiple_delete(request, *args, **kwargs)


class RolesOptionsViewSet(AutoPermissionAPIView, ListAPIView):
    """
    list:
    角色--获取选项列表
    """
    queryset = Roles.objects.all()
    serializer_class = RolesOptionsSerializer
    pagination_class = None


class RoleMenuIdsAPIView(AutoPermissionAPIView, RetrieveAPIView):
    """
    retrieve:
    角色--获取菜单ID列表

    获取指定角色的菜单ID列表，status: 200(成功), return: 菜单ID列表
    """
    queryset = Roles.objects.all()
    # 不需要完整的序列化器，我们会自定义返回数据
    pagination_class = None
    lookup_field = 'pk'

    def get_serializer_class(self):
        # 检测是否是Swagger的假视图调用
        if getattr(self, 'swagger_fake_view', False):
            # 为Swagger文档生成提供一个简单的序列化器
            from rest_framework import serializers
            class FakeMenuIdsSerializer(serializers.Serializer):
                menu_ids = serializers.ListField(child=serializers.IntegerField())

            return FakeMenuIdsSerializer
        # 实际请求中不需要序列化器
        return None

    def retrieve(self, request, *args, **kwargs):
        # 获取角色对象
        instance = self.get_object()
        # 从角色对象中获取菜单ID列表
        menu_ids = list(instance.permissions.values_list('id', flat=True))
        # 返回自定义格式的数据
        return Response(data=menu_ids)