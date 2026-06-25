"""OAuth 菜单路由 API。"""

from fastapi import APIRouter, Request

from app.api.deps import CurrentUser
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel

router = APIRouter()

@router.get(
    "/menus/routes/",
    response_model=ResponseModel[list],
    summary="获取用户菜单路由",
    description="""
## 获取当前用户的菜单路由

返回当前用户有权访问的菜单列表，用于前端动态路由生成。

### 请求头
- `Authorization` (必填): Bearer {accessToken}

### 响应数据
返回菜单树形结构，每个菜单项包含：
- `id`: 菜单ID
- `name`: 菜单名称
- `type`: 菜单类型（MENU: 菜单, BUTTON: 按钮, API: 接口）
- `routeName`: 路由名称
- `routePath`: 路由路径
- `component`: 组件路径
- `sort`: 排序
- `visible`: 是否可见
- `icon`: 图标
- `redirect`: 重定向路径
- `perm`: 权限标识
- `keepAlive`: 是否缓存
- `alwaysShow`: 是否一直显示
- `params`: 路由参数
- `children`: 子菜单列表

### 使用说明
1. 前端根据返回的菜单数据动态生成路由
2. 根据 `visible` 字段控制菜单显示
3. 根据 `children` 递归生成子菜单

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
                        "data": [
                            {
                                "id": 1,
                                "name": "系统管理",
                                "type": "MENU",
                                "routeName": "System",
                                "routePath": "/system",
                                "component": "LAYOUT",
                                "sort": 1,
                                "visible": 1,
                                "icon": "setting",
                                "children": [
                                    {
                                        "id": 2,
                                        "name": "用户管理",
                                        "type": "MENU",
                                        "routeName": "User",
                                        "routePath": "user",
                                        "component": "system/user/index",
                                        "sort": 1,
                                        "visible": 1,
                                        "icon": "user",
                                        "children": []
                                    }
                                ]
                            }
                        ]
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
async def get_user_menus(
    request: Request,
    current_user: Users = CurrentUser,
) -> ResponseModel[list]:
    menu_tree = await current_user.get_menus()

    return ResponseModel.success(data=menu_tree)

