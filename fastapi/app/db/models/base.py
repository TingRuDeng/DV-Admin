"""
基础模型模块

定义所有模型的基类，包含通用字段和方法。
"""

from datetime import datetime
from typing import Any

from tortoise import Model, fields


class BaseModel(Model):
    """
    基础模型类

    所有模型的基类，包含通用的创建时间和更新时间字段。
    """

    id = fields.IntField(pk=True, description="主键ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True

    def to_dict(self, *args: str, exclude: list = None) -> dict[str, Any]:
        """
        将模型转换为字典

        Args:
            *args: 要包含的字段名
            exclude: 要排除的字段名

        Returns:
            模型数据的字典表示
        """
        exclude = exclude or []
        data = {}

        if args:
            # 只包含指定的字段
            for field_name in args:
                if hasattr(self, field_name) and field_name not in exclude:
                    value = getattr(self, field_name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    data[field_name] = value
        else:
            # 包含所有字段
            for field_name in self._meta.fields:
                if field_name not in exclude:
                    value = getattr(self, field_name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    data[field_name] = value

        return data

    class PydanticMeta:
        exclude = ["password", "password_hash"]
