"""
系统通知公告 Schema
"""

from datetime import datetime
from typing import List

from pydantic import Field

from app.schemas.base import BaseSchema


class NoticeBase(BaseSchema):
    """通知公告基础信息"""

    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] = Field(default=[], description="目标用户ID列表")


class NoticeCreate(NoticeBase):
    """创建通知公告请求"""

    pass


class NoticeUpdate(BaseSchema):
    """更新通知公告请求"""

    title: str | None = Field(default=None, description="标题")
    content: str | None = Field(default=None, description="内容")
    type: int | None = Field(default=None, description="类型")
    level: str | None = Field(default=None, description="级别")
    target_type: int | None = Field(default=None, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] | None = Field(default=None, description="目标用户ID列表")


class NoticeFormOut(BaseSchema):
    """通知公告表单数据"""

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] = Field(default=[], description="目标用户ID列表")


class NoticePageOut(BaseSchema):
    """通知公告分页数据"""

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str | None = Field(default=None, description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] = Field(default=[], description="目标用户ID列表")
    publisher_id: int | None = Field(default=None, description="发布人ID")
    publisher_name: str = Field(default="", description="发布人名称")
    publish_status: int = Field(default=0, description="发布状态")
    create_time: datetime | None = Field(default=None, description="创建时间")
    update_time: datetime | None = Field(default=None, description="更新时间")
    publish_time: datetime | None = Field(default=None, description="发布时间")
    revoke_time: datetime | None = Field(default=None, description="撤回时间")


class NoticeMyPageOut(NoticePageOut):
    """我的通知分页数据"""

    is_read: int = Field(default=0, description="是否已读(1:是;0:否)")


class NoticeDetailOut(BaseSchema):
    """通知公告详情"""

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    publisher_name: str = Field(default="", description="发布人名称")
    publish_time: datetime | None = Field(default=None, description="发布时间")
    publish_status: int = Field(default=0, description="发布状态")


class NoticeAdminPageResult(BaseSchema):
    """通知公告分页结果（后台列表）"""

    list: List[NoticePageOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")

    @property
    def results(self) -> List[NoticePageOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total


class NoticeMyPageResult(BaseSchema):
    """通知公告分页结果（我的通知）"""

    list: List[NoticeMyPageOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")

    @property
    def results(self) -> List[NoticeMyPageOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total
