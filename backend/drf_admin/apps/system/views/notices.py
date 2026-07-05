# -*- coding: utf-8 -*-

from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from drf_admin.apps.system.models import Notices
from drf_admin.apps.system.serializers.notices import NoticesSerializer
from drf_admin.apps.system.services.data_scope import apply_notice_admin_data_scope
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView


class NoticesViewSet(AdminViewSet):
    """
    通知公告管理接口
    """

    queryset = Notices.objects.all()
    serializer_class = NoticesSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "content")

    def get_queryset(self):
        """按发布人数据范围限制后台通知管理对象。"""
        return apply_notice_admin_data_scope(super().get_queryset(), self.request.user)

    @staticmethod
    def get_action_permission_mapping():
        """将发布、撤回和路径批量删除动作映射到通知公告权限码。"""
        mapping = AdminViewSet.get_action_permission_mapping()
        return {
            **mapping,
            "update_by_id": "edit",
            "delete_by_ids": "delete",
            "publish": "publish",
            "revoke": "revoke",
        }

    def list(self, request, *args, **kwargs):
        """返回前端管理页依赖的 list/total 分页结构。"""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.filter_by_query_params(queryset, request)
        # 查询参数经 CamelCaseMiddleWare 下划线化，视图层读取 snake_case 键。
        page_num = max(int(request.query_params.get("page_num", 1)), 1)
        page_size = max(int(request.query_params.get("page_size", 10)), 1)
        offset = (page_num - 1) * page_size
        serializer = self.get_serializer(queryset[offset: offset + page_size], many=True)
        return Response(data={"list": serializer.data, "total": queryset.count()})

    def filter_by_query_params(self, queryset, request):
        """按前端查询字段过滤，避免管理页筛选契约漂移。"""
        title = request.query_params.get("title")
        publish_status = request.query_params.get("publish_status")
        if title:
            queryset = queryset.filter(title__icontains=title)
        if publish_status not in (None, ""):
            queryset = queryset.filter(publish_status=int(publish_status))
        return queryset

    def perform_create(self, serializer):
        """创建时写入发布人信息，保持与 FastAPI 响应字段一致。"""
        user = self.request.user
        publisher_name = getattr(user, "name", "") or getattr(user, "username", "")
        serializer.save(publisher_id=user.id, publisher_name=publisher_name, publish_status=0)

    def update(self, request, *args, **kwargs):
        """已发布通知不允许编辑，保持与 FastAPI 写接口规则一致。"""
        instance = self.get_object()
        if instance.publish_status == 1:
            raise ValidationError("已发布通知不允许编辑")
        return super().update(request, *args, **kwargs)

    def update_by_id(self, request, ids: str):
        """从共享路径中解析单个 ID，并转交标准更新流程。"""
        self.kwargs[self.lookup_url_kwarg or self.lookup_field] = parse_single_notice_id(ids)
        return self.update(request)

    def delete_by_ids(self, request, ids: str):
        """按前端路径中的逗号分隔 ID 删除未发布通知。"""
        notice_ids = parse_notice_ids(ids)
        queryset = self.get_queryset().filter(id__in=notice_ids)
        if queryset.count() != len(set(notice_ids)):
            raise NotFound("通知不存在")
        if queryset.filter(publish_status=1).exists():
            raise ValidationError("已发布通知不允许删除")
        queryset.delete()
        return Response(data={})

    def publish(self, request, pk: int):
        """发布通知并记录发布时间。"""
        notice = self.get_object()
        notice.publish_status = 1
        notice.publish_time = timezone.now()
        notice.revoke_time = None
        notice.save(update_fields=["publish_status", "publish_time", "revoke_time", "update_time"])
        return Response(data={})

    def revoke(self, request, pk: int):
        """撤回已发布通知并记录撤回时间。"""
        notice = self.get_object()
        notice.publish_status = -1
        notice.revoke_time = timezone.now()
        notice.save(update_fields=["publish_status", "revoke_time", "update_time"])
        return Response(data={})


def parse_notice_ids(ids: str) -> list[int]:
    """解析路径中的通知 ID 列表，非法输入直接暴露为校验错误。"""
    try:
        notice_ids = [int(item) for item in ids.split(",") if item.strip()]
    except ValueError as exc:
        raise ValidationError("通知 ID 格式错误") from exc
    if not notice_ids:
        raise ValidationError("通知 ID 不能为空")
    return notice_ids


def parse_single_notice_id(ids: str) -> int:
    """解析单个通知 ID，避免更新接口接受批量 ID。"""
    notice_ids = parse_notice_ids(ids)
    if len(notice_ids) != 1:
        raise ValidationError("更新通知只能传入单个 ID")
    return notice_ids[0]


class NoticesAPIView(AutoPermissionAPIView):
    """
    我的通知

    返回当前登录用户可见的已发布通知，分页结构与 FastAPI 的 `my-page` 对齐。

    说明：Django 后端当前没有 `NoticeReads` 模型，不跟踪每用户已读状态，
    因此 `isRead` 统一返回 0（视为未读）。如果前端按 `isRead=1` 过滤，将返回空列表。
    """

    def get(self, request):
        """返回当前用户可见的已发布通知分页列表。"""
        # 查询参数经 CamelCaseMiddleWare 下划线化，视图层读取 snake_case 键。
        user = request.user
        title = request.query_params.get("title")
        is_read_param = request.query_params.get("is_read")
        page_num = max(int(request.query_params.get("page_num", 1)), 1)
        page_size = max(int(request.query_params.get("page_size", 10)), 1)

        queryset = Notices.objects.filter(publish_status=1)
        if title:
            queryset = queryset.filter(title__icontains=title)
        queryset = queryset.order_by("-publish_time", "-create_time")

        visible = [notice for notice in queryset if self._is_visible_to(notice, user)]

        # Django 不跟踪每用户已读状态，全部视为未读；按已读过滤时返回空列表。
        if is_read_param not in (None, "") and int(is_read_param) == 1:
            visible = []

        total = len(visible)
        offset = (page_num - 1) * page_size
        page_items = visible[offset: offset + page_size]
        serializer = NoticesSerializer(page_items, many=True)
        data = [{**dict(item), "is_read": 0} for item in serializer.data]
        return Response(data={"list": data, "total": total})

    @staticmethod
    def _is_visible_to(notice, user) -> bool:
        """全体通知对所有人可见；指定通知仅对目标用户可见。"""
        if notice.target_type == 1:
            return True
        return user.id in (notice.target_user_ids or [])
