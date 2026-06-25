"""
系统菜单 Schema
"""

from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class MenuBase(BaseSchema):
    """菜单基础信息"""

    name: str = Field(description="名称")
    type: str = Field(default="MENU", description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int = Field(default=0, description="排序")
    visible: int = Field(default=1, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] = Field(default=[], description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuCreate(MenuBase):
    """创建菜单请求"""

    pass


class MenuUpdate(BaseSchema):
    """更新菜单请求"""

    name: str | None = Field(default=None, description="名称")
    type: str | None = Field(default=None, description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int | None = Field(default=None, description="排序")
    visible: int | None = Field(default=None, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] | None = Field(default=None, description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuOut(TimestampSchema):
    """菜单响应数据"""

    name: str = Field(description="名称")
    type: str = Field(description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int = Field(default=0, description="排序")
    visible: int = Field(default=1, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] = Field(default=[], description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuTree(MenuOut):
    """菜单树形结构"""

    children: list["MenuTree"] = Field(default=[], description="子菜单")
