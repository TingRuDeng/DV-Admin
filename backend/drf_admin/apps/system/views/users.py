# -*- coding: utf-8 -*-

from pathlib import Path

from django.conf import settings
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from drf_admin.apps.system.filters.users import UsersFilter
from drf_admin.apps.system.models import Permissions, Users
from drf_admin.apps.system.serializers.users import (
    ResetPasswordSerializer,
    UsersOptionsSerializer,
    UsersPartialSerializer,
    UsersSerializer,
)
from drf_admin.apps.system.services.data_scope import apply_user_data_scope
from drf_admin.apps.system.services.user_import_export import (
    build_import_template,
    export_users,
    import_users,
)
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView


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
    queryset = Users.objects.all().select_related('dept').prefetch_related('roles')
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

    def get_queryset(self):
        queryset = super().get_queryset()
        return apply_user_data_scope(queryset, self.request.user)

    def validate_ids(self, delete_ids):
        """批量删除必须全部处于当前数据范围，且不因重复 ID 误判。"""
        if not isinstance(delete_ids, list) or not delete_ids:
            raise ValidationError("参数错误,ids为必传List")
        if any(not isinstance(user_id, int) or user_id < 1 for user_id in delete_ids):
            raise ValidationError("ids必须为正整数列表")
        unique_ids = list(dict.fromkeys(delete_ids))
        queryset = self.get_queryset().filter(id__in=unique_ids)
        locked_ids = list(
            queryset.select_for_update().values_list("id", flat=True)
        )
        if len(locked_ids) != len(unique_ids):
            raise NotFound("用户不存在")
        return queryset.filter(id__in=locked_ids)

    @transaction.atomic
    def multiple_delete(self, request, *args, **kwargs):
        """在同一事务内完成范围校验与批量删除。"""
        return super().multiple_delete(request, *args, **kwargs)


class UsersOptionsViewSet(AutoPermissionAPIView, ListAPIView):
    """
    get:
    用户--下拉框列表

    获取用户下拉框列表, status: 200(成功), return: 用户下拉框列表
    """
    queryset = Users.objects.all()
    serializer_class = UsersOptionsSerializer
    pagination_class = None  # 禁用分页

    def get_queryset(self):
        return apply_user_data_scope(super().get_queryset(), self.request.user)


class UserImportTemplateAPIView(AutoPermissionAPIView):
    """下载用户导入模板。"""

    model = Users

    @staticmethod
    def get_method_permission_mapping():
        return {"get": "import"}

    def get(self, request):
        return Response(data=build_import_template())


class UserExportAPIView(AutoPermissionAPIView):
    """导出当前数据范围内的用户。"""

    model = Users

    @staticmethod
    def get_method_permission_mapping():
        return {"post": "export"}

    def post(self, request):
        return Response(data=export_users(request.user))


class UserImportAPIView(AutoPermissionAPIView):
    """导入 xlsx 用户数据。"""

    model = Users

    @staticmethod
    def get_method_permission_mapping():
        return {"post": "import"}

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            raise ValidationError("文件不能为空")
        if Path(uploaded_file.name).suffix.lower() != ".xlsx":
            raise ValidationError("文件格式错误，仅支持 .xlsx 格式")
        if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
            max_size = settings.MAX_UPLOAD_SIZE
            max_size_label = (
                f"{max_size / (1024 * 1024):g} MiB"
                if max_size >= 1024 * 1024
                else f"{max_size} 字节"
            )
            raise ValidationError(f"文件大小不能超过 {max_size_label}")
        dept_id = self._parse_dept_id(request.query_params)
        return Response(
            data=import_users(
                uploaded_file.file,
                dept_id=dept_id,
                current_user=request.user,
            )
        )

    @staticmethod
    def _parse_dept_id(query_params):
        raw_dept_id = query_params.get("deptId", query_params.get("dept_id"))
        if raw_dept_id in (None, ""):
            return None
        try:
            return int(raw_dept_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError("deptId 必须为整数") from exc


class ResetPasswordAPIView(mixins.UpdateModelMixin, AutoPermissionAPIView, GenericAPIView):
    """
    patch:
    用户--重置密码

    用户重置密码, status: 200(成功), return: None
    """
    queryset = Users.objects.all()
    serializer_class = ResetPasswordSerializer

    def get_queryset(self):
        return apply_user_data_scope(super().get_queryset(), self.request.user)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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


class PermissionsAPIView(AutoPermissionAPIView):
    """
    get:
    用户--获取用户拥有权限ID列表

    获取用户拥有权限ID列表, status: 200(成功), return: 用户拥有权限ID列表
    """

    queryset = Users.objects.all()

    def get(self, request, pk):
        user = apply_user_data_scope(self.queryset, request.user).filter(id=pk).first()
        if user is None:
            raise NotFound("用户不存在")
        # admin角色
        if 'admin' in user.roles.values_list('name', flat=True) or user.is_superuser:
            return Response(data={'results': Permissions.objects.values_list('id', flat=True)})
        # 其他角色
        return Response(data={'results': list(filter(None, set(user.roles.values_list('permissions__id', flat=True))))})
