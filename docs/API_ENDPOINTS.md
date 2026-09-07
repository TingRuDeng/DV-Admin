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
- 用户与角色写入执行权限子集和数据范围委派校验；无操作权限或越界授权返回 HTTP 403。角色关联范围外用户时修改/停用/删除均拒绝；批删逐条返回不可重试的 `PERMISSION_DENIED`。Django 兼容 PATCH 授权入口执行相同规则。
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
- `scripts/api_field_contract_validation.py` 校验字段来源类、读端点字段契约覆盖关系、写端点字段契约覆盖关系、前端字段契约覆盖完整性和 `converge` 收敛债务文档登记。
- `scripts/api_frontend_field_contracts.py` 定义前端 API 类型字段契约目录和非普通对象响应豁免，锁定前端已声明的高价值字段必须挂靠后端字段契约。
- `scripts/api_error_codes.py` 定义共享错误码契约目录，锁定前端刷新逻辑和双后端错误语义。
- `scripts/api_route_coverage_validation.py` 校验关键端点契约能对应到 Django URLConf/AdminRouter 和 FastAPI 具体 `method + path` 路由；通知公告的 `{ids}` 到 `{id}` 兼容只限其共用路由场景。
- `scripts/api_runtime_route_contracts.py` 在关键契约外显式登记所有共享、单后端和兼容业务路由。两端 `test_runtime_route_inventory.py` 分别递归枚举实际 URLConf / ASGI 路由树，对比 `method + 规范化路径`，新增、移除或改方法都会失败；不是扫描预设源码文件列表。
- 规范化统一参数占位符和尾斜杠，不等同于字段/行为兼容承诺。只排除明确的健康、API 文档、开发静态媒体入口及隐式 HEAD/OPTIONS；独立 HEAD/OPTIONS、未知路由类型或新嵌套模块不会静默跳过。根校验器仅检查登记自洽与两端测试入口存在，不同时导入 Django/FastAPI。
- 原有单后端和兼容入口被登记不代表推荐新调用，也不代表补齐功能差异；例如 Django 的旧个人信息别名、DRF PATCH，FastAPI 的嵌套字典项和 OAuth 表单登录仍是兼容边界。
- `backend/drf_admin/utils/test_response_contract.py` 覆盖 Django 响应中间件的成功、错误和幂等包裹。
- `backend/drf_admin/utils/test_api_capability_contracts.py` 覆盖操作日志不再登记为单后端独占能力。
- `backend/drf_admin/utils/test_api_field_contracts.py` 覆盖 Django serializer 对外字段集合。
- `fastapi/tests/test_api_contracts.py` 覆盖 FastAPI `ResponseModel` 与 `PageResult`。
- `fastapi/tests/test_api_capability_contracts.py` 覆盖单后端独占能力存在时的 FastAPI 源码证据。
- `fastapi/tests/test_api_field_contracts.py` 覆盖 FastAPI schema 对外字段集合。
- `frontend/src/utils/__tests__/api-contract.test.ts` 覆盖前端对 Django `msg/errors` 与 FastAPI `message` 的兼容读取。
- `frontend/src/api/__tests__/api-frontend-field-contract-governance.spec.ts` 覆盖前端字段契约文件入口和关键豁免片段；覆盖完整性由根契约校验器反向检查。
- `scripts/validate_api_contracts.py` 校验契约定义、生成报告、测试文件和本文档入口是否同步。

共享错误码契约目录只记录当前前端与双后端共同依赖的公共错误语义。登录失败、验证码失败等普通业务失败使用 `40000`；只有 Access Token 无效或过期才能使用 `40001`，避免前端误触发 token 刷新流程。

共享 `429` 表示限速，HTTP 状态同为 429，并保留 `Retry-After`；共享 `503` 表示服务依赖不可用，HTTP 状态同为 503，不得当作令牌失效清除本地登录信息。

---

## 认证模块 (OAuth)

### 登录

**Django & FastAPI：**
```
POST /api/v1/oauth/login/
```

账号 5 分钟内失败 5 次后冷却 5 分钟，单 IP 每分钟最多 60 次尝试。第 5 次失败及被限速请求返回 429 和 `Retry-After`，被拒请求不延长冷却；成功只清空账号失败计数。FastAPI `/api/v1/oauth/token/` 表单入口执行同一规则。登录保护 Redis 不可用返回 503，开发环境也需要 Redis。

