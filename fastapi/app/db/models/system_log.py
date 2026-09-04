"""
系统操作日志模型
"""

from typing import Any

from tortoise import fields
from tortoise.fields.db_defaults import SqlDefault
from tortoise.indexes import Index

from app.db.models.base import BaseModel


class OperationLog(BaseModel):
    """
    操作日志模型

    记录用户的操作行为，包括请求信息、响应状态、执行时间等。
    """

    user_id = fields.IntField(null=True, description="用户ID")
    username = fields.CharField(max_length=150, default="", description="用户名")
    name = fields.CharField(max_length=50, default="", description="用户姓名")

    operation = fields.CharField(max_length=100, default="", description="操作描述")
    method = fields.CharField(max_length=10, default="", description="请求方法")
    path = fields.CharField(max_length=500, default="", description="请求路径")
    request_id = fields.CharField(
        max_length=64,
        default="",
        db_default="",
        description="请求ID",
    )
    object_type = fields.CharField(
        max_length=100,
        default="",
        db_default="",
        description="业务对象类型",
    )
    object_id = fields.CharField(
        max_length=255,
        default="",
        db_default="",
        description="业务对象ID",
    )
    query_params = fields.TextField(default="", description="查询参数")
    request_context: fields.Field[dict[str, Any]] = fields.JSONField(
        default=dict,
        db_default=SqlDefault("('{}')"),
        description="结构化请求上下文",
    )

    request_body = fields.TextField(default="", description="请求体")
    response_status = fields.IntField(default=0, description="响应状态码")
    response_body = fields.TextField(default="", description="响应体")

    ip = fields.CharField(max_length=50, default="", description="IP地址")
    browser = fields.CharField(max_length=100, default="", description="浏览器")
    os = fields.CharField(max_length=100, default="", description="操作系统")
    execution_time = fields.IntField(default=0, description="执行时间(毫秒)")

    status = fields.IntField(default=1, description="状态(1:成功；0:失败)")
    error_msg = fields.TextField(default="", description="错误信息")

    class Meta:
        table = "system_operation_log"
        ordering = ["-created_at"]
        indexes = (
            Index(fields=("user_id",)),
            Index(fields=("username",)),
            Index(fields=("status",)),
            Index(fields=("method",)),
            Index(fields=("request_id",)),
            Index(fields=("object_type", "object_id")),
            Index(fields=("user_id", "created_at")),
            Index(fields=("status", "created_at")),
        )

    def __str__(self) -> str:
        return f"{self.username} - {self.operation}"
