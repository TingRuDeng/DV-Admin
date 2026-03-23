"""
基础 Schema 模块

定义所有 Pydantic 模型的基类和通用模型。
"""

from datetime import datetime
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    基础 Schema 类

    所有 Pydantic 模型的基类。
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
        str_strip_whitespace=True,
    )


class ResponseModel(BaseSchema, Generic[T]):
    """
    统一响应模型

    所有 API 响应的统一格式。
    """

    code: int = Field(default=20000, description="状态码")
    message: str = Field(default="success", description="消息")
    data: T | None = Field(default=None, description="数据")

    @classmethod
    def success(cls, data: T | None = None, message: str = "success") -> "ResponseModel[T]":
        """成功响应"""
        return cls(code=20000, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "error") -> "ResponseModel[T]":
        """错误响应"""
        return cls(code=code, message=message, data=None)


class PageQuery(BaseSchema):
    """
    分页查询参数

    分页查询的基础参数。
    """

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: str | None = Field(default=None, description="搜索关键词")
    ordering: str | None = Field(default=None, description="排序字段")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size


class PageResult(BaseSchema, Generic[T]):
    """
    分页结果

    分页查询的返回结果。
    """

    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")
    list: List[T] = Field(description="数据列表")

    @property
    def results(self) -> List[T]:
        """Backward-compatible accessor for legacy internal callers."""
        return self.list

    @property
    def count(self) -> int:
        """Backward-compatible accessor for legacy internal callers."""
        return self.total

    @classmethod
    def create(
        cls,
        total: int,
        page: int,
        page_size: int,
        results: List[T],
    ) -> "PageResult[T]":
        """
        创建分页结果

        Args:
            total: 总记录数
            page: 当前页码
            page_size: 每页数量
            results: 数据列表

        Returns:
            分页结果对象
        """
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            list=results,
        )


class TimestampSchema(BaseSchema):
    """
    时间戳 Schema

    包含创建时间和更新时间的 Schema 基类。
    """

    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