部署须通过 `TRUSTED_PROXY_IPS` 明确代理 IP/CIDR；未配置时仅采用连接对端 IP。FastAPI Uvicorn 应禁用框架代理头解析，由应用统一校验受信代理链。

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
    "expiresIn": 1800,
    "refreshExpiresIn": 604800
  }
}
```

以上为 FastAPI 默认有效期示例，不是不可配置的常量。两端 Access Token 默认均为 1800 秒（30 分钟）；FastAPI Refresh Token 默认 604800 秒（7 天），Django 默认 86400 秒（1 天）。FastAPI 使用 `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS`，Django 使用 `JWT_ACCESS_TOKEN_LIFETIME`（分钟）/ `JWT_REFRESH_TOKEN_LIFETIME`（天）覆盖；以实际响应和运行配置为准。

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
    "expiresIn": 1800
  }
}
```

**注意：** Django 后端已统一使用 `/refresh-token/` 接口，与 FastAPI 保持一致。

两套后端都执行 Refresh Token 轮换：刷新成功后返回新的 `refreshToken`，旧令牌立即失效且再次使用返回 `40002`。前端只允许原请求在刷新成功后重试一次；若重试仍返回 `40001`，立即结束刷新链并跳转登录页。

FastAPI 生产环境无法读取或写入令牌撤销状态时返回 HTTP 503（业务 `code=503`），不冒充令牌失效。刷新遇到 503 时前端结束请求但保留登录信息；用户主动退出仍清理本地状态，服务端撤销未确认则提示。刷新后的令牌保留原会话时间，仍受用户级撤销约束。

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
DELETE /api/v1/system/users/          # 批量删除，请求体 ids
POST   /api/v1/system/users/batch-delete/retry/ # 逐条重试失败项，请求体 ids
```

#### 其他用户端点

**Django & FastAPI：**
```
GET  /api/v1/system/users/options/              # 用户下拉选项
PUT  /api/v1/system/users/{id}/password/reset/  # 重置密码
GET  /api/v1/system/users/{id}/permissions/     # 用户权限ID列表
```

**Django & FastAPI：**
```
GET  /api/v1/system/users/template              # 用户导入模板
POST /api/v1/system/users/import                # 导入用户
POST /api/v1/system/users/export/               # 导出用户
```

> 两套后端的共享 `PUT` 密码重置端点都要求请求体提供 `password` 与 `confirm_password`；两次密码必须一致，默认 15-128 个 Unicode 字符，不得使用常见密码，不要求字符类型组合，首尾空格参与密码。敏感字段不得放入 URL query，成功响应不回显明文。FastAPI 额外保留已标记废弃的 `POST /api/v1/system/users/{id}/password/reset/` 兼容入口，并按 `DEFAULT_PASSWORD` 重置，该配置也必须满足新策略；共享前端不使用该兼容入口。
> 用户输出中的 `mobile/email` 默认保留字段但返回脱敏值；拥有 `system:users:field:plain` 或 `is_superuser` 时返回原文。
> 后台用户创建/更新请求中显式写入非空 `mobile/email` 时，需要 `system:users:field:write` 或 `is_superuser`。
> 用户列表、详情、下拉选项、权限查询、状态更新、密码重置和删除均受角色数据范围约束；范围外 ID 按不存在处理。批量删除初次请求会先预检全部 ID，任一 ID 不存在或不可见时整批拒绝且不删除目标；预检通过后，当前用户等保护对象或单条执行异常会作为失败项返回，不阻塞其他目标。
> 创建用户或显式变更用户部门时，目标部门必须处于操作者的数据范围；仅本人（`SELF`）范围不能创建用户。提交角色 ID 时必须全部有效，不存在的角色不会被静默忽略。
> 模板和导出响应统一返回 `{ filename, content, contentType }`，其中 `content` 是 Base64 编码；模板为 `.xlsx`，导出文件为带 UTF-8 BOM 的 CSV。前端不得把该 JSON 响应当作 Blob。
> 用户导出仅包含当前操作者范围内的用户，并复用 `mobile/email` 脱敏规则；用户导入仅接受 `.xlsx`，逐行校验目标部门、敏感字段写入权限和全部角色 ID，失败行不会创建用户。

用户导入的唯一字段、部门和角色预加载只查询当前文件引用值，每批最多 500 项；同文件重复、逐行拒绝和意外失败事务回滚语义不变。本项不改响应/分页，不新增异步导入任务。

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
POST   /api/v1/system/roles/batch-delete/retry/ # 逐条重试失败项，请求体 ids
GET    /api/v1/system/roles/options/  # 角色下拉选项
GET    /api/v1/system/roles/{id}/menu-ids/ # 角色菜单ID列表
PUT    /api/v1/system/roles/{id}/menus/    # 分配角色菜单权限，请求体 menuIds
```

