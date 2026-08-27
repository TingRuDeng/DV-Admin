"""用户导入导出 API 路由。"""

from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, cast

from fastapi import APIRouter, File, Query, Request, UploadFile

from app.api.deps import require_permissions
from app.core.config import settings
from app.core.exceptions import ValidationError
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import EncodedFile, UserImportResult
from app.services.system.user_service import user_service
from app.utils.file import copy_upload_file

router = APIRouter()
IMPORT_SPOOL_MEMORY_SIZE = 1024 * 1024

@router.get("/template", response_model=ResponseModel[EncodedFile])
async def get_import_template(
    request: Request,
    current_user: Users = require_permissions("system:users:import"),
):
    """
    获取用户导入模板
    """
    return ResponseModel.success(data=await user_service.get_import_template())
@router.post("/export/", response_model=ResponseModel[EncodedFile])
async def export_users(
    request: Request,
    current_user: Users = require_permissions("system:users:export"),
):
    """
    导出用户
    """
    return ResponseModel.success(
        data=await user_service.export_users(current_user=current_user)
    )
@router.post(
    "/import",
    response_model=ResponseModel[UserImportResult],
    summary="导入用户数据",
    description="""
## 批量导入用户

通过 Excel 文件批量导入用户数据。

### 请求参数
- `deptId` (可选): 默认部门ID，未指定部门的用户将分配到此部门
- `file` (必填): Excel 文件，仅支持 `.xlsx` 格式

### 权限要求
- 需要 `system:users:import` 权限

### 文件格式要求
Excel 文件必须包含以下列：
- 用户名*（必填，唯一）
- 姓名（可选）
- 邮箱（可选）
- 手机号（可选）
- 性别（可选，0/1/2）
- 部门ID（可选，不存在时使用默认部门）
- 角色ID(多个用逗号分隔)（可选，必须全部存在且启用）

### 响应数据
返回导入结果：
- `validCount`: 成功导入数量
- `invalidCount`: 失败数量
- `messageList`: 错误信息列表

### 业务规则
1. 用户名重复的记录将跳过
2. 部门或角色不匹配的记录将跳过
3. 格式错误的记录将跳过
4. 导入的用户默认密码为系统默认密码

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `400`: 文件格式错误
    """,
    responses={
        200: {
            "description": "导入完成",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "导入完成",
                        "data": {
                            "validCount": 95,
                            "invalidCount": 5,
                            "messageList": [
                                "第3行：用户名 'test' 已存在",
                                "第5行：部门 '测试部' 不存在",
                                "第8行：邮箱格式错误",
                                "第12行：手机号格式错误",
                                "第15行：角色 '测试角色' 不存在"
                            ]
                        }
                    }
                }
            }
        },
        400: {
            "description": "文件格式错误",
            "content": {
                "application/json": {
                    "example": {
                        "code": 400,
                        "message": "文件格式错误，仅支持 .xlsx 格式",
                        "data": None
                    }
                }
            }
        }
    }
)
async def import_users(
    request: Request,
    dept_id: int | None = Query(None, alias="deptId", description="部门ID"),
    legacy_dept_id: int | None = Query(
        None,
        alias="dept_id",
        include_in_schema=False,
    ),
    file: UploadFile = File(..., description="Excel文件"),
    current_user: Users = require_permissions("system:users:import"),
) -> ResponseModel[UserImportResult]:
    # 验证文件类型
    if not file.filename or Path(file.filename).suffix.lower() != ".xlsx":
        raise ValidationError("文件格式错误，仅支持 .xlsx 格式")

    # 分块复制到有界临时文件；大于内存阈值后自动落盘，避免整份工作簿驻留内存。
    with SpooledTemporaryFile(max_size=IMPORT_SPOOL_MEMORY_SIZE, mode="w+b") as raw_buffer:
        buffer = cast(BinaryIO, raw_buffer)
        await copy_upload_file(file, buffer, max_size=settings.max_upload_size)
        result = await user_service.import_users(
            buffer,
            dept_id if dept_id is not None else legacy_dept_id,
            current_user=current_user,
        )

    return ResponseModel.success(data=result, message="导入完成")
