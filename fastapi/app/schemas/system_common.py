"""系统通用 Schema。"""

from typing import Any, Literal

from pydantic import Field

from app.schemas.base import BaseSchema


class BulkDelete(BaseSchema):
    """批量删除请求"""

    ids: list[int] = Field(description="ID列表")


class BatchDeleteRequest(BaseSchema):
    """结果化批量删除请求。

    `ids` 保持宽类型，由业务层统一返回 HTTP 400，避免 FastAPI 默认的
    422 与 Django 实现产生差异。
    """

    ids: Any = Field(default=None, description="待删除对象 ID 列表")


class BatchDeleteSuccessItem(BaseSchema):
    """批量删除成功项。"""

    object_id: str = Field(description="对象 ID")
    object_name: str = Field(default="", description="对象名称")


class BatchDeleteFailure(BaseSchema):
    """批量删除失败项。"""

    object_id: str = Field(description="对象 ID")
    object_name: str = Field(default="", description="对象名称")
    error_code: str = Field(description="稳定业务错误码")
    message: str = Field(description="失败原因")
    retryable: bool = Field(default=False, description="是否允许逐条重试")


class BatchDeleteResult(BaseSchema):
    """批量删除逐条处理结果。"""

    status: Literal["succeeded", "partial_failed", "failed"] = Field(
        description="批量处理状态"
    )
    total_count: int = Field(description="去重后的请求总数")
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    processed_count: int = Field(description="已处理数量")
    success_items: list[BatchDeleteSuccessItem] = Field(
        default_factory=list,
        description="成功项",
    )
    failures: list[BatchDeleteFailure] = Field(default_factory=list, description="失败项")


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
