---
ai_summary:
  purpose: "说明 Django/FastAPI 两套替代后端的核心 API 契约和已知差异。"
  read_when:
    - "新增或修改 API 前"
    - "排查 Django/FastAPI 或前后端契约不一致时"
  source_of_truth:
    - "backend/drf_admin/apps/oauth/urls.py"
    - "backend/drf_admin/apps/oauth/views/oauth.py"
    - "backend/drf_admin/apps/system/urls.py"
    - "backend/drf_admin/apps/system/views/health.py"
    - "backend/drf_admin/apps/system/views/logs.py"
    - "backend/drf_admin/utils/middleware.py"
    - "fastapi/app/api/v1/oauth/auth.py"
    - "fastapi/app/api/v1/oauth/routes/login.py"
    - "fastapi/app/api/v1/oauth/routes/session.py"
    - "fastapi/app/api/v1/oauth/routes/profile.py"
    - "fastapi/app/api/v1/oauth/routes/menus.py"
    - "fastapi/app/api/v1/oauth/routes/captcha.py"
    - "fastapi/app/api/v1/system/__init__.py"
    - "fastapi/app/api/v1/system/log_routes/query.py"
    - "fastapi/app/api/v1/system/log_routes/mutation.py"
    - "fastapi/app/api/health.py"
    - "fastapi/app/schemas/base.py"
    - "frontend/src/api/auth-api.ts"
    - "frontend/src/utils/request.ts"
    - "scripts/api_contracts.py"
    - "scripts/api_endpoint_contracts.py"
    - "scripts/generate_api_contract_report.py"
    - "scripts/api_route_coverage_validation.py"
    - "scripts/validate_api_contracts.py"
    - "docs/api-contract-report.json"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/validate_api_contracts.py ."
    - "git ls-files backend/drf_admin/apps/oauth/urls.py fastapi/app/api/v1/oauth/auth.py fastapi/app/api/v1/oauth/routes/login.py fastapi/app/api/v1/oauth/routes/session.py fastapi/app/api/v1/oauth/routes/profile.py fastapi/app/api/v1/oauth/routes/menus.py fastapi/app/api/v1/oauth/routes/captcha.py frontend/src/api/auth-api.ts"
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
- `fastapi/app/api/v1/oauth/routes/login.py`
- `fastapi/app/api/v1/oauth/routes/session.py`
- `fastapi/app/api/v1/oauth/routes/profile.py`
- `fastapi/app/api/v1/oauth/routes/menus.py`
- `fastapi/app/api/v1/oauth/routes/captcha.py`
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
- 共享响应、分页、字段、错误码、能力边界和关键端点路由覆盖由 `scripts/api_contracts.py`、`scripts/api_endpoint_contracts.py`、`scripts/api_route_coverage_validation.py`、Django/FastAPI 后端测试和前端契约测试共同锁定。

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
- Django: 仅在 `ENABLE_SWAGGER=true` 时访问 `/api/swagger/` 或 `/api/redoc/`
- FastAPI: 非生产环境访问 `/api/swagger/`、`/api/redoc/` 或 `/api/openapi.json`；生产环境按 `settings.is_production` 关闭这三个入口

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
- 前端成功分支仅依赖 `code/data`，错误分支通过 `normalizeApiErrorEnvelope` 统一读取 `data.errors`、`errors`、`msg` 与 `message`（见 `frontend/src/utils/request.ts`）。

### 共享 API 契约验证

共享契约不是靠字段名已经完全一致来保证，而是靠前端真实依赖的公共语义来约束：

