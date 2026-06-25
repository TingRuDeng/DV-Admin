"""
系统用户 Schema
"""

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """用户基础信息"""

    username: str = Field(description="用户名")
    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")


class UserCreate(UserBase):
    """创建用户请求"""

    password: str | None = Field(default=None, description="密码")
    role_ids: list[int] = Field(default=[], alias="roles", description="角色ID列表")
    avatar: str | None = Field(default="avatar/default.png", description="头像")


class UserUpdate(BaseSchema):
    """更新用户请求"""

    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    gender: int | None = Field(default=None, description="性别")
    is_active: int | None = Field(default=None, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")
    role_ids: list[int] | None = Field(default=None, alias="roles", description="角色ID列表")
    avatar: str | None = Field(default=None, description="头像")


class UserPartialUpdate(BaseSchema):
    """局部更新用户（用于激活/禁用）"""

    is_active: int = Field(description="是否激活")


class UserOut(TimestampSchema):
    """用户响应数据"""

    username: str = Field(description="用户名")
    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    avatar: str = Field(default="avatar/default.png", description="头像")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")
    dept_name: str | None = Field(default=None, description="部门名称")
    role_names: str | None = Field(default=None, description="角色名称")

    @field_validator("role_names", mode="before")
    @classmethod
    def validate_role_names(cls, v):
        """验证角色名称"""
        if isinstance(v, list):
            return ",".join(v)
        return v


class UserFormOut(UserOut):
    """用户表单响应数据（用于编辑回填）"""

    roles: list[int] = Field(default=[], description="角色ID列表")


class UserPageQuery(BaseSchema):
    """用户分页查询"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: str | None = Field(default=None, description="搜索关键词")
    is_active: int | None = Field(default=None, description="状态")
    dept_id: int | None = Field(default=None, description="部门ID")
