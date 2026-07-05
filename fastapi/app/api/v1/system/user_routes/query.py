"""用户查询 API 路由。"""

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import require_permissions
from app.api.pagination import PaginationParams, page_params
from app.db.models.oauth import Users
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import UserFormOut, UserOut
from app.services.system.user_service import user_service

router = APIRouter()

@router.get(
    "/",
    response_model=ResponseModel[PageResult[UserOut]],
    summary="获取用户分页列表",
    description="""
## 获取用户分页列表

分页查询用户列表，支持多条件筛选和搜索。

### 请求参数
- `pageNum` (可选): 页码，默认 1，最小值 1
- `pageSize` (可选): 每页数量，默认 10，范围 1-100
- `search` (可选): 搜索关键词，匹配用户名、姓名、邮箱、手机号
- `isActive` (可选): 状态筛选，1: 启用, 0: 禁用
- `dept` (可选): 部门ID筛选

### 权限要求
- 需要 `system:users:query` 权限

### 响应数据
返回分页结果：
- `total`: 总记录数
- `page`: 当前页码
- `pageSize`: 每页数量
- `totalPages`: 总页数
- `list`: 用户列表，每个用户包含：
  - `id`: 用户ID
  - `username`: 用户名
  - `name`: 真实姓名
  - `email`: 邮箱
  - `mobile`: 手机号
  - `avatar`: 头像URL
  - `gender`: 性别
  - `isActive`: 是否激活
  - `deptId`: 部门ID
  - `deptName`: 部门名称
  - `roleNames`: 角色名称
  - `createdAt`: 创建时间
  - `updatedAt`: 更新时间

### 错误码
- `401`: 未授权
- `403`: 权限不足
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "total": 100,
                            "page": 1,
                            "pageSize": 10,
                            "totalPages": 10,
                            "list": [
                                {
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
                                    "roleNames": "管理员",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "updatedAt": "2024-01-01T00:00:00Z"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def get_users(
    request: Request,
    pagination: PaginationParams = Depends(page_params),
    search: str | None = Query(None, description="搜索关键词"),
    is_active: int | None = Query(None, description="状态"),
    dept: int | None = Query(None, description="部门ID"),
    current_user: Users = require_permissions("system:users:query"),
) -> ResponseModel[PageResult[UserOut]]:
    result = await user_service.get_page(
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
        is_active=is_active,
        dept_id=dept,
        current_user=current_user,
    )
    return ResponseModel.success(data=result)
@router.get(
    "/options",
    response_model=ResponseModel[list[dict]],
    summary="获取用户下拉选项",
    description="""
## 获取用户下拉选项

获取所有启用状态的用户列表，用于下拉选择框。

### 权限要求
- 需要 `system:users:query` 权限

### 响应数据
返回用户选项列表，每个选项包含：
- `value`: 用户ID
- `label`: 用户名称（格式：用户名(姓名)）

### 使用场景
- 分配任务时选择用户
- 设置审批人时选择用户
- 其他需要选择用户的场景

### 错误码
- `401`: 未授权
- `403`: 权限不足
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": [
                            {"value": 1, "label": "admin(管理员)"},
                            {"value": 2, "label": "zhangsan(张三)"}
                        ]
                    }
                }
            }
        }
    }
)
async def get_user_options(
    request: Request,
    current_user: Users = require_permissions("system:users:query"),
) -> ResponseModel[list[dict]]:
    options = await user_service.get_options()
    return ResponseModel.success(data=options)
@router.get(
    "/{user_id}/",
    response_model=ResponseModel[UserFormOut],
    summary="获取用户详情",
    description="""
## 获取用户详情

根据用户ID获取用户的详细信息，用于编辑表单回填。

### 路径参数
- `userId` (必填): 用户ID

### 权限要求
- 需要 `system:users:query` 权限

### 响应数据
返回用户详细信息：
- `id`: 用户ID
- `username`: 用户名
- `name`: 真实姓名
- `email`: 邮箱
- `mobile`: 手机号
- `avatar`: 头像URL
- `gender`: 性别（0: 未知, 1: 男, 2: 女）
- `isActive`: 是否激活
- `deptId`: 部门ID
- `deptName`: 部门名称
- `roleNames`: 角色名称
- `roles`: 角色ID列表（用于编辑表单回填）
- `createdAt`: 创建时间
- `updatedAt`: 更新时间

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `404`: 用户不存在
    """,
    responses={
        200: {
            "description": "查询成功",
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
                            "roleNames": "管理员",
                            "roles": [1, 2],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        404: {
            "description": "用户不存在",
            "content": {
                "application/json": {
                    "example": {
                        "code": 404,
                        "message": "用户不存在",
                        "data": None
                    }
                }
            }
        }
    }
)
async def get_user(
    request: Request,
    user_id: int,
    current_user: Users = require_permissions("system:users:query"),
) -> ResponseModel[UserFormOut]:
    user = await user_service.get_form(user_id)
    return ResponseModel.success(data=user)