- `scripts/api_contracts.py` 定义成功响应、错误响应和分页载荷的跨后端断言。
- `scripts/api_capability_contracts.py` 定义单后端 API 能力边界契约；操作日志已双实现后目录暂为空，机制保留用于登记未来可能出现的单后端独占能力。
- `scripts/api_endpoint_contracts.py` 定义关键端点契约目录，锁定路径、方法、权限、分页和关键字段。
- `scripts/generate_api_contract_report.py` 从关键端点契约目录生成 `docs/api-contract-report.json`；该 JSON 是机器可读的关键端点报告，不作为新的手工事实源。
- `scripts/api_field_contracts.py` 定义首批响应字段契约目录，锁定已登记的 Django/FastAPI 字段漂移面。
- `scripts/api_field_contract_validation.py` 校验字段来源类、读端点字段契约覆盖关系和 `converge` 收敛债务文档登记。
- `scripts/api_frontend_field_contracts.py` 定义前端 API 类型字段契约目录，锁定前端已声明的高价值字段必须挂靠后端字段契约。
- `scripts/api_error_codes.py` 定义共享错误码契约目录，锁定前端刷新逻辑和双后端错误语义。
- `scripts/api_route_coverage_validation.py` 校验关键端点契约能对应到 Django URLConf/AdminRouter 和 FastAPI 具体 `method + path` 路由；通知公告的 `{ids}` 到 `{id}` 兼容只限其共用路由场景。
- `backend/drf_admin/utils/test_response_contract.py` 覆盖 Django 响应中间件的成功、错误和幂等包裹。
- `backend/drf_admin/utils/test_api_capability_contracts.py` 覆盖操作日志不再登记为单后端独占能力。
- `backend/drf_admin/utils/test_api_field_contracts.py` 覆盖 Django serializer 对外字段集合。
- `fastapi/tests/test_api_contracts.py` 覆盖 FastAPI `ResponseModel` 与 `PageResult`。
- `fastapi/tests/test_api_capability_contracts.py` 覆盖单后端独占能力存在时的 FastAPI 源码证据。
- `fastapi/tests/test_api_field_contracts.py` 覆盖 FastAPI schema 对外字段集合。
- `frontend/src/utils/__tests__/api-contract.test.ts` 覆盖前端对 Django `msg/errors` 与 FastAPI `message` 的兼容读取。
- `frontend/src/api/__tests__/api-frontend-field-contract-governance.spec.ts` 覆盖前端字段契约文件入口和首批 API 类型文件登记。
- `scripts/validate_api_contracts.py` 校验契约定义、生成报告、测试文件和本文档入口是否同步。

共享错误码契约目录只记录当前前端与双后端共同依赖的公共错误语义。登录失败、验证码失败等普通业务失败使用 `40000`；只有 Access Token 无效或过期才能使用 `40001`，避免前端误触发 token 刷新流程。

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
- FastAPI：从请求体读取 `refreshToken`（`RefreshTokenRequest`，无查询参数）。
- 前端 `auth-api.ts` 统一以请求体 `{ refreshToken }` 调用，与两套后端均兼容。

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
> 用户输出中的 `mobile/email` 默认保留字段但返回脱敏值；拥有 `system:users:field:plain` 或 `is_superuser` 时返回原文。
> 后台用户创建/更新请求中显式写入非空 `mobile/email` 时，需要 `system:users:field:write` 或 `is_superuser`。

---

### 角色管理

**Django & FastAPI：**
```
GET    /api/v1/system/roles/          # 列表
POST   /api/v1/system/roles/          # 创建
GET    /api/v1/system/roles/{id}/     # 详情
PUT    /api/v1/system/roles/{id}/     # 更新
DELETE /api/v1/system/roles/{id}/     # 删除
DELETE /api/v1/system/roles/          # 批量删除，请求体 ids
GET    /api/v1/system/roles/options/  # 角色下拉选项
GET    /api/v1/system/roles/{id}/menu-ids/ # 角色菜单ID列表
PUT    /api/v1/system/roles/{id}/menus/    # 分配角色菜单权限，请求体 menuIds
```

