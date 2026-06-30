"""
系统角色 Schema
"""

from pydantic import Field

from app.schemas.base import BaseSchema, SharedTimestampSchema


class RoleBase(BaseSchema):
    """角色基础信息"""

    name: str = Field(description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    is_default: int = Field(default=0, description="是否默认")
    desc: str | None = Field(default=None, description="描述")


class RoleCreate(RoleBase):
    """创建角色请求"""

    permission_ids: list[int] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseSchema):
    """更新角色请求"""

    name: str | None = Field(default=None, description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int | None = Field(default=None, description="状态")
    sort: int | None = Field(default=None, description="排序")
    is_default: int | None = Field(default=None, description="是否默认")
    desc: str | None = Field(default=None, description="描述")
    permission_ids: list[int] | None = Field(default=None, description="权限ID列表")


class RoleOut(SharedTimestampSchema):
    """角色响应数据"""

    name: str = Field(description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    is_default: int = Field(default=0, description="是否默认")
    desc: str | None = Field(default=None, description="描述")
    permissions: list[int] = Field(default=[], description="权限ID列表")


class RoleWithPermissions(RoleOut):
    """带权限的角色数据"""

    permissions: list[int] = Field(default=[], description="权限ID列表")
