"""
系统部门 Schema
"""

from pydantic import Field

from app.schemas.base import BaseSchema, SharedTimestampSchema


class DeptBase(BaseSchema):
    """部门基础信息"""

    name: str = Field(description="部门名称")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptCreate(DeptBase):
    """创建部门请求"""

    pass


class DeptUpdate(BaseSchema):
    """更新部门请求"""

    name: str | None = Field(default=None, description="部门名称")
    status: int | None = Field(default=None, description="状态")
    sort: int | None = Field(default=None, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptOut(SharedTimestampSchema):
    """部门响应数据"""

    name: str = Field(description="部门名称")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptTree(DeptOut):
    """部门树形结构"""

    label: str | None = Field(default=None, description="部门名称(兼容前端)")
    children: list["DeptTree"] = Field(default=[], description="子部门")
