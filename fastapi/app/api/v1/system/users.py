# -*- coding: utf-8 -*-
"""
用户管理 API 路由
"""
from typing import List, Optional

from fastapi import APIRouter, File, Query, Request, Depends, UploadFile

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import (
    BulkDelete,
    UserCreate,
    UserOut,
    UserFormOut,
    UserPartialUpdate,
    UserUpdate,
    UserImportResult,
)
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
- `page` (可选): 页码，默认 1，最小值 1
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
- `results`: 用户列表，每个用户包含：
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
                            "results": [
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
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[int] = Query(None, description="状态"),
    dept: Optional[int] = Query(None, description="部门ID"),
    current_user: Users = require_permissions("system:users:query"),
) -> ResponseModel[PageResult[UserOut]]:
    result = await user_service.get_page(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        dept_id=dept,
    )
    return ResponseModel.success(data=result)


@router.get(
    "/options",
    response_model=ResponseModel[List[dict]],
    summary="获取用户下拉选项",
    description="""
## 获取用户下拉选项

获取所有启用状态的用户列表，用于下拉选择框。

### 权限要求
- 需要 `system:users:view` 权限

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
    current_user: Users = require_permissions("system:users:view"),
) -> ResponseModel[List[dict]]:
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
- 需要 `system:users:view` 权限

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
    current_user: Users = require_permissions("system:users:view"),
) -> ResponseModel[UserFormOut]:
    user = await user_service.get_form(user_id)
    return ResponseModel.success(data=user)


@router.post(
    "/",
    response_model=ResponseModel[UserOut],
    summary="创建用户",
    description="""
## 创建新用户

创建新的系统用户账号。

### 请求参数
- `username` (必填): 用户名，长度 3-50 字符，唯一
- `password` (可选): 密码，长度 6-20 字符，不填则使用默认密码
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


@router.post(
    "/{user_id}/password/reset/",
    response_model=ResponseModel[None],
    summary="重置用户密码",
    description="""
## 重置用户密码

将指定用户的密码重置为系统默认密码。

### 路径参数
- `userId` (必填): 用户ID

### 权限要求
- 需要 `system:users:edit` 权限

### 业务规则
1. 重置后的密码为系统默认密码（通常是 `123456`）
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
    current_user: Users = require_permissions("system:users:edit"),
) -> ResponseModel[None]:
    await user_service.reset_password(user_id)
    return ResponseModel.success(message="密码重置成功")


@router.get("/template", response_model=ResponseModel[dict])
async def get_import_template(
    request: Request,
    current_user: Users = require_permissions("system:users:add"),
):
    """
    获取用户导入模板
    """
    return ResponseModel.success(data=await user_service.get_import_template())


@router.post("/export/", response_model=ResponseModel[dict])
async def export_users(
    request: Request,
    current_user: Users = require_permissions("system:users:query"),
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
- 需要 `system:users:add` 权限

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
    dept_id: Optional[int] = Query(None, description="部门ID"),
    file: UploadFile = File(..., description="Excel文件"),
    current_user: Users = require_permissions("system:users:add"),
) -> ResponseModel[UserImportResult]:
    # 验证文件类型
    if not file.filename or not (
        file.filename.endswith(".xlsx") or file.filename.endswith(".xls")
    ):
        return ResponseModel.error(message="文件格式错误，仅支持 .xlsx 或 .xls 格式")

    # 导入用户
    result = await user_service.import_users(file.file, dept_id)

    return ResponseModel.success(data=result, message="导入完成")