角色创建/更新请求体支持 `dataScope` 与 `deptIds`。`dataScope` 枚举：1 全部数据、2 本人数据、3 本部门数据、4 本部门及以下数据、5 自定义部门数据；仅自定义部门范围需要提交 `deptIds`。

> 内置系统角色不可删除：单条删除返回 `400`；批量删除中对应项目返回 `PROTECTED_OBJECT` 且 `retryable=false`，不阻塞同批普通角色。

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
GET    /api/v1/system/menus/options/  # 父级菜单树选项，data 节点为 id/label/children
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
GET    /api/v1/system/dict-items/     # 字典项分页，dictCode/pageNum/pageSize
POST   /api/v1/system/dict-items/     # 创建字典项
GET    /api/v1/system/dict-items/{id}/ # 字典项详情
PUT    /api/v1/system/dict-items/{id}/ # 更新字典项
DELETE /api/v1/system/dict-items/     # 批量删除字典项，请求体 ids
```

两端字典项列表均返回 `data: {list, total}`，按字典编码筛选使用 `dictCode`，不使用旧的
`dict__dict_code`。前端标签/选择器的 `getDictItems` 按 `pageSize=100` 逐页取齐，再向调用方
返回数组；不是另一个数组型后端接口。加载失败或分页响应不完整时不写入部分缓存。

通知表单使用的用户选项地址为 `GET /api/v1/system/users/options/`，前端直接请求尾斜杠路径，
避免 Django 301 跳转丢失开发代理前缀。FastAPI 同时保留旧的无尾斜杠入口，两个地址直接返回
同一数组响应，不依赖重定向；权限要求不变。

---

### 通知公告

**Django / FastAPI 与前端管理页：**
```
GET    /api/v1/system/notices/page           # 通知列表
GET    /api/v1/system/notices/{id}/form      # 后台通知表单
POST   /api/v1/system/notices                # 创建通知
PUT    /api/v1/system/notices/{id}           # 更新通知
DELETE /api/v1/system/notices/               # 批量删除通知，请求体 ids
DELETE /api/v1/system/notices/{ids}          # 兼容旧逗号分隔路径
POST   /api/v1/system/notices/batch-delete/retry/ # 逐条重试失败项，请求体 ids
PUT    /api/v1/system/notices/{id}/publish   # 发布通知
PUT    /api/v1/system/notices/{id}/revoke    # 撤回通知
GET    /api/v1/system/notices/my-page/       # 我的通知
GET    /api/v1/system/notices/{id}/detail    # 查看可见通知并标记已读
PUT    /api/v1/system/notices/read-all       # 当前用户可见通知全部已读
```

> 后台通知创建/更新请求中显式写入非空 `targetUserIds` 时，需要 `system:notices:target:write` 或 `is_superuser`。
> 通知输出中的 `targetUserIds` 默认保留字段但返回空数组；拥有 `system:notices:target:plain` 或 `is_superuser` 时返回原始目标用户 ID。
> 后台通知管理输出中的 `content` 默认保留字段但返回 `[已脱敏]`；拥有 `system:notices:content:plain` 或 `is_superuser` 时返回原文。“我的通知”接口仍返回正文原文。
> 后台通知管理列表、更新、删除、发布和撤回会按通知 `publisherId` 套用当前用户角色数据范围；FastAPI 表单查询也使用同一规则。不在范围内的通知按不存在处理。

### 结果化批量删除

用户、角色和通知的批量删除均使用 JSON 请求体，并返回 `200` 的逐条处理结果。请求体为：

```json
{
  "ids": [123, 456]
}
```

响应位于统一包裹的 `data` 字段中：

```json
{
  "status": "partial_failed",
  "totalCount": 2,
  "successCount": 1,
  "failedCount": 1,
  "processedCount": 2,
  "successItems": [
    {"objectId": "123", "objectName": "对象名称"}
  ],
  "failures": [
    {
      "objectId": "456",
      "objectName": "对象名称",
      "errorCode": "PUBLISHED_OBJECT",
      "message": "失败原因",
      "retryable": true
    }
  ]
}
```

`status` 取 `succeeded`、`partial_failed` 或 `failed`；请求 ID 去重后计入 `totalCount`。初次请求对不存在或越权 ID 进行整批预检，预检失败不会删除任何目标；保护对象、已发布通知和单条删除异常在预检通过后逐条返回。`failures[].retryable=true` 的 ID 可单独或合并提交到对应的 `batch-delete/retry/` 端点，`false` 表示无需再次尝试。当前稳定错误码为 `PROTECTED_OBJECT`、`PUBLISHED_OBJECT`、`NOT_FOUND`、`ALREADY_DELETED` 和 `DELETE_FAILED`。

**我的通知接口（Django & FastAPI）：**
```
GET    /api/v1/system/notices/my-page/       # 我的通知，支持 pageNum/pageSize/title/isRead
```

> 两套后端都只返回当前用户可见的已发布通知（全体通知 + 指定到该用户的通知），分页结构统一为 `list/total`。查看详情会写入 `NoticeReads`，`read-all` 只标记当前用户可见的已发布通知；`isRead` 返回和过滤真实持久化状态。

---

### 操作日志

**Django & FastAPI 与前端管理页：**
```
GET    /api/v1/system/logs/page                    # 日志分页，支持 pageNum/pageSize/operation/username/requestId/objectType/objectId/method/status/startTime/endTime
GET    /api/v1/system/logs/{id}                    # 日志详情
GET    /api/v1/system/logs/visit-trend             # 访问趋势，支持 startDate/endDate，最多 366 个自然日
GET    /api/v1/system/logs/visit-stats             # 访问统计
DELETE /api/v1/system/logs/{ids}                   # 删除日志
DELETE /api/v1/system/logs/clear/{days}            # 清理历史日志
```

**双实现说明：**
- 两套后端均提供 `OperationLog` 模型、写操作落库中间件与上述查询/删除路由，前端日志管理页在两端均可用。
- 写操作（POST/PUT/PATCH/DELETE）由请求日志中间件落库；GET 读请求不落库，避免审计表被轮询淹没。
- 请求体写入结构化运行日志和操作日志前都会掩码 `password/token/secret/key/authorization` 等敏感字段；非 JSON 请求体解析失败时不记录原文。
- 两端均将响应头对应的 `requestId` 持久化；客户端传入值会去除首尾空白、限制为 64 字符，并只接受字母、数字、点、下划线、冒号和连字符，非法值由服务端重新生成。失败写请求额外保存脱敏、截断后的 `responseBody`，并从脱敏后的统一错误响应提取 `errorMsg`。成功写请求不保存响应体和错误摘要。
- Django 权限码 `system:logs:query` / `system:logs:delete` 与 FastAPI 一致；`/logs/page` 和 `/logs/{id}` 字段集合由双后端字段契约 `logs_out` 锁定。
- `/logs/page` 与 `/logs/{id}` 输出中的 `requestBody/responseBody/ip` 默认保留字段但返回脱敏值；拥有 `system:logs:field:plain` 或 `is_superuser` 时返回原文。
- 日志通过稳定业务命名关联对象：`objectType`（如 `system.users`、`system.roles`）与 `objectId` 均为精确匹配字段；非标准动作由业务入口显式登记，不从 URL 或 ORM 表名推断。
- `requestContext` 保存脱敏后的结构化上下文，包括路径参数、查询参数、请求体摘要、白名单 Header、文件元数据、变更字段、请求体哈希及批量元数据；上下文超过大小上限时保留 `truncated=true`。白名单中的 Referer 仅保留 URL 结构和参数名，查询与片段参数值统一掩码。FastAPI 审计中间件对可能携带请求体的请求设置采集上限：超过上限或缺少合法 `Content-Length` 时不读取整包请求体，改为记录 `bodyCapture.status/reason/maxBytes` 并保留 `truncated=true`，不影响业务端点继续消费上传流；无体方法在没有 body 信号时仍按空 body 处理。
- `/logs/page`、`/logs/{id}`、`/logs/visit-trend`、`/logs/visit-stats`、删除和历史清理统一复用日志数据范围；不在当前用户可见范围内的 ID 按不存在处理。
- `/logs/visit-trend` 两端均在数据库按日聚合并为缺失日期补 0；反向区间或超过 366 个自然日的查询返回 400。FastAPI 以 `startDate/endDate` 为公开参数，并在过渡期兼容 `start_date/end_date`。
- 批量删除日志采用全有或全无语义，任一 ID 不存在或不可见时不删除任何目标；历史清理只清理当前用户范围内的日志。
- `/logs/page` 与 `/logs/{id}` 返回 `requestId`；分页接口支持通过 `requestId` 精确筛选，详情页可据此关联响应头和结构化运行日志。
- `/logs/page` 支持通过 `objectType` 与 `objectId` 精确筛选；详情与列表返回 `objectType/objectId/requestContext`。
- Django 对非法 `status/pageNum/pageSize/startTime/endTime/startDate/endDate/ids` 会返回 400，避免把外部输入解析错误暴露为 500；FastAPI 侧通过 Query/Path 类型约束处理同类入参。

---

## 个人中心模块 (Information)

生产媒体存储统一 `/data/media`，所选后端读写、Nginx 只读；接口仍返回既有 `/media/` URL 和相对标识，不迁移数据库记录。旧文件复制与回退见 [媒体部署说明](MEDIA_DEPLOYMENT.md)。

头像使用 Pillow 识别实际格式、校验扩展名并逐帧解码，不以 MIME 声明作为内容证明；仍为 2 MiB 上限，单边不超过 4096 像素、最多 100 帧、累计解码最多 3200 万像素。保留原有可解码图片格式；拒绝不支持、伪装、损坏或超预算文件时 HTTP 400，不保存新文件、不改变原头像。数据库保存失败也回滚并清理新文件。普通附件规则不变。

**Django / FastAPI 共享端点：**

```text
GET  /api/v1/information/profile/       # 获取个人信息
GET  /api/v1/information/password-policy # 获取新密码长度规则，要求登录
PUT  /api/v1/information/profile/       # 更新 name/email/mobile/gender
PUT  /api/v1/information/password       # 修改密码
POST /api/v1/information/change-avatar/ # 上传头像，multipart 字段为 file
```

修改密码请求字段统一为 `oldPassword/newPassword/confirmPassword`，头像响应统一包含 `avatar/url`，头像文件上限为 2 MiB。Django 暂时保留 `change-information/`、`change-password/` 以及旧密码字段作为兼容入口，但共享前端不再依赖这些旧接口。

密码规则响应为 `{ "minLength": 15, "maxLength": 128 }`（包在标准 `data` 内），读取实际配置，不是前端硬编码。`PASSWORD_MIN_LENGTH/PASSWORD_MAX_LENGTH` 只允许在 15-128 范围内收紧；两端新密码还需通过固定版本 SecLists 常见密码清单。已有密码登录不追溯新规则，允许原有空格。FastAPI 参数校验失败返回 HTTP 422、`code=422`，只含字段/错误类型/说明，不含输入密码；Django 密码校验沿用 HTTP 400、`code=40000`。

---

## 文件管理模块 (Files)

**Django / FastAPI 共享端点：**
```
POST   /api/v1/files/   # 上传文件，返回 name/url/path
DELETE /api/v1/files/?filePath=files/{user_id}/{filename}   # 删除当前用户文件
```

> 两套后端的通用上传和用户 Excel 导入使用 `MAX_UPLOAD_SIZE`（默认 10 MiB）作为硬上限。通用上传按 `files/{user_id}/` 隔离目录，先写有界临时文件再原子替换；删除接口只允许当前用户删除自己目录中的文件。`filePath` 必须使用上传响应 `data.path`，不能传完整 `data.url`、绝对路径或包含 `..` 的路径。

用户 Excel 导入的公开部门查询参数为 `deptId`；两套后端在过渡期兼容 `dept_id`。`MAX_UPLOAD_SIZE` 必须为正整数，非法配置会在应用启动时拒绝加载。

---

## 健康检查（Django & FastAPI）

```
GET /health        # 基本健康检查
GET /health/ready  # 就绪检查（含数据库、Redis）
GET /health/live   # 存活检查
```

**实现说明：**
- Django：`backend/drf_admin/apps/system/views/health.py`，响应头会携带 `X-Request-ID`。
- FastAPI：`fastapi/app/api/health.py`，响应中包含结构化依赖检查，响应头同样携带 `X-Request-ID`。

两端生产就绪探针要求数据库和 Redis 正常，依赖缺失或故障真实返回 HTTP 503；存活探针不访问数据库或 Redis。默认 localhost Redis URL 也是有效配置，必须实际探活。Nginx 直接转发 `/health/ready`、`/health/live`，`/nginx-health` 的固定 200 仅表示代理本身存活。

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

**最后更新：** 2026-09-06
**维护者：** DV-Admin Team

**重要提醒：** 本文档不保证完整性，实际开发请以代码为准。
