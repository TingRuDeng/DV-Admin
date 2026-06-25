"""OAuth 当前用户信息 API 路由。"""

from fastapi import APIRouter, Request

from app.api.deps import CurrentUser
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.oauth import UserInfo

router = APIRouter()

@router.get(
    "/info/",
    response_model=ResponseModel[UserInfo],
    summary="获取当前用户信息",
    description="""
## 获取当前登录用户信息

返回当前登录用户的详细信息，包括基本信息、部门、角色、权限等。

### 请求头
- `Authorization` (必填): Bearer {accessToken}

### 响应数据
- `id`: 用户ID
- `username`: 用户名
- `name`: 真实姓名
- `email`: 邮箱
- `mobile`: 手机号
- `avatar`: 头像URL
- `gender`: 性别（0: 未知, 1: 男, 2: 女）
- `isActive`: 是否激活（1: 是, 0: 否）
- `deptId`: 部门ID
- `deptName`: 部门名称
- `roleNames`: 角色名称列表（逗号分隔）
- `roles`: 角色列表（JSON字符串）
- `perms`: 权限标识列表
- `createdAt`: 创建时间
- `updatedAt`: 更新时间

### 使用说明
1. 前端在用户登录后调用此接口获取用户信息
2. 用于显示用户头像、名称等信息
3. 用于前端权限控制（根据 `perms` 字段）

### 错误码
- `401`: 未授权，令牌无效或已过期
    """,
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "id": 1,
                            "username": "admin",
                            "name": "管理员",
                            "email": "admin@example.com",
                            "mobile": "13800138000",
                            "avatar": "/media/avatar/admin.png",
                            "gender": 1,
                            "isActive": 1,
                            "deptId": 1,
                            "deptName": "技术部",
                            "roleNames": "管理员、超级管理员",
                            "roles": "[\"管理员\", \"超级管理员\"]",
                            "perms": ["system:users:query", "system:users:add", "system:users:edit"],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        401: {
            "description": "未授权",
            "content": {
                "application/json": {
                    "example": {
                        "code": 401,
                        "message": "未授权访问",
                        "data": None
                    }
                }
            }
        }
    }
)
async def get_current_user_info(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[UserInfo]:
    # 获取部门名称
    dept_name = None
    if current_user.dept_id:
        from app.db.models.system import Departments

        dept = await Departments.get_or_none(id=current_user.dept_id)
        if dept:
            dept_name = dept.name

    # 获取角色名称
    await current_user.fetch_related("roles")
    role_names = "、".join([role.name for role in current_user.roles])

    # 构造 roles (JSON字符串)
    import json
    roles_json = json.dumps([role.name for role in current_user.roles])

    # 获取权限
    permissions = await current_user.get_permissions()

    # 处理头像 URL
    avatar = current_user.avatar
    if avatar and not avatar.startswith(("http", "/media")):
        avatar = f"/media/{avatar}"

    user_info = UserInfo(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email if current_user.email else "",
        mobile=current_user.mobile if current_user.mobile else "",
        avatar=avatar,
        gender=current_user.gender,
        is_active=current_user.is_active,
        dept_id=current_user.dept_id,
        dept_name=dept_name if dept_name else "",
        role_names=role_names,
        roles=roles_json,
        perms=permissions,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

    return ResponseModel.success(data=user_info)

