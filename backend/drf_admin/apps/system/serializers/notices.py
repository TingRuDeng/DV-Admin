# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Notices


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
