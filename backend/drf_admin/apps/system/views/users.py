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
from drf_admin.apps.system.serializers.batch_delete import BatchDeleteResultSerializer
from drf_admin.apps.system.serializers.users import (
    ResetPasswordSerializer,
    UsersOptionsSerializer,
    UsersPartialSerializer,
    UsersSerializer,
)
from drf_admin.apps.system.services.batch_delete import (
    build_batch_delete_result,
    failure_item,
    normalize_batch_ids,
    preflight_batch_ids,
    success_item,
)
from drf_admin.apps.system.services.data_scope import apply_user_data_scope
from drf_admin.apps.system.services.user_import_export import (
    build_import_template,
    export_users,
    import_users,
)
from drf_admin.utils.audit import set_audit_context, set_audit_object
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

    用户批量删除, status: 200(成功), return: 逐条处理结果

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
        unique_ids = normalize_batch_ids(delete_ids, resource_name="用户")
        include_ids = self._current_user_include_ids(unique_ids)
        preflight_batch_ids(
            self.get_queryset(),
            unique_ids,
            resource_name="用户",
            include_ids=include_ids,
        )
        return Users.objects.filter(id__in=unique_ids)

    @staticmethod
    def get_action_permission_mapping():
        """为逐条重试动作复用用户删除权限。"""
        mapping = AdminViewSet.get_action_permission_mapping()
        return {**mapping, "retry_batch_delete": "delete"}

    def multiple_delete(self, request, *args, **kwargs):
        """批量删除用户并返回逐条结果。"""
        return self._run_batch_delete(request, retry=False)

    def retry_batch_delete(self, request, *args, **kwargs):
        """逐条重新校验并重试用户删除。"""
        return self._run_batch_delete(request, retry=True)

    def _run_batch_delete(self, request, *, retry: bool):
        """执行一次批量删除或重试，单个对象失败不影响其他对象。"""
        unique_ids = normalize_batch_ids(request.data.get("ids"), resource_name="用户")
        object_by_id = {}
        if not retry:
            preflight_batch_ids(
                self.get_queryset(),
                unique_ids,
                resource_name="用户",
                include_ids=self._current_user_include_ids(unique_ids),
            )
            object_by_id = {
                user.id: user for user in Users.objects.filter(id__in=unique_ids)
            }

        success_items = []
        failures = []
        current_user_id = getattr(request.user, "id", None)
        for user_id in unique_ids:
            user = (
                Users.objects.filter(id=user_id).first()
                if retry
                else object_by_id.get(user_id)
            )
            if user is None:
                failures.append(
                    failure_item(
                        user_id,
                        error_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                        message="用户已不存在" if retry else "用户不存在",
                    )
                )
                continue

            if retry and user_id != current_user_id:
                if not self.get_queryset().filter(id=user_id).exists():
                    failures.append(
                        failure_item(
                            user_id,
                            object_name=user.name or user.username,
                            error_code="NOT_FOUND",
                            message="用户不存在",
                        )
                    )
                    continue

            object_name = user.name or user.username
            if current_user_id is not None and user_id == current_user_id:
                failures.append(
                    failure_item(
                        user_id,
                        object_name=object_name,
                        error_code="PROTECTED_OBJECT",
                        message="不能删除当前登录用户",
                    )
                )
                continue

            try:
                with transaction.atomic():
                    scoped_queryset = (
                        self.get_queryset()
                        .filter(id=user_id)
                        .select_related(None)
                        .prefetch_related(None)
                    )
                    locked_user = scoped_queryset.select_for_update().first()
                    if locked_user is None:
                        failures.append(
                            failure_item(
                                user_id,
                                object_name=object_name,
                                error_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                                message="用户已不存在" if retry else "用户不存在",
                            )
                        )
                    else:
                        locked_user.delete()
                        success_items.append(success_item(user_id, object_name))
            except Exception:  # noqa: BLE001 - 单条失败不能阻塞其余项目
                failures.append(
                    failure_item(
                        user_id,
                        object_name=object_name,
                        error_code="DELETE_FAILED",
                        message="删除用户失败",
                        retryable=True,
                    )
                )

        result = build_batch_delete_result(unique_ids, success_items, failures)
        set_audit_context(
            request,
            batch_count=result["total_count"],
            success_count=result["success_count"],
            failed_count=result["failed_count"],
            failure_codes=sorted({item["error_code"] for item in failures}),
            retry=retry,
        )
        return Response(data=BatchDeleteResultSerializer(result).data)

    def _current_user_include_ids(self, unique_ids):
        """允许把当前用户纳入预检，以便返回稳定的保护对象失败项。"""
        current_user_id = getattr(self.request.user, "id", None)
        if current_user_id in unique_ids and Users.objects.filter(id=current_user_id).exists():
            return [current_user_id]
        return []


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

    def initial(self, request, *args, **kwargs):
        set_audit_object(request, "system.users", "", changed_fields=["export"])
        return super().initial(request, *args, **kwargs)

    def post(self, request):
        result = export_users(request.user)
        set_audit_context(request, export_fields=list(result.keys()))
        return Response(data=result)


class UserImportAPIView(AutoPermissionAPIView):
    """导入 xlsx 用户数据。"""

    model = Users

    @staticmethod
    def get_method_permission_mapping():
        return {"post": "import"}

    def initial(self, request, *args, **kwargs):
        set_audit_object(request, "system.users", "", changed_fields=["file", "deptId"])
        return super().initial(request, *args, **kwargs)

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
        result = import_users(
            uploaded_file.file,
            dept_id=dept_id,
            current_user=request.user,
        )
        set_audit_context(
            request,
            batch_count=result.get("validCount", 0) + result.get("invalidCount", 0),
            success_count=result.get("validCount", 0),
            failed_count=result.get("invalidCount", 0),
        )
        return Response(data=result)

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

    @staticmethod
    def get_method_permission_mapping():
        return {"put": "password:reset", "patch": "password:reset"}

    def get_queryset(self):
        return apply_user_data_scope(super().get_queryset(), self.request.user)

    def initial(self, request, *args, **kwargs):
        set_audit_object(
            request,
            "system.users",
            kwargs.get(self.lookup_url_kwarg or self.lookup_field, ""),
            changed_fields=["password"],
        )
        return super().initial(request, *args, **kwargs)

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
