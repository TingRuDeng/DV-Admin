"""用户写操作 API 路由。"""

from fastapi import APIRouter, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import BulkDelete, UserCreate, UserOut, UserPartialUpdate, UserUpdate
from app.services.system.user_service import user_service

router = APIRouter()

@router.post(
    "/",
    response_model=ResponseModel[UserOut],
    summary="创建用户",
    description="""
## 创建新用户

创建新的系统用户账号。

### 请求参数
- `username` (必填): 用户名，长度 3-50 字符，唯一
- `password` (可选): 密码，长度 6-20 字符，不填则使用显式配置的 `DEFAULT_PASSWORD`
- `name` (可选): 真实姓名
- `email` (可选): 邮箱地址
- `mobile` (可选): 手机号
- `gender` (可选): 性别（0: 未知, 1: 男, 2: 女），默认 0
- `isActive` (可选): 是否激活（1: 是, 0: 否），默认 1
- `deptId` (可选): 部门ID
- `roles` (可选): 角色ID列表
- `avatar` (可选): 头像URL，默认使用默认头像

### 权限要求
- 需要 `system:users:add` 权限

### 业务规则
1. 用户名必须唯一，不能重复
2. 密码如果不填写，将使用系统默认密码
3. 创建时会自动记录创建人信息

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `400`: 用户名已存在
- `422`: 参数验证失败
    """,
    responses={
        200: {
            "description": "创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "创建成功",
                        "data": {
                            "id": 10,
                            "username": "newuser",
                            "name": "新用户",
                            "email": "newuser@example.com",
                            "mobile": "13900139000",
                            "avatar": "avatar/default.png",
                            "gender": 1,
                            "isActive": 1,
                            "deptId": 1,
                            "deptName": "技术部",
                            "roleNames": "普通用户",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        400: {
            "description": "用户名已存在",
            "content": {
                "application/json": {
                    "example": {
                        "code": 400,
                        "message": "用户名已存在",
                        "data": None
                    }
                }
            }
        }
    }
)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: Users = require_permissions("system:users:add"),
) -> ResponseModel[UserOut]:
    user = await user_service.create(user_data)
    return ResponseModel.success(data=user, message="创建成功")
@router.put("/{user_id}/", response_model=ResponseModel[UserOut])
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    current_user: Users = require_permissions("system:users:edit"),
) -> ResponseModel[UserOut]:
    """
    更新用户
    """
    user = await user_service.update(user_id, user_data)
    return ResponseModel.success(data=user, message="更新成功")
@router.patch(
    "/{user_id}/",
    response_model=ResponseModel[UserOut],
    summary="局部更新用户",
    description="""
## 局部更新用户状态

用于快速启用或禁用用户账号。

### 路径参数
- `userId` (必填): 用户ID

### 请求参数
- `isActive` (必填): 是否激活（1: 启用, 0: 禁用）

### 权限要求
- 需要 `system:users:edit` 权限

### 业务规则
1. 禁用用户后，该用户将无法登录系统
2. 已登录的用户禁用后，令牌仍然有效直到过期
3. 不能禁用自己的账号

### 使用场景
- 批量启用/禁用用户
- 快速切换用户状态

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `404`: 用户不存在
- `400`: 不能禁用自己的账号
    """,
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "更新成功",
                        "data": {
                            "id": 2,
                            "username": "testuser",
                            "name": "测试用户",
                            "isActive": 0,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            }
        }
    }
)
async def partial_update_user(
    request: Request,
    user_id: int,
    user_data: UserPartialUpdate,
    current_user: Users = require_permissions("system:users:edit"),
) -> ResponseModel[UserOut]:
    user = await user_service.partial_update(user_id, user_data)
    return ResponseModel.success(data=user, message="更新成功")
@router.delete(
    "/{user_id}/",
    response_model=ResponseModel[None],
    summary="删除用户",
    description="""
## 删除单个用户

删除指定的用户账号。

### 路径参数
- `userId` (必填): 用户ID

### 权限要求
- 需要 `system:users:delete` 权限

### 业务规则
1. 不能删除自己的账号
2. 不能删除超级管理员账号
3. 删除用户会同时删除用户与角色的关联关系
4. 删除操作为物理删除，不可恢复

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `404`: 用户不存在
- `400`: 不能删除自己的账号或超级管理员
    """,
    responses={
        200: {
            "description": "删除成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "删除成功",
                        "data": None
                    }
                }
            }
        },
        400: {
            "description": "不能删除",
            "content": {
                "application/json": {
                    "example": {
                        "code": 400,
                        "message": "不能删除自己的账号",
                        "data": None
                    }
                }
            }
        }
    }
)
async def delete_user(
    request: Request,
    user_id: int,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[None]:
    await user_service.delete(user_id, current_user.id)
    return ResponseModel.success(message="删除成功")
@router.delete(
    "/",
    response_model=ResponseModel[None],
    summary="批量删除用户",
    description="""
## 批量删除用户

一次性删除多个用户账号。

### 请求参数
- `ids` (必填): 用户ID列表，数组格式

### 权限要求
- 需要 `system:users:delete` 权限

### 业务规则
1. 不能删除自己的账号
2. 不能删除超级管理员账号
3. 删除用户会同时删除用户与角色的关联关系
4. 删除操作为物理删除，不可恢复

### 请求示例
```json
{
    "ids": [2, 3, 4]
}
```

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `400`: 不能删除自己的账号或超级管理员
    """,
    responses={
        200: {
            "description": "批量删除成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "批量删除成功",
                        "data": None
                    }
                }
            }
        }
    }
)
async def batch_delete_users(
    request: Request,
    delete_req: BulkDelete,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[None]:
    await user_service.batch_delete(delete_req.ids, current_user.id)
    return ResponseModel.success(message="批量删除成功")
