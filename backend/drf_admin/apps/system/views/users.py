# -*- coding: utf-8 -*-

from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView
from drf_admin.apps.system.filters.users import UsersFilter
from drf_admin.apps.system.models import Users, Permissions
from drf_admin.apps.system.serializers.users import (
    UsersSerializer, UsersPartialSerializer, ResetPasswordSerializer, UsersOptionsSerializer
)


class UsersViewSet(AdminViewSet):
    """
    create:
    用户--新增

    用户新增, status: 201(成功), return: 新增用户信息

    destroy:
    用户--删除

    用户删除, status: 204(成功), return: None

    multiple_delete:
    用户--批量删除

    用户批量删除, status: 204(成功), return: None

    update:
    用户--修改

    用户修改, status: 200(成功), return: 修改后的用户信息

    partial_update:
    用户--局部修改

    用户局部修改(激活/锁定), status: 200(成功), return: 修改后的用户信息

    list:
    用户--获取列表

    用户列表信息, status: 200(成功), return: 用户信息列表

    retrieve:
    用户--详情

    用户详情信息, status: 200(成功), return: 单个用户信息详情
    """
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = UsersFilter
    search_fields = ('username', 'name', 'mobile', 'email')
    ordering_fields = ('id',)

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return UsersPartialSerializer
        else:
            return UsersSerializer


class UsersOptionsViewSet(AutoPermissionAPIView, ListAPIView):
    """
    get:
    用户--下拉框列表

    获取用户下拉框列表, status: 200(成功), return: 用户下拉框列表
    """
    queryset = Users.objects.all()
    serializer_class = UsersOptionsSerializer
    pagination_class = None  # 禁用分页


class ResetPasswordAPIView(mixins.UpdateModelMixin, GenericAPIView):
    """
    patch:
    用户--重置密码

    用户重置密码, status: 200(成功), return: None
    """
    queryset = Users.objects.all()
    serializer_class = ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


# class UserFormAPIView(RetrieveAPIView):
#     """
#     retrieve:
#     用户--获取单个用户表单数据
#
#     获取单个用户的详细信息，用于表单展示，status: 200(成功), return: 单个用户详细信息
#     """
#     queryset = Users.objects.all()
#     serializer_class = UsersSerializer
#     pagination_class = None  # 禁用分页
#
#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#         except Users.DoesNotExist:
#             raise ValidationError('无效的用户ID')


# class UpdateUserProfileAPIView(APIView):
#     """
#     put:
#     用户--更新个人信息
#
#     用户更新自己的个人信息（包括姓名、手机、邮箱和密码），status: 200(成功), return: 成功信息
#     """
#
#     def put(self, request):
#         # 获取当前登录用户
#         user = request.user
#
#         # 验证请求数据
#         serializer = UpdateUserProfileSerializer(instance=user, data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 保存更新后的信息
#         serializer.save()
#
#         return Response({'detail': '个人信息更新成功'})
#
#     def get_serializer_class(self):
#         return UpdateUserProfileSerializer


class PermissionsAPIView(APIView):
    """
    get:
    用户--获取用户拥有权限ID列表

    获取用户拥有权限ID列表, status: 200(成功), return: 用户拥有权限ID列表
    """

    def get(self, request, pk):
        try:
            user = Users.objects.get(id=pk)
        except Users.DoesNotExist:
            raise ValidationError('无效的用户ID')
        # admin角色
        if 'admin' in user.roles.values_list('name', flat=True) or user.is_superuser:
            return Response(data={'results': Permissions.objects.values_list('id', flat=True)})
        # 其他角色
        return Response(data={'results': list(filter(None, set(user.roles.values_list('permissions__id', flat=True))))})