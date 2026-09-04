"""
操作日志分页查询路由。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Path, Query, Request

from app.api.deps import require_permissions
from app.api.pagination import PaginationParams, page_params
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import OperationLogOut, OperationLogPageResult
from app.services.system.log_service import log_service

router = APIRouter()


@router.get(
    "/page",
    response_model=ResponseModel[OperationLogPageResult],
    summary="获取操作日志分页列表",
    description="""
## 获取操作日志分页列表

分页查询系统操作日志，支持多条件筛选。

### 请求参数
- `pageNum` (可选): 页码，默认 1，最小值 1
- `pageSize` (可选): 每页数量，默认 10，范围 1-100
- `username` (可选): 用户名，模糊匹配
- `operation` (可选): 操作描述，模糊匹配
- `requestId` (可选): 请求 ID，精确匹配
- `objectType` (可选): 业务对象类型，精确匹配（如 system.users）
- `objectId` (可选): 业务对象 ID，精确匹配
- `method` (可选): 请求方法（GET/POST/PUT/DELETE/PATCH）
- `status` (可选): 状态（1: 成功, 0: 失败）
- `startTime` (可选): 开始时间，ISO 8601 格式
- `endTime` (可选): 结束时间，ISO 8601 格式

### 权限要求
- 需要 `system:logs:query` 权限
    """,
)
async def get_log_page(
    request: Request,
    pagination: PaginationParams = Depends(page_params),
    username: str | None = Query(None, description="用户名"),
    operation: str | None = Query(None, description="操作描述"),
    request_id: str | None = Query(
        None,
        alias="requestId",
        max_length=64,
        description="请求 ID（精确匹配）",
    ),
    object_type: str | None = Query(None, alias="objectType", max_length=100, description="业务对象类型"),
    object_id: str | None = Query(None, alias="objectId", max_length=255, description="业务对象ID"),
    method: str | None = Query(None, description="请求方法"),
    status: int | None = Query(None, description="状态"),
    start_time: datetime | None = Query(None, alias="startTime", description="开始时间"),
    end_time: datetime | None = Query(None, alias="endTime", description="结束时间"),
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_page(
        page=pagination.page,
        page_size=pagination.page_size,
        username=username,
        operation=operation,
        request_id=request_id,
        object_type=object_type,
        object_id=object_id,
        method=method,
        status=status,
        start_time=start_time,
        end_time=end_time,
        current_user=current_user,
    )
    return ResponseModel.success(data=data)


@router.get(
    "/{log_id}",
    response_model=ResponseModel[OperationLogOut],
    summary="获取操作日志详情",
)
async def get_log_detail(
    request: Request,
    log_id: int = Path(..., ge=1, description="日志 ID"),
    current_user: Users = require_permissions("system:logs:query"),
):
    """按当前用户数据范围返回日志详情，敏感字段继续执行原文权限校验。"""
    data = await log_service.get_detail(log_id, current_user=current_user)
    return ResponseModel.success(data=data)
