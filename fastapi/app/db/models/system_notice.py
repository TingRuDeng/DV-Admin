"""
系统通知公告模型
"""

from __future__ import annotations

from datetime import datetime

from tortoise import fields

from app.db.models.base import BaseModel


class Notices(BaseModel):
    """通知公告模型"""

    title = fields.CharField(max_length=200, description="标题")
    content = fields.TextField(description="内容")
    type = fields.IntField(default=0, description="类型")
    level = fields.CharField(max_length=10, default="L", description="级别")
    target_type = fields.IntField(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: fields.Field[list[int]] = fields.JSONField(
        default=list,
        description="目标用户ID列表",
    )

    publisher_id = fields.IntField(null=True, description="发布人ID")
    publisher_name = fields.CharField(max_length=50, default="", description="发布人名称")

    publish_status = fields.IntField(
        default=0,
        description="发布状态(0:未发布;1:已发布;-1:已撤回)",
    )
    publish_time: datetime | None = fields.DatetimeField(
        null=True,
        description="发布时间",
    )
    revoke_time: datetime | None = fields.DatetimeField(
        null=True,
        description="撤回时间",
    )

    class Meta:
        table = "system_notices"
        ordering = ["-created_at"]
        indexes = (
            ("publish_status",),
            ("publisher_id",),
            ("publish_status", "publish_time"),
        )


class NoticeReads(BaseModel):
    """通知已读记录"""

    notice: fields.ForeignKeyRelation[Notices] = fields.ForeignKeyField(
        "models.Notices",
        related_name="reads",
        on_delete=fields.CASCADE,
        description="通知ID",
    )
    notice_id: int
    user_id = fields.IntField(description="用户ID")
    read_time = fields.DatetimeField(auto_now_add=True, description="已读时间")

    class Meta:
        table = "system_notice_reads"
        unique_together = ("notice", "user_id")
        indexes = (("user_id",),)
