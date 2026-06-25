"""
系统通用 Schema
"""

from pydantic import Field

from app.schemas.base import BaseSchema


class BulkDelete(BaseSchema):
    """批量删除请求"""

    ids: list[int] = Field(description="ID列表")


class UserImportResult(BaseSchema):
    """用户导入结果"""

    valid_count: int = Field(default=0, description="成功导入数量")
    invalid_count: int = Field(default=0, description="失败数量")
    message_list: list[str] = Field(default=[], description="错误信息列表")
