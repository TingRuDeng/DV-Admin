---
ai_summary:
  purpose: "说明 Django/FastAPI 两套替代后端的核心 API 契约和已知差异。"
  read_when:
    - "新增或修改 API 前"
    - "排查 Django/FastAPI 或前后端契约不一致时"
  source_of_truth:
    - "backend/drf_admin/apps/oauth/urls.py"
    - "backend/drf_admin/apps/oauth/views/oauth.py"
    - "backend/drf_admin/apps/system/views/health.py"
    - "backend/drf_admin/utils/middleware.py"
    - "fastapi/app/api/v1/oauth/auth.py"
    - "fastapi/app/api/health.py"
    - "fastapi/app/schemas/base.py"
    - "frontend/src/api/auth-api.ts"
    - "frontend/src/utils/request.ts"
    - "scripts/api_contracts.py"
    - "scripts/validate_api_contracts.py"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/validate_api_contracts.py ."
    - "git ls-files backend/drf_admin/apps/oauth/urls.py fastapi/app/api/v1/oauth/auth.py frontend/src/api/auth-api.ts"
  stale_when:
    - "接口路径、请求参数或响应包裹字段变化"
    - "认证、刷新 token、分页契约或错误格式变化"
---

# DV-Admin API 端点文档

> 本文档是核心接口概要，不替代代码路由、schema 或序列化器。

## Purpose

提供跨 Django/FastAPI 两套替代后端的核心 API 契约概览。

## Source of truth

- `backend/drf_admin/apps/oauth/urls.py`
- `backend/drf_admin/apps/oauth/views/oauth.py`
- `backend/drf_admin/apps/system/urls.py`
- `backend/drf_admin/utils/middleware.py`
- `fastapi/app/api/v1/oauth/auth.py`
- `fastapi/app/api/v1/system/users.py`
- `fastapi/app/api/health.py`
- `fastapi/app/schemas/base.py`
- `frontend/src/api/auth-api.ts`
- `frontend/src/api/system/user-api.ts`
- `frontend/src/utils/request.ts`

## Key facts

