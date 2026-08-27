from django.db import models

from drf_admin.utils.models import BaseModel


class Notices(BaseModel):
    """
    通知公告
    """

    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    type = models.IntegerField(default=0, verbose_name="类型")
    level = models.CharField(max_length=10, default="L", verbose_name="级别")
    target_type = models.IntegerField(default=1, verbose_name="目标类型")
    target_user_ids = models.JSONField(default=list, verbose_name="目标用户ID列表")
    publisher_id = models.IntegerField(null=True, blank=True, verbose_name="发布人ID")
    publisher_name = models.CharField(max_length=50, blank=True, default="", verbose_name="发布人名称")
    publish_status = models.IntegerField(default=0, verbose_name="发布状态")
    publish_time = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")
    revoke_time = models.DateTimeField(null=True, blank=True, verbose_name="撤回时间")

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = "system_notices"
        verbose_name = "通知公告"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]
        indexes = [
            models.Index(fields=["publish_status"]),
            models.Index(fields=["publisher_id"]),
            models.Index(fields=["publish_status", "publish_time"]),
        ]


class NoticeReads(BaseModel):
    """用户通知已读记录。"""

    notice = models.ForeignKey(
        Notices,
        related_name="reads",
        on_delete=models.CASCADE,
        verbose_name="通知",
    )
    user_id = models.IntegerField(verbose_name="用户ID")
    read_time = models.DateTimeField(auto_now_add=True, verbose_name="已读时间")

    objects = models.Manager()

    class Meta:
        db_table = "system_notice_reads"
        verbose_name = "通知已读记录"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=["notice", "user_id"],
                name="system_notice_reads_notice_user_uniq",
            ),
        ]
        indexes = [models.Index(fields=["user_id"])]
