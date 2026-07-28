"""
操作日志写操作路由。
"""
from fastapi import APIRouter, Path, Request

from app.api.deps import require_permissions
from app.core.exceptions import ValidationError
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.services.system.log_service import log_service

router = APIRouter()


@router.delete("/{ids}", response_model=ResponseModel[None])
async def delete_logs(
    request: Request,
    ids: str,
    current_user: Users = require_permissions("system:logs:delete"),
):
    """批量删除操作日志。"""
    try:
        id_list = [int(value) for item in ids.split(",") if (value := item.strip())]
    except ValueError as exc:
        raise ValidationError("日志 ID 必须是正整数列表") from exc
    if not id_list or any(log_id < 1 for log_id in id_list):
        raise ValidationError("日志 ID 必须是正整数列表")
    deleted_count = await log_service.delete_by_ids(
        id_list,
        current_user=current_user,
    )
    return ResponseModel.success(message=f"成功删除 {deleted_count} 条日志")


@router.delete(
    "/clear/{days}",
    response_model=ResponseModel[None],
    summary="清理历史日志",
    description="""
## 清理指定天数之前的日志

批量删除指定天数之前的历史日志，用于定期维护。

### 权限要求
- 需要 `system:logs:delete` 权限
    """,
)
async def clear_old_logs(
    request: Request,
    days: int = Path(..., ge=1, description="保留天数"),
    current_user: Users = require_permissions("system:logs:delete"),
):
    deleted_count = await log_service.clear_old_logs(
        days=days,
        current_user=current_user,
    )
    return ResponseModel.success(message=f"成功清理 {deleted_count} 条历史日志")
