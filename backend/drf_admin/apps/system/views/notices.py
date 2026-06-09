# -*- coding: utf-8 -*-

from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from drf_admin.apps.system.models import Notices
from drf_admin.apps.system.serializers.notices import NoticesSerializer
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView


class NoticesViewSet(AdminViewSet):
    """
    通知公告管理接口
    """

    queryset = Notices.objects.all()
    serializer_class = NoticesSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "content")

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
        page_num = max(int(request.query_params.get("pageNum", 1)), 1)
        page_size = max(int(request.query_params.get("pageSize", 10)), 1)
        offset = (page_num - 1) * page_size
        serializer = self.get_serializer(queryset[offset: offset + page_size], many=True)
        return Response(data={"list": serializer.data, "total": queryset.count()})

    def filter_by_query_params(self, queryset, request):
        """按前端查询字段过滤，避免管理页筛选契约漂移。"""
        title = request.query_params.get("title")
        publish_status = request.query_params.get("publishStatus")
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
            raise ValidationError("通知不存在")
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
    我的通知薄实现
    """

    def get(self, request):
        """返回我的通知列表占位结构，保持历史接口兼容。"""
        return Response(data={"list": []})
