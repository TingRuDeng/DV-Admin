# -*- coding: utf-8 -*-

from rest_framework import serializers


class BatchDeleteSuccessItemSerializer(serializers.Serializer):
    """批量删除成功项的共享响应字段。"""

    object_id = serializers.CharField()
    object_name = serializers.CharField(required=False, allow_blank=True)


class BatchDeleteFailureSerializer(serializers.Serializer):
    """批量删除失败项的共享响应字段。"""

    object_id = serializers.CharField()
    object_name = serializers.CharField(required=False, allow_blank=True)
    error_code = serializers.CharField()
    message = serializers.CharField()
    retryable = serializers.BooleanField(required=False, default=False)


class BatchDeleteResultSerializer(serializers.Serializer):
    """用户、角色和通知共享的结果化批量删除响应。"""

    status = serializers.ChoiceField(choices=("succeeded", "partial_failed", "failed"))
    total_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    processed_count = serializers.IntegerField()
    success_items = BatchDeleteSuccessItemSerializer(many=True)
    failures = BatchDeleteFailureSerializer(many=True)
