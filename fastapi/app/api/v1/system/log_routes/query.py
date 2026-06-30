"""
操作日志分页查询路由。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import require_permissions
from app.api.pagination import PaginationParams, page_params
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import OperationLogPageResult
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
        method=method,
        status=status,
        start_time=start_time,
        end_time=end_time,
    )
    return ResponseModel.success(data=data)