- 两套后端共享 `/api/v1/` 契约前缀，但仍存在局部差异端点。
- 前端成功分支主要依赖 `code/data`，错误分支会读取 `errors`、`msg` 或 `message`。
- 刷新 token、验证码和健康检查端点是契约差异高风险区域。
- 共享响应与分页契约由 `scripts/api_contracts.py`、Django/FastAPI 后端测试和前端契约测试共同锁定。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 scripts/validate_api_contracts.py .`
- full: `pnpm --dir frontend run quality`
- full: `make -C fastapi quality`

## Stale when

- 路由、schema、serializer、请求封装或响应中间件变化。
- 新增接口但未同步本概要。

---

## 文档边界

**本文档覆盖：**
- Django 后端核心 API（`/api/v1/` 前缀）
- FastAPI 后端核心 API（`/api/v1/` 前缀）
- 健康检查端点

**本文档不覆盖：**
- 所有 CRUD 操作的完整细节
- 所有可选查询参数
- 所有错误码

**获取完整 API 文档：**
- Django: 访问 `/api/swagger/` 或 `/api/redoc/`
- FastAPI: 访问 `/api/swagger/` 或 `/api/redoc/`

---

## 后端归属说明

本项目有**两个后端实现**，它们是同一产品后端的**替代关系**：

| 后端 | 技术栈 | 路由前缀 | 状态 |
|------|--------|---------|------|
| Django | Django 4.x + DRF | `/api/v1/` | 可替代实现 |
| FastAPI | FastAPI + Tortoise ORM | `/api/v1/` | 可替代实现 |

**运行约定：**
- 日常开发、联调和部署通常只选择其中一种后端实现
- 本文档同时记录两套实现，是为了说明共享契约与现有差异，而不是要求两套后端同时在线

**关键差异：**
- 部分端点路径不同（见下文详细说明）
- Django 与 FastAPI 均提供根级健康检查端点（`/health`）
- 验证码端点仅存在于 FastAPI

---

## API 基础信息

**基础路径：** `/api/v1/`

**认证方式：** Bearer Token (JWT)

**响应格式：**
```json
{
  "code": 20000,
  "msg": "成功",
  "errors": null,
  "data": { ... }
}
```

**分页响应格式：**
```json
{
  "code": 20000,
  "msg": "成功",
  "errors": null,
  "data": {
    "list": [...],
    "total": 100
  }
}
```

**补充说明：**
- Django 响应中间件统一输出 `{code, msg, errors, data}`（见 `backend/drf_admin/utils/middleware.py`）。
- FastAPI `ResponseModel` 默认输出 `{code, message, data}`（见 `fastapi/app/schemas/base.py`）。
- 前端成功分支仅依赖 `code/data`，错误分支当前优先读取 `errors` 与 `msg`（见 `frontend/src/utils/request.ts`）。

### 共享 API 契约验证

共享契约不是靠字段名已经完全一致来保证，而是靠前端真实依赖的公共语义来约束：

- `scripts/api_contracts.py` 定义成功响应、错误响应和分页载荷的跨后端断言。
- `scripts/api_endpoint_contracts.py` 定义关键端点契约目录，锁定路径、方法、权限、分页和关键字段。
- `backend/drf_admin/utils/test_response_contract.py` 覆盖 Django 响应中间件的成功、错误和幂等包裹。
- `fastapi/tests/test_api_contracts.py` 覆盖 FastAPI `ResponseModel` 与 `PageResult`。
- `frontend/src/utils/__tests__/api-contract.test.ts` 覆盖前端对 Django `msg/errors` 与 FastAPI `message` 的兼容读取。
- `scripts/validate_api_contracts.py` 校验契约定义、测试文件和本文档入口是否同步。

---

## 认证模块 (OAuth)

### 登录

**Django & FastAPI：**
```
POST /api/v1/oauth/login/
```

**请求体：**
```json
{
  "username": "admin",
  "password": "123456",
  "captchaKey": "验证码缓存key（FastAPI 可选）",
  "captchaCode": "验证码（FastAPI 可选）"
}
```

**响应：**
```json
{
  "code": 20000,
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "tokenType": "bearer",
    "expiresIn": 7200,
    "refreshExpiresIn": 604800
  }
}
```

---

### 登出

**Django & FastAPI：**
```
POST /api/v1/oauth/logout/
```

---

### 刷新 Token

**Django & FastAPI：**
```
POST /api/v1/oauth/refresh-token/
```

**请求方式：**
- Django：支持查询参数 `?refreshToken=token`，也兼容请求体 `refreshToken/refresh`。
- FastAPI：当前只接收查询参数 `?refreshToken=token`。

**响应：**
```json
{
  "code": 20000,
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "tokenType": "bearer",
    "expiresIn": 3600
  }
}
```

**注意：** Django 后端已统一使用 `/refresh-token/` 接口，与 FastAPI 保持一致。

---

### 获取用户信息

**Django & FastAPI：**
```
GET /api/v1/oauth/info/
```

---

### 获取用户路由

**Django & FastAPI：**
```
GET /api/v1/oauth/menus/routes/
```

---

### 获取验证码

**⚠️ 仅 FastAPI：**
```
GET /api/v1/oauth/captcha/
```

**Django 后端无此端点。**

**响应：**
```json
{
  "code": 20000,
  "data": {
    "captchaKey": "xxx-xxx-xxx",
    "captchaBase64": "data:image/png;base64,..."
  }
}
```

---

### 首页数据

**⚠️ 仅 Django：**
```
GET /api/v1/oauth/home/
```

**FastAPI 后端无此端点。**

**响应：**
```json
{
  "code": 20000,
  "msg": "成功",
  "errors": null,
  "data": {
    "visits": 100,
    "users": 50
  }
}
```

---

## 系统管理模块 (System)

### 用户管理

#### 用户 CRUD

**Django & FastAPI：**
```
GET    /api/v1/system/users/          # 列表
POST   /api/v1/system/users/          # 创建
GET    /api/v1/system/users/{id}/     # 详情
PUT    /api/v1/system/users/{id}/     # 更新
DELETE /api/v1/system/users/{id}/     # 删除
```

#### 其他用户端点

**Django & FastAPI：**
```
GET  /api/v1/system/users/options/              # 用户下拉选项
PUT  /api/v1/system/users/{id}/password/reset/  # 重置密码
GET  /api/v1/system/users/{id}/permissions/     # 用户权限ID列表
```

> Django 该端点读取请求体中的 `password` 与 `confirm_password`，敏感字段不得放入 URL query。FastAPI 当前额外保留 `POST /api/v1/system/users/{id}/password/reset/` 兼容入口，并按 `DEFAULT_PASSWORD` 重置；共享前端契约以 `PUT` 方法为准。

---

### 角色管理

**Django & FastAPI：**
```
GET    /api/v1/system/roles/          # 列表
POST   /api/v1/system/roles/          # 创建
GET    /api/v1/system/roles/{id}/     # 详情
PUT    /api/v1/system/roles/{id}/     # 更新
DELETE /api/v1/system/roles/{id}/     # 删除
GET    /api/v1/system/roles/options/  # 角色下拉选项
GET    /api/v1/system/roles/{id}/menu-ids/ # 角色菜单ID列表
```

---

### 部门管理

**⚠️ 路径差异：**

| 后端 | 端点路径 |
|------|---------|
| Django | `/api/v1/system/departments/` |
| FastAPI | `/api/v1/system/departments/` |

**CRUD：**
```
GET    /api/v1/system/departments/          # 部门树
POST   /api/v1/system/departments/          # 创建
GET    /api/v1/system/departments/{id}/     # 详情
PUT    /api/v1/system/departments/{id}/     # 更新
DELETE /api/v1/system/departments/{id}/     # 删除
```

---

### 菜单/权限管理

**Django & FastAPI：**
```
GET    /api/v1/system/menus/          # 菜单树
POST   /api/v1/system/menus/          # 创建
GET    /api/v1/system/menus/{id}/     # 详情
PUT    /api/v1/system/menus/{id}/     # 更新
DELETE /api/v1/system/menus/{id}/     # 删除
```

---

### 字典管理

**Django & FastAPI：**
```
GET    /api/v1/system/dicts/          # 字典类型列表
POST   /api/v1/system/dicts/          # 创建字典类型
GET    /api/v1/system/dict-items/     # 字典项列表
POST   /api/v1/system/dict-items/     # 创建字典项
```

---

### 通知公告

**Django & FastAPI：**
```
GET  /api/v1/system/notices/           # 通知列表
POST /api/v1/system/notices/           # 创建通知
GET  /api/v1/system/notices/my-page/   # 我的通知
```

---

### 操作日志

**Django & FastAPI：**
```
GET /api/v1/system/logs/       # 日志列表
GET /api/v1/system/logs/stats/ # 访问统计
```

---

## 个人中心模块 (Information)

**⚠️ 路径差异：**

| 功能 | Django 端点 | FastAPI 端点 |
|------|------------|--------------|
| 获取个人信息 | `GET /api/v1/information/profile/` | `GET /api/v1/information/profile/` |
| 更新个人信息 | `PUT /api/v1/information/change-information/` | `PUT /api/v1/information/profile/` |
| 修改密码 | `PUT /api/v1/information/change-password/` | `PUT /api/v1/information/password/` |
| 上传头像 | `POST /api/v1/information/change-avatar/` | `POST /api/v1/information/change-avatar/` |

---

## 文件管理模块 (Files)

**FastAPI：**
```
POST   /api/v1/files/   # 上传文件，返回 name/url/path
DELETE /api/v1/files/?filePath=files/{user_id}/{filename}   # 删除当前用户文件
```

> 删除接口的 `filePath` 必须使用上传响应 `data.path`，不能传完整 `data.url`。

---

## 健康检查（Django & FastAPI）

```
GET /health        # 基本健康检查
GET /health/ready  # 就绪检查（含数据库、Redis）
GET /health/live   # 存活检查
```

**实现说明：**
- Django：`backend/drf_admin/apps/system/views/health.py`，响应头会携带 `X-Request-ID`。
- FastAPI：`fastapi/app/api/health.py`，响应中包含结构化依赖检查。

---

## API 文档

**Django & FastAPI：**
```
GET /api/swagger/       # Swagger UI
GET /api/redoc/         # ReDoc
```

---

## 权限白名单

以下 API 无需认证即可访问（具体以代码为准）：

- `POST /api/v1/oauth/login/`
- `POST /api/v1/oauth/refresh-token/`
- `GET /api/v1/oauth/captcha/`（仅 FastAPI）
- `GET /api/v1/system/dict-items/`
- `GET /health`
- `GET /health/live`
- `GET /health/ready`

---

## 错误码说明

| 错误码 | 说明 |
|-------|------|
| 20000 | 成功 |
| 40000 | 通用错误 |
| 40001 | Token 无效或过期 |
| 40002 | Refresh Token 无效或过期 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 前端 API 调用注意事项

### 死代码警告

`frontend/src/api/test/` 目录下的文件调用了**不存在的后端接口**：

| 文件 | 调用路径 | 状态 |
|------|---------|------|
| `cases-api.ts` | `/api/test/cases/` | ❌ 后端不存在 |
| `project-api.ts` | `/api/test/projects/` | ❌ 后端不存在 |
| `task.api.js` | `/api/test/tasks/` | ❌ 后端不存在 |
| `device.api.js` | `/api/test/devices/` | ❌ 后端不存在 |

**这些文件是前端示例/测试代码残留，不应在实际开发中使用。**

---

**最后更新：** 2026-05-23
**维护者：** DV-Admin Team

**重要提醒：** 本文档不保证完整性，实际开发请以代码为准。
