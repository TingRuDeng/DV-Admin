"""用户导入导出 API 路由。"""

from fastapi import APIRouter, File, Query, Request, UploadFile

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import UserImportResult
from app.services.system.user_service import user_service

router = APIRouter()

@router.get("/template", response_model=ResponseModel[dict])
async def get_import_template(
    request: Request,
    current_user: Users = require_permissions("system:users:import"),
):
    """
    获取用户导入模板
    """
    return ResponseModel.success(data=await user_service.get_import_template())
@router.post("/export/", response_model=ResponseModel[dict])
async def export_users(
    request: Request,
    current_user: Users = require_permissions("system:users:export"),
):
    """
    导出用户
    """
    return ResponseModel.success(data=await user_service.export_users())
@router.post(
    "/import",
    response_model=ResponseModel[UserImportResult],
    summary="导入用户数据",
    description="""
## 批量导入用户

通过 Excel 文件批量导入用户数据。

### 请求参数
- `deptId` (可选): 默认部门ID，未指定部门的用户将分配到此部门
- `file` (必填): Excel 文件，支持 `.xlsx` 或 `.xls` 格式

### 权限要求
- 需要 `system:users:import` 权限

### 文件格式要求
Excel 文件必须包含以下列：
- 用户名（必填，唯一）
- 真实姓名（可选）
- 邮箱（可选）
- 手机号（可选）
- 性别（可选，男/女/未知）
- 部门名称（可选，需与系统中的部门名称一致）
- 角色名称（可选，需与系统中的角色名称一致）

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
                        "message": "文件格式错误，仅支持 .xlsx 或 .xls 格式",
                        "data": None
                    }
                }
            }
        }
    }
)
async def import_users(
    request: Request,
    dept_id: int | None = Query(None, description="部门ID"),
    file: UploadFile = File(..., description="Excel文件"),
    current_user: Users = require_permissions("system:users:import"),
) -> ResponseModel[UserImportResult]:
    # 验证文件类型
    if not file.filename or not (
        file.filename.endswith(".xlsx") or file.filename.endswith(".xls")
    ):
        return ResponseModel.error(message="文件格式错误，仅支持 .xlsx 或 .xls 格式")

    # 导入用户
    result = await user_service.import_users(file.file, dept_id)

    return ResponseModel.success(data=result, message="导入完成")
