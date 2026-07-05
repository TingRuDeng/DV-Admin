# -*- coding: utf-8 -*-

from collections import Counter
from datetime import datetime, timedelta

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_admin.apps.system.models import OperationLog
from drf_admin.apps.system.serializers.logs import OperationLogSerializer
from drf_admin.utils.permissions import RBACPermission


def parse_optional_int(value: str | None, field_name: str) -> int | None:
    """解析外部整数字段，非法时返回 400，避免未处理异常泄露为 500。"""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field_name: "必须是整数"}) from exc


def parse_positive_int(value: str | None, field_name: str, default: int) -> int:
    """解析分页正整数；保留历史的最小值兜底语义。"""
    parsed = parse_optional_int(value, field_name)
    return max(parsed if parsed is not None else default, 1)


def parse_optional_datetime(value: str | None, field_name: str):
    """解析 ISO 日期时间；无时区输入按当前时区处理。"""
    if value in (None, ""):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError({field_name: "必须是 ISO 8601 日期时间"}) from exc
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return timezone.localtime(parsed)


def parse_id_list(ids: str) -> list[int]:
    """解析逗号分隔 ID 列表，拒绝空值和非正整数。"""
    parsed_ids: list[int] = []
    for item in ids.split(","):
        value = item.strip()
        if not value:
            continue
        parsed_id = parse_optional_int(value, "ids")
        if parsed_id is None or parsed_id < 1:
            raise ValidationError({"ids": "必须是正整数列表"})
        parsed_ids.append(parsed_id)
    if not parsed_ids:
        raise ValidationError({"ids": "不能为空"})
    return parsed_ids


class LogPermissionAPIView(APIView):
    """显式声明 system:logs 权限码，对齐 FastAPI 与前端契约。"""

    permission_classes = [RBACPermission]
    required_permissions = {
        "get": ["system:logs:query"],
        "delete": ["system:logs:delete"],
    }


class LogPageAPIView(LogPermissionAPIView):
    """操作日志分页列表，结构与 FastAPI `/logs/page` 对齐为 list/total。"""

    def get(self, request):
        queryset = OperationLog.objects.all()
        params = request.query_params  # 经 CamelCaseMiddleWare 下划线化

        operation = params.get("operation")
        username = params.get("username")
        method = params.get("method")
        status_param = params.get("status")
        start_time = params.get("start_time")
        end_time = params.get("end_time")

        status_value = parse_optional_int(status_param, "status")
        start_time_value = parse_optional_datetime(start_time, "startTime")
        end_time_value = parse_optional_datetime(end_time, "endTime")
        if operation:
            queryset = queryset.filter(operation__icontains=operation)
        if username:
            queryset = queryset.filter(username__icontains=username)
        if method:
            queryset = queryset.filter(method=method.upper())
        if status_value is not None:
            queryset = queryset.filter(status=status_value)
        if start_time_value is not None:
            queryset = queryset.filter(created_at__gte=start_time_value)
        if end_time_value is not None:
            queryset = queryset.filter(created_at__lte=end_time_value)

        queryset = queryset.order_by("-created_at")
        page_num = parse_positive_int(params.get("page_num"), "pageNum", 1)
        page_size = parse_positive_int(params.get("page_size"), "pageSize", 10)
        offset = (page_num - 1) * page_size
        total = queryset.count()
        serializer = OperationLogSerializer(queryset[offset: offset + page_size], many=True)
        return Response(data={"list": serializer.data, "total": total})


class VisitTrendAPIView(LogPermissionAPIView):
    """访问趋势（按日聚合），与 FastAPI VisitTrendOut 对齐为 [{date, count}]。"""

    def get(self, request):
        params = request.query_params
        end_date = params.get("end_date")
        start_date = params.get("start_date")
        end = parse_optional_datetime(end_date, "endDate") or timezone.localtime()
        start = parse_optional_datetime(start_date, "startDate") or (end - timedelta(days=7))

        logs = OperationLog.objects.filter(created_at__gte=start, created_at__lte=end)
        counter: Counter = Counter()
        for created in logs.values_list("created_at", flat=True):
            counter[timezone.localtime(created).strftime("%Y-%m-%d")] += 1

        results = []
        cursor = start.date()
        end_day = end.date()
        while cursor <= end_day:
            key = cursor.strftime("%Y-%m-%d")
            results.append({"date": key, "count": counter.get(key, 0)})
            cursor += timedelta(days=1)
        return Response(data=results)


class VisitStatsAPIView(LogPermissionAPIView):
    """访问统计汇总，与 FastAPI VisitStatsOut 对齐。"""

    def get(self, request):
        now = timezone.localtime()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        all_logs = OperationLog.objects.all()
        avg_time = all_logs.filter(execution_time__gt=0).aggregate(
            avg_execution_time=Avg("execution_time")
        )["avg_execution_time"]
        avg_execution_time = int(avg_time) if avg_time is not None else 0
        top_users = list(
            all_logs.exclude(username="")
            .values("username")
            .annotate(count=Count("id"))
            .order_by("-count", "username")[:10]
        )
        top_paths = list(
            all_logs.exclude(path="")
            .values("path")
            .annotate(count=Count("id"))
            .order_by("-count", "path")[:10]
        )

        data = {
            "total_count": all_logs.count(),
            "today_count": all_logs.filter(created_at__gte=today_start).count(),
            "week_count": all_logs.filter(created_at__gte=week_start).count(),
            "month_count": all_logs.filter(created_at__gte=month_start).count(),
            "success_count": all_logs.filter(status=1).count(),
            "fail_count": all_logs.filter(status=0).count(),
            "avg_execution_time": avg_execution_time,
            "top_users": top_users,
            "top_paths": top_paths,
        }
        return Response(data=data)


class LogDeleteAPIView(LogPermissionAPIView):
    """按逗号分隔的 ID 批量删除操作日志。"""

    def delete(self, request, ids: str):
        id_list = parse_id_list(ids)
        OperationLog.objects.filter(id__in=id_list).delete()
        return Response(data={})


class LogClearAPIView(LogPermissionAPIView):
    """清理指定天数之前的操作日志。"""

    def delete(self, request, days: int):
        threshold = timezone.now() - timedelta(days=int(days))
        OperationLog.objects.filter(created_at__lt=threshold).delete()
        return Response(data={})
