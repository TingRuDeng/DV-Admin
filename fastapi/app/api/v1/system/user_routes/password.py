"""用户密码 API 路由。"""

from fastapi import APIRouter, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system_user import UserPasswordReset
from app.services.system.user_service import user_service
from app.utils.audit import set_audit_object

router = APIRouter()


@router.put(
    "/{user_id}/password/reset/",
    response_model=ResponseModel[None],
    summary="重置用户密码",
    description="""
## 重置用户密码

使用请求体中的新密码重置指定用户的密码。

### 路径参数
- `userId` (必填): 用户ID

### 请求体
- `password` (必填): 新密码
- `confirmPassword` (必填): 确认新密码

### 权限要求
- 需要 `system:users:password:reset` 权限

### 业务规则
1. 两次密码必须一致，且密码至少 6 位并同时包含字母和数字
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
                    "example": {"code": 20000, "message": "密码重置成功", "data": None}
                }
            },
        }
    },
)
async def reset_user_password(
    request: Request,
    user_id: int,
    password_in: UserPasswordReset,
    current_user: Users = require_permissions("system:users:password:reset"),
) -> ResponseModel[None]:
    set_audit_object(request, "system.users", user_id, changed_fields=["password"])
    await user_service.reset_password(
        user_id,
        current_user=current_user,
        password=password_in.password,
    )
    return ResponseModel.success(message="密码重置成功")


@router.post(
    "/{user_id}/password/reset/",
    response_model=ResponseModel[None],
    summary="按默认密码重置用户密码（兼容入口）",
    deprecated=True,
)
async def reset_user_password_to_default(
    request: Request,
    user_id: int,
    current_user: Users = require_permissions("system:users:password:reset"),
) -> ResponseModel[None]:
    """兼容旧客户端；共享前端契约使用 PUT 并显式提供新密码。"""
    set_audit_object(request, "system.users", user_id, changed_fields=["password"])
    await user_service.reset_password(user_id, current_user=current_user)
    return ResponseModel.success(message="密码重置成功")