角色创建/更新请求体支持 `dataScope` 与 `deptIds`。`dataScope` 枚举：1 全部数据、2 本人数据、3 本部门数据、4 本部门及以下数据、5 自定义部门数据；仅自定义部门范围需要提交 `deptIds`。

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
DELETE /api/v1/system/departments/          # 批量删除，请求体 ids
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
GET    /api/v1/system/dicts/{id}/     # 字典类型详情
PUT    /api/v1/system/dicts/{id}/     # 更新字典类型
DELETE /api/v1/system/dicts/          # 批量删除字典类型，请求体 ids
GET    /api/v1/system/dict-items/     # 字典项列表
POST   /api/v1/system/dict-items/     # 创建字典项
GET    /api/v1/system/dict-items/{id}/ # 字典项详情
PUT    /api/v1/system/dict-items/{id}/ # 更新字典项
DELETE /api/v1/system/dict-items/     # 批量删除字典项，请求体 ids
```

---

### 通知公告

**Django / FastAPI 与前端管理页：**
```
GET    /api/v1/system/notices/page           # 通知列表
POST   /api/v1/system/notices                # 创建通知
PUT    /api/v1/system/notices/{id}           # 更新通知
DELETE /api/v1/system/notices/{ids}          # 删除通知
PUT    /api/v1/system/notices/{id}/publish   # 发布通知
PUT    /api/v1/system/notices/{id}/revoke    # 撤回通知
GET    /api/v1/system/notices/my-page/       # 我的通知
```

**我的通知接口（Django & FastAPI）：**
```
GET    /api/v1/system/notices/my-page/       # 我的通知，支持 pageNum/pageSize/title/isRead
```

> Django 返回当前用户可见的已发布通知（全体通知 + 指定到该用户的通知），分页结构与 FastAPI 对齐为 `list/total`。差异：Django 当前无 `NoticeReads` 模型，不跟踪每用户已读状态，`isRead` 统一返回 0；按 `isRead=1` 过滤时返回空列表。FastAPI 通过 `NoticeReads` 返回真实已读状态。

---

### 操作日志

**Django & FastAPI 与前端管理页：**
```
GET    /api/v1/system/logs/page                    # 日志分页，支持 pageNum/pageSize/operation/startTime/endTime
GET    /api/v1/system/logs/visit-trend             # 访问趋势
GET    /api/v1/system/logs/visit-stats             # 访问统计
DELETE /api/v1/system/logs/{ids}                   # 删除日志
DELETE /api/v1/system/logs/clear/{days}            # 清理历史日志
```

**双实现说明：**
- 两套后端均提供 `OperationLog` 模型、写操作落库中间件与上述查询/删除路由，前端日志管理页在两端均可用。
- 写操作（POST/PUT/PATCH/DELETE）由请求日志中间件落库；GET 读请求不落库，避免审计表被轮询淹没。
- 请求体落库前会掩码 `password/token/secret/key/authorization` 等敏感字段。
- Django 权限码 `system:logs:query` / `system:logs:delete` 与 FastAPI 一致；`/logs/page` 列表项字段集合由双后端字段契约 `logs_out` 锁定。
- `/logs/page` 输出中的 `requestBody/responseBody/ip` 默认保留字段但返回脱敏值；拥有 `system:logs:field:plain` 或 `is_superuser` 时返回原文。
- Django 对非法 `status/pageNum/pageSize/startTime/endTime/startDate/endDate/ids` 会返回 400，避免把外部输入解析错误暴露为 500；FastAPI 侧通过 Query/Path 类型约束处理同类入参。

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
GET /api/openapi.json   # OpenAPI JSON（FastAPI 非生产环境）
```

**暴露策略：**
- Django API 文档入口由 `ENABLE_SWAGGER` 控制，默认不暴露。
- FastAPI 在生产环境关闭 `/api/swagger/`、`/api/redoc/` 和 `/api/openapi.json`。

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
| 40000 | 通用业务错误 |
| 40001 | Access Token 无效或过期 |
| 40002 | Refresh Token 无效或过期 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 前端 API 调用注意事项

### 已清理死代码

`frontend/src/api/test/` 下曾存在的示例接口文件已清理。这些文件调用 `/api/test/cases/`、`/api/test/projects/`、`/api/test/tasks/`、`/api/test/devices/`，仓库内没有对应后端契约。

---

**最后更新：** 2026-07-04
**维护者：** DV-Admin Team

**重要提醒：** 本文档不保证完整性，实际开发请以代码为准。
