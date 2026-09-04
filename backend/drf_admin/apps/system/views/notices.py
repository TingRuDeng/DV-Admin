# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from drf_admin.apps.system.models import NoticeReads, Notices
from drf_admin.apps.system.serializers.batch_delete import BatchDeleteResultSerializer
from drf_admin.apps.system.serializers.notices import NoticeMyPageSerializer, NoticesSerializer
from drf_admin.apps.system.services.batch_delete import (
    build_batch_delete_result,
    failure_item,
    normalize_batch_ids,
    preflight_batch_ids,
    success_item,
)
from drf_admin.apps.system.services.data_scope import apply_notice_admin_data_scope
from drf_admin.utils.audit import set_audit_context, set_audit_object
from drf_admin.utils.views import AdminViewSet, AutoPermissionAPIView


class NoticesViewSet(AdminViewSet):
    """
    通知公告管理接口
    """

    queryset = Notices.objects.all()
    serializer_class = NoticesSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "content")

    def get_serializer_context(self):
        """后台通知管理读路径启用正文原文权限控制。"""
        context = super().get_serializer_context()
        if getattr(self, "action", None) in {"list", "retrieve"}:
            context["mask_notice_content"] = True
        return context

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
            "retry_batch_delete": "delete",
            "publish": "publish",
            "revoke": "revoke",
        }

    def list(self, request, *args, **kwargs):
        """返回前端管理页依赖的 list/total 分页结构。"""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.filter_by_query_params(queryset, request)
        # 查询参数经 CamelCaseMiddleWare 下划线化，视图层读取 snake_case 键。
        page_num = parse_positive_query_int(
            request.query_params.get("page_num"),
            name="pageNum",
            default=1,
        )
        page_size = parse_positive_query_int(
            request.query_params.get("page_size"),
            name="pageSize",
            default=10,
            maximum=100,
        )
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
        notice_id = parse_single_notice_id(ids)
        self.kwargs[self.lookup_url_kwarg or self.lookup_field] = notice_id
        set_audit_object(
            request,
            "system.notices",
            notice_id,
            changed_fields=list(request.data.keys()) if hasattr(request.data, "keys") else [],
        )
        return self.update(request)

    def multiple_delete(self, request, *args, **kwargs):
        """使用 JSON body 批量删除通知并返回逐条结果。"""
        return self._run_batch_delete(request, retry=False)

    def retry_batch_delete(self, request, *args, **kwargs):
        """逐条重新校验并重试通知删除。"""
        return self._run_batch_delete(request, retry=True)

    def delete_by_ids(self, request, ids: str):
        """按历史逗号分隔路径删除通知，并复用结果化处理。"""
        return self._run_batch_delete(request, retry=False, ids=parse_notice_ids(ids))

    def _run_batch_delete(self, request, *, retry: bool, ids=None):
        """执行一次批量删除或重试，单个通知失败不影响其他通知。"""
        unique_ids = normalize_batch_ids(
            request.data.get("ids") if ids is None else ids,
            resource_name="通知",
        )
        notices_by_id = {}
        if not retry:
            preflight_batch_ids(
                self.get_queryset(),
                unique_ids,
                resource_name="通知",
            )
            notices_by_id = {
                notice.id: notice
                for notice in self.get_queryset().filter(id__in=unique_ids)
            }

        success_items = []
        failures = []
        for notice_id in unique_ids:
            notice = (
                Notices.objects.filter(id=notice_id).first()
                if retry
                else notices_by_id.get(notice_id)
            )
            if notice is None:
                failures.append(
                    failure_item(
                        notice_id,
                        error_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                        message="通知已不存在" if retry else "通知不存在",
                    )
                )
                continue

            object_name = notice.title or ""
            if retry and not self.get_queryset().filter(id=notice_id).exists():
                failures.append(
                    failure_item(
                        notice_id,
                        object_name=object_name,
                        error_code="NOT_FOUND",
                        message="通知不存在",
                    )
                )
                continue

            outcome = self._delete_one_for_batch(
                notice_id,
                object_name,
                missing_code="ALREADY_DELETED" if retry else "NOT_FOUND",
                missing_message="通知已不存在" if retry else "通知不存在",
            )
            if outcome.get("success"):
                success_items.append(success_item(notice_id, object_name))
            else:
                failures.append(outcome["failure"])

        result = build_batch_delete_result(unique_ids, success_items, failures)
        set_audit_object(request, "system.notices", "", changed_fields=["ids"])
        set_audit_context(
            request,
            batch_count=result["total_count"],
            batch_ids=[str(item) for item in unique_ids[:100]],
            success_count=result["success_count"],
            failed_count=result["failed_count"],
            failure_codes=sorted({item["error_code"] for item in failures}),
            retry=retry,
        )
        return Response(data=BatchDeleteResultSerializer(result).data)

    def _delete_one_for_batch(
        self,
        notice_id: int,
        object_name: str,
        *,
        missing_code: str,
        missing_message: str,
    ) -> dict:
        """在独立事务中复核状态并删除单个通知。"""
        try:
            with transaction.atomic():
                notice = self.get_queryset().filter(id=notice_id).select_for_update().first()
                if notice is None:
                    # 先锁定无范围对象以区分“已删除”和“当前操作者无权访问”。
                    unscoped_notice = (
                        Notices.objects.filter(id=notice_id).select_for_update().first()
                    )
                    if unscoped_notice is not None:
                        return {
                            "success": False,
                            "failure": failure_item(
                                notice_id,
                                object_name=object_name,
                                error_code="NOT_FOUND",
                                message="通知不存在",
                            ),
                        }
                    return {
                        "success": False,
                        "failure": failure_item(
                            notice_id,
                            object_name=object_name,
                            error_code=missing_code,
                            message=missing_message,
                        ),
                    }
                if notice.publish_status == 1:
                    return {
                        "success": False,
                        "failure": failure_item(
                            notice_id,
                            object_name=object_name,
                            error_code="PUBLISHED_OBJECT",
                            message="已发布通知不允许删除",
                            retryable=True,
                        ),
                    }
                notice.delete()
            return {"success": True}
        except Exception:  # noqa: BLE001 - 单条失败不能阻塞其余项目
            return {
                "success": False,
                "failure": failure_item(
                    notice_id,
                    object_name=object_name,
                    error_code="DELETE_FAILED",
                    message="删除通知失败",
                    retryable=True,
                ),
            }

    def publish(self, request, pk: int):
        """发布通知并记录发布时间。"""
        set_audit_object(request, "system.notices", pk, changed_fields=["publishStatus"])
        notice = self.get_object()
        notice.publish_status = 1
        notice.publish_time = timezone.now()
        notice.revoke_time = None
        notice.save(update_fields=["publish_status", "publish_time", "revoke_time", "update_time"])
        return Response(data={})

    def revoke(self, request, pk: int):
        """撤回已发布通知并记录撤回时间。"""
        set_audit_object(request, "system.notices", pk, changed_fields=["publishStatus"])
        notice = self.get_object()
        notice.publish_status = -1
        notice.revoke_time = timezone.now()
        notice.save(update_fields=["publish_status", "revoke_time", "update_time"])
        return Response(data={})


