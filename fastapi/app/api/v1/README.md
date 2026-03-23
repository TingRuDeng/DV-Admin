# FastAPI API v1 模块

> 本模块包含 FastAPI 后端的所有 v1 版本 API 端点。

---

## 模块概述

**位置：** `fastapi/app/api/v1/`

**特点：**
- 异步架构
- 自动 API 文档
- 与 Django 后端 API 兼容

---

## 目录结构

```
v1/
├── __init__.py       # 路由注册
├── oauth/            # 认证模块
│   ├── __init__.py
│   └── auth.py       # 登录/登出/刷新Token
├── system/           # 系统管理模块
│   ├── __init__.py
│   ├── users.py      # 用户管理
│   ├── roles.py      # 角色管理
│   ├── menus.py      # 菜单/权限管理
│   ├── depts.py      # 部门管理
│   ├── dicts.py      # 字典类型管理
│   ├── dict_items.py # 字典项管理
│   ├── notices.py    # 通知公告
│   └── logs.py       # 操作日志
├── information/      # 个人中心模块
│   ├── __init__.py
│   └── profile.py    # 个人信息管理
└── files/            # 文件管理模块
    ├── __init__.py
    └── upload.py     # 文件上传
```

---

## 路由注册

在 `__init__.py` 中统一注册：

```python
from fastapi import APIRouter
from app.api.v1 import oauth, system, information, files

router = APIRouter(prefix="/api/v1")

router.include_router(oauth.router)
router.include_router(system.router)
router.include_router(information.router)
router.include_router(files.router)
```

---

## 端点规范

### 响应格式

统一使用 `{code, message, data}` 格式：

```python
from app.schemas.base import ResponseModel

@router.get("/users/", response_model=ResponseModel[UserListResponse])
async def get_users(...):
    return {
        "code": 200,
        "message": "success",
        "data": {...}
    }
```

### 分页格式

```python
from app.schemas.base import PaginatedResponse

@router.get("/users/", response_model=PaginatedResponse[User])
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    ...
```

### 认证依赖

```python
from app.api.deps import get_current_user

@router.get("/profile/")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

### 权限检查

```python
from app.api.deps import check_permission

@router.post("/users/", dependencies=[Depends(check_permission("system:user:add"))])
async def create_user(...):
    ...
```

---

## 模块说明

### OAuth 模块

**端点：**
- `POST /api/v1/oauth/login/` - 登录
- `POST /api/v1/oauth/logout/` - 登出
- `POST /api/v1/oauth/refresh/` - 刷新 Token
- `GET /api/v1/oauth/info/` - 获取用户信息
- `GET /api/v1/oauth/menus/routes/` - 获取用户路由
- `GET /api/v1/oauth/captcha/` - 获取验证码

### System 模块

**端点：**
- `/api/v1/system/users/` - 用户管理
- `/api/v1/system/roles/` - 角色管理
- `/api/v1/system/menus/` - 菜单管理
- `/api/v1/system/depts/` - 部门管理
- `/api/v1/system/dicts/` - 字典类型管理
- `/api/v1/system/dict-items/` - 字典项管理
- `/api/v1/system/notices/` - 通知公告
- `/api/v1/system/logs/` - 操作日志

### Information 模块

**端点：**
- `GET /api/v1/information/profile/` - 获取个人信息
- `PUT /api/v1/information/profile/` - 更新个人信息
- `PUT /api/v1/information/password/` - 修改密码
- `POST /api/v1/information/avatar/` - 上传头像

### Files 模块

**端点：**
- `POST /api/v1/files/upload/` - 上传文件
- `DELETE /api/v1/files/upload/` - 删除文件

---

## 修改指南

### 新增 API 端点

1. 在对应模块目录创建或修改文件
2. 定义 Schema（在 `app/schemas/`）
3. 实现 Service（在 `app/services/`）
4. 创建端点函数
5. 在模块 `__init__.py` 注册路由
6. 更新 `docs/API_ENDPOINTS.md`

### 新增模块

1. 在 `v1/` 下创建新目录
2. 创建 `__init__.py` 和路由文件
3. 在 `v1/__init__.py` 中注册
4. 更新本文档

---

## 与 Django API 兼容性

### 必须保持一致

- URL 路径
- 请求参数名称
- 响应格式
- 错误码

### 差异说明

| 项目 | Django | FastAPI |
|------|--------|---------|
| 认证 | simplejwt | python-jose |
| ORM | Django ORM | Tortoise ORM |
| 验证 | DRF Serializer | Pydantic |

---

## 测试

```bash
# 运行所有 API 测试
cd fastapi
uv run pytest tests/ -v

# 运行特定模块测试
uv run pytest tests/test_users.py -v
uv run pytest tests/test_oauth.py -v
```

---

## 常见陷阱

### 陷阱 1：忘记添加认证依赖

**错误：**
```python
@router.get("/profile/")
async def get_profile():  # 无认证
    ...
```

**正确：**
```python
@router.get("/profile/")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    ...
```

### 陷阱 2：响应格式不一致

**错误：**
```python
return {"users": users}  # 缺少 code, message
```

**正确：**
```python
return {"code": 200, "message": "success", "data": {"users": users}}
```

### 陷阱 3：命名格式错误

**注意：** FastAPI 端直接返回数据，前端期望 camelCase

**解决方案：** 使用 Pydantic 模型的 `alias` 功能

---

**最后更新：** 2026-03-23
