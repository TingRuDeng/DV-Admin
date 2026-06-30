# -*- coding: utf-8 -*-

from collections import Counter
from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_admin.apps.system.models import OperationLog
from drf_admin.apps.system.serializers.logs import OperationLogSerializer
from drf_admin.utils.permissions import RBACPermission


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

        if operation:
            queryset = queryset.filter(operation__icontains=operation)
        if username:
            queryset = queryset.filter(username__icontains=username)
        if method:
            queryset = queryset.filter(method=method.upper())
        if status_param not in (None, ""):
            queryset = queryset.filter(status=int(status_param))
        if start_time:
            queryset = queryset.filter(created_at__gte=start_time)
        if end_time:
            queryset = queryset.filter(created_at__lte=end_time)

        queryset = queryset.order_by("-created_at")
        page_num = max(int(params.get("page_num", 1)), 1)
        page_size = max(int(params.get("page_size", 10)), 1)
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
        end = timezone.localtime() if not end_date else timezone.localtime(timezone.datetime.fromisoformat(end_date))
        start = (end - timedelta(days=7)) if not start_date else timezone.localtime(
            timezone.datetime.fromisoformat(start_date)
        )

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
        recent = list(all_logs.order_by("-created_at")[:1000])

        exec_times = [log.execution_time for log in all_logs.filter(execution_time__gt=0)]
        avg_execution_time = int(sum(exec_times) / len(exec_times)) if exec_times else 0

        top_users = [
            {"username": username, "count": count}
            for username, count in Counter(
                log.username for log in recent if log.username
            ).most_common(10)
        ]
        top_paths = [
            {"path": path, "count": count}
            for path, count in Counter(log.path for log in recent if log.path).most_common(10)
        ]

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
        id_list = [int(item) for item in ids.split(",") if item.strip()]
        OperationLog.objects.filter(id__in=id_list).delete()
        return Response(data={})


class LogClearAPIView(LogPermissionAPIView):
    """清理指定天数之前的操作日志。"""

    def delete(self, request, days: int):
        threshold = timezone.now() - timedelta(days=int(days))
        OperationLog.objects.filter(created_at__lt=threshold).delete()
        return Response(data={})
