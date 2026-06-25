"""
系统部门模型
"""

from __future__ import annotations

from tortoise import fields

from app.db.models.base import BaseModel


class Departments(BaseModel):
    """
    部门模型

    定义组织架构中的部门，支持树形结构。
    """

    name = fields.CharField(max_length=32, description="部门名称")
    status = fields.IntField(default=1, description="状态")
    sort = fields.IntField(default=0, description="排序")

    parent: fields.ForeignKeyNullableRelation[Departments] = fields.ForeignKeyField(
        "models.Departments",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
        description="父部门",
    )
    parent_id: int | None

    class Meta:
        table = "system_departments"
        ordering = ["sort"]
        indexes = (
            ("status",),
            ("parent_id", "sort"),
        )

    def __str__(self) -> str:
        return self.name
