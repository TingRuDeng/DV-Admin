# -*- coding: utf-8 -*-

from rest_framework.filters import SearchFilter, OrderingFilter

from drf_admin.apps.system.models import Permissions
from drf_admin.utils.views import AdminViewSet, TreeAPIView
from drf_admin.apps.system.serializers.permissions import MenusSerializer, MenusTreeSerializer


class MenusViewSet(AdminViewSet, TreeAPIView):
    """
    create:
    权限--新增

    菜单新增, status: 201(成功), return: 新增菜单信息

    destroy:
    权限--删除

    权限删除, status: 204(成功), return: None

    multiple_delete:
    权限--批量删除

    权限批量删除, status: 204(成功), return: None

    update:
    权限--修改

    权限修改, status: 200(成功), return: 修改增权限信息

    partial_update:
    权限--局部修改

    权限局部修改, status: 200(成功), return: 修改增权限信息

    list:
    权限--获取列表

    权限列表信息, status: 200(成功), return: 权限信息列表
    """
    queryset = Permissions.objects.all()
    serializer_class = MenusSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'route_name', 'desc')
    ordering_fields = ('id', 'name')

    def get_serializer_class(self):
        if self.action == 'list':
            return MenusTreeSerializer
        else:
            return MenusSerializer


class MenusTreeViewSet(TreeAPIView):
    """
    list:
    菜单--获取树状列表
    """
    queryset = Permissions.objects.all()
    serializer_class = MenusTreeSerializer
    pagination_class = None
