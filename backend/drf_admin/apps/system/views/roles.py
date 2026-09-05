# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from drf_admin.apps.system.models import Permissions, Roles, Users
from drf_admin.apps.system.serializers.batch_delete import BatchDeleteResultSerializer
from drf_admin.apps.system.serializers.roles import (
    RolesMenuAssignSerializer,
    RolesOptionsSerializer,
    RolesPartialSerializer,
    RolesSerializer,
)
from drf_admin.apps.system.services.batch_delete import (
    build_batch_delete_result,
    failure_item,
    normalize_batch_ids,
    preflight_batch_ids,
    success_item,
)
from drf_admin.apps.system.signals import clear_user_permission_cache
from drf_admin.utils.audit import set_audit_context, set_audit_object
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView

logger = logging.getLogger("error")

PROTECTED_ROLE_IDENTIFIERS = frozenset(
    {
        "admin",
        "superadmin",
        "administrator",
        "超级管理员",
        "系统管理员",
    }
)


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

    角色批量删除, status: 200(成功), return: 逐条处理结果

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

    @staticmethod
    def get_action_permission_mapping():
        """将角色权限分配动作映射到角色编辑权限。"""
        mapping = AdminViewSet.get_action_permission_mapping()
        return {
            **mapping,
            'assign_menus': 'edit',
            'retry_batch_delete': 'delete',
        }

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return RolesPartialSerializer
        else:
            return RolesSerializer

    # def update(self, request, *args, **kwargs):
    #     if self.get_object().name == 'admin':
    #         return Response(data={'detail': 'admin角色不可修改'}, status=status.HTTP_400_BAD_REQUEST)
    #     return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self._is_protected_role(self.get_object()):
            raise ValidationError("系统角色不可删除")
        return super().destroy(request, *args, **kwargs)

    # def partial_update(self, request, *args, **kwargs):
    #     if self.get_object().name == 'admin':
    #         return Response(data={'detail': 'admin角色, 默认拥有所有权限'}, status=status.HTTP_400_BAD_REQUEST)
    #     return super().partial_update(request, *args, **kwargs)

    def multiple_delete(self, request, *args, **kwargs):
        """批量删除角色并返回逐条结果。"""
        return self._run_batch_delete(request, retry=False)

    def retry_batch_delete(self, request, *args, **kwargs):
        """逐条重新校验并重试角色删除。"""
        return self._run_batch_delete(request, retry=True)

    def _run_batch_delete(self, request, *, retry: bool):
        """执行一次批量删除或重试，单个角色失败不影响其他角色。"""
        unique_ids = normalize_batch_ids(request.data.get("ids"), resource_name="角色")
        roles_by_id = {}
        if not retry:
            preflight_batch_ids(
                self.get_queryset(),
                unique_ids,
                resource_name="角色",
            )
            roles_by_id = {
                role.id: role
                for role in Roles.objects.filter(id__in=unique_ids)
            }

        success_items = []
        failures = []
        for role_id in unique_ids:
            role = (
                Roles.objects.filter(id=role_id).first()
                if retry
                else roles_by_id.get(role_id)
            )
            if role is None:
                failures.append(
                    failure_item(
                        role_id,
                        error_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                        message="角色已不存在" if retry else "角色不存在",
                    )
                )
                continue

            object_name = role.name or role.code or ""
            outcome = self._delete_one_for_batch(
                role_id,
                object_name,
                missing_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                missing_message="角色已不存在" if retry else "角色不存在",
            )
            if outcome.get("success"):
                success_items.append(success_item(role_id, object_name))
            else:
                failures.append(outcome["failure"])

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

    @staticmethod
    def _is_protected_role(role) -> bool:
        """按名称和编码识别内置系统角色。"""
        return any(
            isinstance(value, str)
            and value.strip().casefold() in PROTECTED_ROLE_IDENTIFIERS
            for value in (role.name, role.code)
        )

    @classmethod
    def _protected_failure(cls, role_id: int, object_name: str):
        return failure_item(
            role_id,
            object_name=object_name,
            error_code="PROTECTED_OBJECT",
            message="系统角色不可删除",
            retryable=False,
        )

    @classmethod
    def _delete_one_for_batch(
        cls,
        role_id: int,
        object_name: str,
        *,
        missing_code: str,
        missing_message: str,
    ) -> dict:
        """在独立事务中复核并删除单个角色。"""
        try:
            with transaction.atomic():
                locked_role = Roles.objects.select_for_update().filter(id=role_id).first()
                if locked_role is None:
                    return {
                        "success": False,
                        "failure": failure_item(
                            role_id,
                            object_name=object_name,
                            error_code=missing_code,
                            message=missing_message,
                        ),
                    }
                if cls._is_protected_role(locked_role):
                    return {
                        "success": False,
                        "failure": cls._protected_failure(role_id, object_name),
                    }
                affected_user_ids = list(
                    Users.objects.filter(roles=locked_role).values_list("id", flat=True)
                )
                locked_role.delete()
        except Exception:  # noqa: BLE001 - 单条失败不能阻塞其余项目
            return {
                "success": False,
                "failure": failure_item(
                    role_id,
                    object_name=object_name,
                    error_code="DELETE_FAILED",
                    message="删除角色失败",
                    retryable=True,
                ),
            }

        # 数据库提交后，缓存只是后处理；其故障不能把已删除对象报告成失败。
        for user_id in affected_user_ids:
            try:
                clear_user_permission_cache(user_id)
            except Exception as exc:  # noqa: BLE001 - 记录后继续处理其余缓存
                logger.error("角色 %s 删除后清理用户 %s 权限缓存失败: %s", role_id, user_id, exc)
        return {"success": True}

    @action(detail=True, methods=['put'], url_path='menus')
    def assign_menus(self, request, *args, **kwargs):
        """分配角色菜单权限"""
        serializer = RolesMenuAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_ids = serializer.validated_data['menu_ids']
        set_audit_object(
            request,
            "system.roles",
            kwargs.get(self.lookup_url_kwarg or self.lookup_field, ""),
            changed_fields=["menuIds"],
            assigned_menu_ids=menu_ids[:100],
        )
        permissions = Permissions.objects.filter(id__in=menu_ids)
        if permissions.count() != len(set(menu_ids)):
            raise ValidationError({'menuIds': '权限不存在'})

        role = self.get_object()
        role.permissions.set(permissions)
        return Response(data=list(role.permissions.values_list('id', flat=True)))


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
