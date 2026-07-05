# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import OperationLog
from drf_admin.apps.system.services.field_permission import apply_log_field_permissions


class OperationLogSerializer(serializers.ModelSerializer):
    """
    操作日志序列化器

    字段集合与 FastAPI `OperationLogOut` 对齐（含 createdAt/updatedAt）。
    """

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "user_id",
            "username",
            "name",
            "operation",
            "method",
            "path",
            "query_params",
            "request_body",
            "response_status",
            "response_body",
            "ip",
            "browser",
            "os",
            "execution_time",
            "status",
            "error_msg",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is None:
            return data
        return apply_log_field_permissions(data, request.user)
