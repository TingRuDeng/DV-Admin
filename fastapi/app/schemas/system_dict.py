"""
系统字典 Schema
"""

from pydantic import AliasChoices, Field

from app.schemas.base import BaseSchema, TimestampSchema


class DictDataBase(BaseSchema):
    """字典类型基础信息"""

    name: str = Field(description="字典名称")
    dict_code: str = Field(
        description="字典编码",
        validation_alias=AliasChoices("dictCode", "code", "dict_code"),
        serialization_alias="dictCode",
    )
    status: int = Field(default=1, description="状态")
    remark: str | None = Field(
        default=None,
        description="描述",
        validation_alias=AliasChoices("remark", "desc"),
        serialization_alias="remark",
    )


class DictDataCreate(DictDataBase):
    """创建字典类型请求"""

    pass


class DictDataUpdate(BaseSchema):
    """更新字典类型请求"""

    name: str | None = Field(default=None, description="字典名称")
    dict_code: str | None = Field(
        default=None,
        description="字典编码",
        validation_alias=AliasChoices("dictCode", "code", "dict_code"),
        serialization_alias="dictCode",
    )
    status: int | None = Field(default=None, description="状态")
    remark: str | None = Field(
        default=None,
        description="描述",
        validation_alias=AliasChoices("remark", "desc"),
        serialization_alias="remark",
    )


class DictDataOut(TimestampSchema):
    """字典类型响应数据"""

    name: str = Field(description="字典名称")
    dict_code: str = Field(description="字典编码", serialization_alias="dictCode")
    status: int = Field(default=1, description="状态")
    remark: str | None = Field(default=None, description="描述", serialization_alias="remark")


class DictItemBase(BaseSchema):
    """字典项基础信息"""

    label: str = Field(max_length=32, description="标签")
    value: str = Field(max_length=32, description="值")
    status: int = Field(default=1, description="状态")
    tag_type: str | None = Field(
        default=None,
        description="标签类型",
        validation_alias=AliasChoices("tagType", "tag_type"),
        serialization_alias="tagType",
    )


class DictItemCreate(DictItemBase):
    """创建字典项请求"""

    dict_data_id: int = Field(
        description="字典类型ID",
        validation_alias=AliasChoices("dict", "dictDataId", "dict_data_id"),
        serialization_alias="dict",
    )


class DictItemUpdate(BaseSchema):
    """更新字典项请求"""

    label: str | None = Field(default=None, max_length=32, description="标签")
    value: str | None = Field(default=None, max_length=32, description="值")
    status: int | None = Field(default=None, description="状态")
    tag_type: str | None = Field(
        default=None,
        description="标签类型",
        validation_alias=AliasChoices("tagType", "tag_type"),
        serialization_alias="tagType",
    )


class DictItemOut(TimestampSchema):
    """字典项响应数据"""

    label: str = Field(description="标签")
    value: str = Field(description="值")
    status: int = Field(default=1, description="状态")
    tag_type: str | None = Field(default=None, description="标签类型", serialization_alias="tagType")
    dict_data_id: int = Field(description="字典类型ID", serialization_alias="dict")
    dict_name: str | None = Field(default=None, description="字典类型名称", serialization_alias="dictName")


class DictWithItems(DictDataOut):
    """带字典项的字典类型"""

    items: list[DictItemOut] = Field(default=[], description="字典项列表")
