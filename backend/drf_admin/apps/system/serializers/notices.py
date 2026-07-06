# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Notices
from drf_admin.apps.system.services.field_permission import (
    apply_notice_field_permissions,
    can_write_notice_target_fields,
    has_notice_target_write,
)


class NoticesSerializer(serializers.ModelSerializer):
    """
    通知公告序列化器
    """

    class Meta:
        model = Notices
        fields = "__all__"
        read_only_fields = (
            "publisher_id",
            "publisher_name",
            "publish_status",
            "publish_time",
            "revoke_time",
        )

    def validate(self, attrs):
        """校验通知指定用户目标字段写入权限。"""
        request = self.context.get("request")
        user = request.user if request else None
        if has_notice_target_write(attrs) and not can_write_notice_target_fields(user):
            raise serializers.ValidationError("缺少通知目标字段写入权限，不能写入指定用户范围")
        return attrs

    def to_representation(self, instance):
        """按通知目标字段读取权限处理输出。"""
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is None:
            return data
        if request.method != "GET":
            return data
        return apply_notice_field_permissions(
            data,
            request.user,
            mask_content=bool(self.context.get("mask_notice_content")),
        )