def parse_notice_ids(ids: str) -> list[int]:
    """解析路径中的通知 ID 列表，非法输入直接暴露为校验错误。"""
    try:
        notice_ids = [int(item.strip()) for item in ids.split(",") if item.strip()]
    except ValueError as exc:
        raise ValidationError("通知 ID 格式错误") from exc
    return normalize_batch_ids(notice_ids, resource_name="通知")


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

    读取状态持久化到 `NoticeReads`，与 FastAPI 的详情和全部已读语义一致。
    """

    model = Notices

    def get(self, request):
        """返回当前用户可见的已发布通知分页列表。"""
        # 查询参数经 CamelCaseMiddleWare 下划线化，视图层读取 snake_case 键。
        user = request.user
        title = request.query_params.get("title")
        is_read_param = request.query_params.get("is_read")
        page_num = parse_positive_query_int(
            request.query_params.get("page_num"),
            name="pageNum",
            default=1,
        )
        page_size = parse_positive_query_int(
            request.query_params.get("page_size"),
            name="pageSize",
            default=10,
            maximum=100,
        )

        queryset = Notices.objects.filter(publish_status=1)
        if title:
            queryset = queryset.filter(title__icontains=title)
        queryset = queryset.order_by("-publish_time", "-create_time", "-id")

        read_exists = NoticeReads.objects.filter(
            user_id=user.id,
            notice_id=OuterRef("pk"),
        )
        queryset = queryset.annotate(_is_read=Exists(read_exists))
        is_read = None
        if is_read_param not in (None, ""):
            try:
                is_read = int(is_read_param)
            except (TypeError, ValueError) as exc:
                raise ValidationError("isRead 只能为 0 或 1") from exc
            if is_read not in (0, 1):
                raise ValidationError("isRead 只能为 0 或 1")

        offset = (page_num - 1) * page_size
        total = 0
        page_items = []
        for notice in queryset.iterator(chunk_size=200):
            if not self._is_visible_to(notice, user):
                continue
            if is_read is not None and bool(notice._is_read) != bool(is_read):
                continue
            if offset <= total < offset + page_size:
                page_items.append(notice)
            total += 1
        serializer = NoticeMyPageSerializer(page_items, many=True, context={"request": request})
        return Response(data={"list": serializer.data, "total": total})

    @staticmethod
    def _is_visible_to(notice, user) -> bool:
        """全体通知对所有人可见；指定通知仅对目标用户可见。"""
        if notice.target_type == 1:
            return True
        return user.id in (notice.target_user_ids or [])


class NoticeDetailAPIView(AutoPermissionAPIView):
    """返回当前用户可见的已发布通知，并持久化已读状态。"""

    model = Notices

    def get(self, request, pk: int):
        notice = Notices.objects.filter(id=pk, publish_status=1).first()
        if notice is None or not NoticesAPIView._is_visible_to(notice, request.user):
            raise NotFound("通知不存在")
        NoticeReads.objects.get_or_create(notice=notice, user_id=request.user.id)
        serializer = NoticesSerializer(notice, context={"request": request})
        return Response(serializer.data)


class NoticeReadAllAPIView(AutoPermissionAPIView):
    """把当前用户可见的全部已发布通知标记为已读。"""

    model = Notices

    @staticmethod
    def get_method_permission_mapping():
        return {"put": "query"}

    def put(self, request):
        pending = []
        queryset = Notices.objects.filter(publish_status=1).only(
            "id",
            "target_type",
            "target_user_ids",
        )
        for notice in queryset.iterator(chunk_size=200):
            if not NoticesAPIView._is_visible_to(notice, request.user):
                continue
            pending.append(NoticeReads(notice_id=notice.id, user_id=request.user.id))
            if len(pending) == 200:
                NoticeReads.objects.bulk_create(pending, ignore_conflicts=True)
                pending.clear()
        if pending:
            NoticeReads.objects.bulk_create(pending, ignore_conflicts=True)
        return Response(data={})


def parse_positive_query_int(raw_value, *, name: str, default: int, maximum: int | None = None) -> int:
    """解析正整数查询参数，并与 FastAPI 的分页约束保持一致。"""
    if raw_value in (None, ""):
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} 必须为正整数") from exc
    if value < 1:
        raise ValidationError(f"{name} 必须为正整数")
    if maximum is not None and value > maximum:
        raise ValidationError(f"{name} 不能大于 {maximum}")
    return value
