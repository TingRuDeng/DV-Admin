"""
系统字典模型
"""

from __future__ import annotations

from tortoise import fields

from app.db.models.base import BaseModel


class DictData(BaseModel):
    """
    字典类型模型

    定义字典数据的类型。
    """

    name = fields.CharField(max_length=50, description="字典名称")
    dict_code = fields.CharField(max_length=32, unique=True, description="字典编码")
    status = fields.IntField(default=1, description="状态")
    remark = fields.CharField(max_length=100, default="", description="描述")
    items: fields.BackwardFKRelation[DictItems]

    class Meta:
        table = "system_dicts"
        ordering = ["-created_at"]
        indexes = (
            ("dict_code",),
            ("status",),
        )

    def __str__(self) -> str:
        return self.name


class DictItems(BaseModel):
    """
    字典项模型

    定义字典的具体数据项。
    """

    label = fields.CharField(max_length=32, description="标签")
    value = fields.CharField(max_length=32, description="值")
    status = fields.IntField(default=1, description="状态")

    dict_data: fields.ForeignKeyRelation[DictData] = fields.ForeignKeyField(
        "models.DictData",
        related_name="items",
        on_delete=fields.CASCADE,
        description="字典类型",
    )
    dict_data_id: int

    class Meta:
        table = "system_dict_items"
        ordering = ["dict_data_id", "value"]
        indexes = (
            ("status",),
            ("dict_data_id", "value"),
            ("dict_data_id", "status"),
        )

    def __str__(self) -> str:
        return self.label
