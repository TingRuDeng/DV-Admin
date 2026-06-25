"""
操作日志统计路由。
"""
from datetime import datetime

from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import VisitStatsOut, VisitTrendOut
from app.services.system.log_service import log_service

router = APIRouter()


@router.get(
    "/visit-trend",
    response_model=ResponseModel[list[VisitTrendOut]],
    summary="获取访问趋势统计",
    description="""
## 获取访问趋势统计

获取指定日期范围内的每日访问次数统计，用于绘制趋势图表。

### 权限要求
- 需要 `system:logs:query` 权限
    """,
)
async def get_visit_trend(
    request: Request,
    start_date: datetime | None = Query(None, description="开始日期"),
    end_date: datetime | None = Query(None, description="结束日期"),
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_visit_trend(
        start_date=start_date,
        end_date=end_date,
    )
    return ResponseModel.success(data=data)


@router.get(
    "/visit-stats",
    response_model=ResponseModel[VisitStatsOut],
    summary="获取访问统计",
    description="""
## 获取访问统计数据

获取系统访问的综合统计数据，用于首页数据展示。

### 权限要求
- 需要 `system:logs:query` 权限
    """,
)
async def get_visit_stats(
    request: Request,
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_visit_stats()
    return ResponseModel.success(data=data)
