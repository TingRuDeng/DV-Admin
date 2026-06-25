"""用户密码 API 路由。"""

from fastapi import APIRouter, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.services.system.user_service import user_service

router = APIRouter()

@router.api_route(
    "/{user_id}/password/reset/",
    methods=["PUT", "POST"],
    response_model=ResponseModel[None],
    summary="重置用户密码",
    description="""
## 重置用户密码

将指定用户的密码重置为系统默认密码。

### 路径参数
- `userId` (必填): 用户ID

### 权限要求
- 需要 `system:users:password:reset` 权限

### 业务规则
1. 重置后的密码来自系统显式配置的 `DEFAULT_PASSWORD`
2. 重置后用户需要使用新密码登录
3. 建议用户登录后立即修改密码

### 安全建议
1. 重置密码后及时通知用户
2. 建议用户首次登录后修改密码
3. 定期清理长期未登录的账号

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `404`: 用户不存在
    """,
    responses={
        200: {
            "description": "重置成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "密码重置成功",
                        "data": None
                    }
                }
            }
        }
    }
)
async def reset_user_password(
    request: Request,
    user_id: int,
    current_user: Users = require_permissions("system:users:password:reset"),
) -> ResponseModel[None]:
    await user_service.reset_password(user_id)
    return ResponseModel.success(message="密码重置成功")
