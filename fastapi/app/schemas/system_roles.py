"""
角色管理专用 Schema。
"""

from pydantic import Field

from app.schemas.base import BaseSchema


class RoleMenuAssign(BaseSchema):
    """角色权限分配请求。"""

    menu_ids: list[int] = Field(default=[], description="菜单权限ID列表")
