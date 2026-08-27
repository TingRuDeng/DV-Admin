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
    message_list: list[str] = Field(default_factory=list, description="错误信息列表")


class EncodedFile(BaseSchema):
    """Base64 编码的下载文件。"""

    filename: str = Field(description="下载文件名")
    content: str = Field(description="Base64 编码文件内容")
    content_type: str = Field(description="文件 MIME 类型")
