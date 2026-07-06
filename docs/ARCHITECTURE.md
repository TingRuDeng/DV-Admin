---
ai_summary:
  purpose: "说明 DV-Admin 的系统架构边界、双后端替代关系和关键前端约定。"
  read_when:
    - "评估跨模块影响时"
    - "修改鉴权、路由、缓存、响应包裹或替代后端兼容逻辑时"
  source_of_truth:
    - "frontend/src/utils/route-meta.ts"
    - "frontend/src/utils/view-cache.ts"
    - "frontend/src/store/modules/tags-view-store.ts"
    - "backend/drf_admin/settings.py"
    - "backend/drf_admin/utils/middleware.py"
    - "backend/drf_admin/utils/request_id.py"
    - "backend/drf_admin/apps/system/views/health.py"
    - "fastapi/app/main.py"
    - "fastapi/app/schemas/base.py"
    - "scripts/api_contracts.py"
    - "scripts/api_route_coverage_validation.py"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/validate_api_contracts.py ."
    - "git ls-files frontend/src/utils/route-meta.ts backend/drf_admin/settings.py fastapi/app/main.py"
  stale_when:
    - "前后端目录结构变化"
    - "响应包裹、鉴权、路由 meta 或缓存策略变化"
    - "Django/FastAPI 替代关系变化"
---

# DV-Admin 系统架构

> 本文档记录系统形态、模块边界、跨层数据流与关键中间件行为。

## Purpose

沉淀 DV-Admin 的系统形态、模块边界、跨层数据流与关键中间件行为。

## Source of truth

- `frontend/src/utils/route-meta.ts`
- `frontend/src/utils/view-cache.ts`
- `frontend/src/store/modules/tags-view-store.ts`
- `backend/drf_admin/settings.py`
- `backend/drf_admin/utils/middleware.py`
- `fastapi/app/main.py`
- `fastapi/app/schemas/base.py`

## Key facts

- 前端为 Vue 3 + TypeScript + Element Plus + Vite 7。
- `backend/` 是 Django/DRF 实现，`fastapi/` 是 FastAPI/Tortoise ORM 替代实现。
- 共享 API 或数据契约变化时，需要同时考虑两套后端兼容性。
- Django 与 FastAPI 都提供健康检查能力；Django 请求链路会通过 `X-Request-ID` 串联响应和操作日志。
- 关键 API 端点不仅校验契约目录，还会静态校验 Django/FastAPI 路由中是否存在对应 `method + path`。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 scripts/validate_api_contracts.py .`
- full: `pnpm --dir frontend run quality`
- full: `make -C fastapi quality`

## Stale when

- 中间件顺序或响应包裹协议变化。
- 路由 meta、KeepAlive 缓存键或 ProTable 页面契约变化。

---

## 架构概览

DV-Admin 采用前后端分离架构，支持两种后端实现（Django 和 FastAPI），前端统一调用。
两套后端是**替代关系**：面向同一业务域和同一前端，日常运行或部署通常二选一，而不是并行协作的双后端集群。

```
┌─────────────────────────────────────────────────────────────┐
│                        前端应用                              │
│  Vue 3 + TypeScript + Element Plus + Vite 7                │
│  端口: 9527                                                  │
└─────────────────┬───────────────────────────┬───────────────┘
                  │                           │
                  │ HTTP/REST API             │ WebSocket
                  ▼                           ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│   后端实现 A (Django)       │ │   后端实现 B (FastAPI)      │
│  Django 4.x + DRF + JWT     │ │  FastAPI + Tortoise ORM     │
│  Channels (WebSocket)       │ │  异步架构                    │
│  端口: 8769                 │ │  端口: 8769                 │
│  API 兼容层                 │ │  API 兼容层                 │
└─────────┬───────────────────┘ └─────────┬───────────────────┘
          │                               │
          ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │   MySQL 8.0   │  │  Redis 6.x    │  │   SQLite      │   │
│  │   (生产环境)   │  │  (缓存/会话)  │  │  (开发环境)   │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**运行关系：**
- 前端会接入其中一个后端实现
- Django 与 FastAPI 不是同时为同一请求链路提供服务的上下游组件
- 维护两套实现的目的，是在不同技术栈下提供可切换的同等后端能力

---

## 核心组件

### 前端架构

**技术栈：**
- Vue 3 (Composition API + `<script setup>`)
- TypeScript 5.x
- Element Plus (UI 组件库)
- Vite 7 (构建工具)
- Pinia (状态管理)
- Vue Router 4 (路由)
- Axios (HTTP 客户端)
- UnoCSS (原子化 CSS)

**目录结构：**
```
frontend/src/
├── api/              # API 接口定义
├── assets/           # 静态资源
├── components/       # 公共组件
├── composables/      # 组合式函数
├── constants/        # 常量定义
├── directives/       # 自定义指令
├── enums/            # 枚举定义
├── lang/             # 国际化
├── layouts/          # 布局组件
├── plugins/          # 插件
├── router/           # 路由配置
├── store/            # 状态管理
├── styles/           # 样式文件
├── types/            # 类型定义
├── utils/            # 工具函数
└── views/            # 页面组件
```

**核心模块：**
- **认证模块**：`store/modules/user-store.ts`, `api/auth-api.ts`
- **权限模块**：`store/modules/permission-store.ts`, `directives/permission/`
- **字典模块**：`store/modules/dict-store.ts`, `components/Dict/`
- **布局模块**：`layouts/` (支持 left/top/mix 三种布局模式)

**前端样式治理：**
- `frontend/src/styles` 采用分层结构：`tokens -> theme -> foundation -> skins -> pages`
- 路由页应优先组合 `PageShell`、`FilterPanel`、`DataPanel`，而不是在页面内重复拼接 `glass-panel` 或 `minimal-*` 视觉类
- `UnoCSS` 主要用于布局和局部原子样式，共享视觉皮肤统一放在 `skins/*`
- `_minimal-saas.scss` 仅作为未迁移页面的兼容层，不再作为新增样式的主入口
- `components/CURD` 作为历史兼容层保留；新页面/重构页面统一使用 `ProSearch`、`ProTable`、`ProFormDrawer`
- `ProTable` 支持受控模式与 `request(params)=>{list,total}` 请求驱动模式，对外分页参数统一为 `pageNum/pageSize`
- 页面层（`src/views`）统一约束为 `ProTable(request)` 用法；受控模式仅作为组件层复用能力保留
- 系统页 `requestTableData` 统一通过 `utils/pro-table-request.ts`（`createPageRequest` / `createListRequest`）接入，避免重复手写分页映射

**前端路由与缓存约定：**
- 动态路由在进入前端 store 前，会先将后端返回的 `meta` 统一清洗为前端 `RouteMeta` 语义
- `RouteMeta` 当前统一字段至少包括：`title`、`icon`、`hidden`、`alwaysShow`、`affix`、`keepAlive`、`breadcrumb`、`activeMenu`、`cacheKey`、`cacheByQuery`、`cacheQueryKeys`、`perms`、`roles`、`layout`
- `TagsView` 负责访问标签管理，`cachedViews` 只存放稳定缓存键，不再直接以 `fullPath` 作为唯一缓存标识
- KeepAlive 默认优先使用 `meta.cacheKey`，其次使用无动态参数的 `route.name`；仅在动态参数页或未命名场景下回退到 `fullPath`
- 仅在显式声明 `cacheByQuery=true` 或 `cacheQueryKeys=['k1','k2']` 时，才会按 query 维度区分缓存实例，避免默认缓存膨胀
- 标签行为约定：刷新标签只清理当前标签缓存键；关闭左/右/其它/全部按标签对应缓存键同步删除，重定向刷新复用同一缓存键规则

---

### Django 后端架构

**技术栈：**
- Django 4.x
- Django REST Framework (DRF)
- djangorestframework-simplejwt (JWT 认证)
- django-cors-headers (跨域)
- django-filter (过滤)
- channels (WebSocket)
- django-redis (缓存)

**目录结构：**
```
backend/drf_admin/
├── apps/
│   ├── oauth/        # 认证模块
│   │   ├── views/    # 视图
│   │   ├── serializers/  # 序列化器
│   │   └── urls.py   # 路由
│   ├── system/       # 系统管理模块
│   │   ├── models.py # 数据模型
│   │   ├── views/
│   │   ├── serializers/
│   │   └── filters/  # 过滤器
│   └── information/  # 个人中心模块
├── common/           # 公共模块
├── utils/            # 工具函数
│   ├── middleware.py # 中间件
│   ├── permissions.py # 权限验证
│   └── exceptions.py # 异常处理
├── media/            # 媒体文件
└── settings.py       # 配置文件
```

**核心中间件（按顺序）：**
1. `CorsMiddleware` - CORS 跨域处理
2. `RequestIdMiddleware` - 注入 `X-Request-ID` 链路标识
3. `IpBlackListMiddleware` - IP 黑名单
4. `OperationLogMiddleware` - 操作日志
5. `ResponseMiddleware` - 响应格式化
6. `CamelCaseMiddleWare` - 驼峰/蛇形命名转换

**可观测性约定：**
- Django request id 来源优先级：复用请求头 `X-Request-ID`，缺失时生成新值。
- Django 响应头固定回写 `X-Request-ID`，操作日志同步输出 `RequestId` 字段。
- Django 与 FastAPI 均提供 `OperationLog` 模型、写操作落库中间件和 `/api/v1/system/logs/*` 查询/统计/删除接口。
- 两端操作日志只记录 POST/PUT/PATCH/DELETE 写请求，GET 不落库；落库失败不阻断主请求，敏感字段会先掩码。
- Django 与 FastAPI 的日志权限码统一为 `system:logs:query` / `system:logs:delete`，`/logs/page` 列表字段由双后端字段契约 `logs_out` 锁定。
- Django 健康检查端点位于 `/health`、`/health/live`、`/health/ready`。
- FastAPI 已有结构化日志、慢请求日志和 `/health` 探针，二者都可被部署探针直接调用。

---

### FastAPI 后端架构

**技术栈：**
- FastAPI (异步框架)
- Tortoise ORM (异步 ORM)
- python-jose (JWT)
- passlib (密码哈希)
- Redis (缓存)
- loguru (日志)

**目录结构：**
```
fastapi/app/
├── api/
│   └── v1/           # API v1 版本
│       ├── oauth/    # 认证模块
│       ├── system/   # 系统管理模块
│       ├── information/  # 个人中心模块
│       └── files/    # 文件管理模块
├── core/             # 核心配置
│   ├── config.py     # 配置管理
│   ├── security.py   # 安全模块
│   ├── cache.py      # 缓存服务
│   └── exceptions.py # 异常定义
├── db/
│   └── models/       # 数据模型
├── schemas/          # Pydantic 模型
├── services/         # 业务服务层
├── middleware/       # 中间件
└── utils/            # 工具函数
```

**核心特性：**
- 异步架构，高并发支持
- 非生产环境自动 API 文档（Swagger/ReDoc/OpenAPI JSON），生产环境关闭文档入口
- 健康检查端点
- 慢查询监控
- 结构化日志

---

## 双后端契约治理

Django 与 FastAPI 当前保留历史响应字段差异：Django 输出 `{code,msg,errors,data}`，FastAPI 输出 `{code,message,data}`。前端请求层以 `code/data` 作为成功公共语义，并在错误分支兼容读取 `errors/msg/message`。

本仓库用以下可执行入口约束共享契约：

- `scripts/api_contracts.py`：跨后端响应与分页断言。
- `scripts/api_endpoint_contracts.py`：关键端点契约目录，锁定路径、方法、权限、分页和关键字段。
- `backend/drf_admin/utils/test_response_contract.py`：Django 响应包裹契约测试。
- `fastapi/tests/test_api_contracts.py`：FastAPI 响应与分页契约测试。
- `frontend/src/utils/__tests__/api-contract.test.ts`：前端兼容读取契约测试。
- `scripts/validate_api_contracts.py`：文档、脚本和测试入口一致性检查。

---

## 认证授权机制

### JWT 双 Token 机制

```
┌──────────┐                    ┌──────────┐
│  前端    │                    │  后端    │
└────┬─────┘                    └────┬─────┘
     │                               │
     │  1. 登录请求                   │
     │ ─────────────────────────────>│
     │                               │
     │  2. 返回 Access Token +       │
     │     Refresh Token             │
     │ <─────────────────────────────│
     │                               │
     │  3. 携带 Access Token         │
     │     访问 API                   │
     │ ─────────────────────────────>│
     │                               │
     │  4. Token 有效，返回数据       │
     │ <─────────────────────────────│
     │                               │
     │  5. Token 过期 (401)          │
     │ <─────────────────────────────│
     │                               │
     │  6. 使用 Refresh Token        │
     │     刷新 Access Token         │
     │ ─────────────────────────────>│
     │                               │
     │  7. 返回新的 Access Token     │
     │ <─────────────────────────────│
     │                               │
```

**Token 配置：**
- Access Token 过期时间：30 分钟（可配置）
- Refresh Token 过期时间：7 天（可配置）
- 存储位置：前端 localStorage（支持"记住我"持久化）

**Token 刷新策略：**
- 前端自动检测 401 错误
- 使用 Refresh Token 无感刷新
- 刷新失败则跳转登录页

---

### RBAC 权限模型

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│     用户     │ ──N:M─│     角色     │ ──N:M─│     权限     │
│   (Users)    │       │   (Roles)    │       │(Permissions) │
└──────────────┘       └──────────────┘       └──────────────┘
       │                      │                      │
       │                      │                      │
       ▼                      ▼                      ▼
  用户信息               角色信息               权限信息
  - username             - name                 - name
  - name                 - code                 - type
  - mobile               - status               - route_name
  - roles[]              - permissions[]        - route_path
  - dept                 - is_default           - perm
                         - data_scope
                         - data_depts[]
                                                - parent
```

**权限类型：**
| 类型 | 说明 | 用途 |
|------|------|------|
| CATALOG | 根目录 | 菜单分组 |
| MENU | 菜单 | 页面路由 |
| BUTTON | 按钮 | 操作权限 |
| EXTLINK | 外链 | 外部链接 |

**权限标识格式：** `模块:资源:操作`
- 示例：`system:user:add`、`system:role:edit`

**前端权限职责边界：**
- `userInfo.perms` / `userInfo.roles` 是当前登录用户的“身份快照”，用于按钮与角色指令判定（`v-hasPerm` / `v-hasRole`）
- `RouteMeta.perms` / `RouteMeta.roles` 是路由级访问语义，只表达“该页面需要的权限/角色条件”
- 路由级语义与按钮级语义分层：页面准入看 `RouteMeta`，页面内细粒度操作看按钮权限指令
- 路由守卫会对 `to.matched` 链路逐级校验 `perms/roles`；校验失败统一跳转 `/403`

**权限验证流程：**
1. 用户登录后获取角色列表
2. 根据角色获取权限列表
3. 前端根据权限生成动态路由
4. API 请求时后端验证权限标识

**数据范围控制：**
- 角色包含 `dataScope` 与 `deptIds`，用于表达全部数据、本人数据、本部门、本部门及以下和自定义部门。
- 多角色用户的数据范围按并集合并；任一角色拥有全部数据时不追加数据范围过滤。
- 超级管理员默认拥有全部数据。
- 当前已在 Django 与 FastAPI 的用户列表、操作日志列表和后台通知管理强制应用数据范围过滤；前端表单只负责配置，不作为安全边界。
- 后台通知管理按通知 `publisher_id` 映射可见用户集合；列表和按 ID 后台管理动作均必须经过该范围过滤，FastAPI 表单查询也使用同一规则。“我的通知”仍按接收人可见性判断，不复用后台管理数据范围。

**字段读取控制：**
- 当前第二阶段已在 Django 与 FastAPI 的用户输出和操作日志分页输出接入字段读取脱敏；第六阶段已覆盖通知 `targetUserIds` 输出；第七阶段已覆盖后台通知管理 `content` 输出。
- 用户敏感字段 `mobile/email` 默认保留字段但脱敏；拥有 `system:users:field:plain` 或 `is_superuser` 时返回原文。
- 操作日志敏感字段 `requestBody/responseBody/ip` 默认保留字段但脱敏；拥有 `system:logs:field:plain` 或 `is_superuser` 时返回原文。
- 通知目标用户字段 `targetUserIds` 默认保留字段但返回空数组；拥有 `system:notices:target:plain` 或 `is_superuser` 时返回原始目标用户 ID。
- 后台通知管理正文 `content` 默认保留字段但返回 `[已脱敏]`；拥有 `system:notices:content:plain` 或 `is_superuser` 时返回原文。“我的通知”正文始终返回原文，确保收件人可阅读通知内容。
- 字段读取控制只影响响应输出，不改变查询范围、写入校验和字段契约集合。
- 字段级权限码已纳入权限目录治理：运行时代码、Django 初始权限树和 FastAPI 测试权限 fixture 必须通过 `scripts/field_permission_contracts.py` 保持一致。

**字段写入控制：**
- 当前第三阶段已在 Django 与 FastAPI 的后台用户创建和更新路径接入字段写入拒绝；第四阶段已覆盖后台通知创建和更新路径的指定用户目标字段。
- 后台用户管理请求中显式写入非空 `mobile/email` 时，需要 `system:users:field:write` 或 `is_superuser`。
- 后台通知创建/更新请求中显式写入非空 `targetUserIds` 时，需要 `system:notices:target:write` 或 `is_superuser`。
- 字段写入控制不影响个人中心资料维护路径，不改变数据库字段和响应字段集合。

---

## 数据流向

### 请求数据流

```
前端请求 (camelCase)
    │
    ▼
┌─────────────────────────────────┐
│  Axios 拦截器                    │
│  - 添加 Authorization 头         │
│  - 自动添加 API 版本前缀         │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  Django 中间件                   │
│  - CamelCaseMiddleWare          │
│  - 将 camelCase 转为 snake_case  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  DRF 视图                        │
│  - CamelCaseJSONParser          │
│  - CamelCaseFormParser          │
│  - CamelCaseMultiPartParser     │
└─────────────────────────────────┘
    │
    ▼
数据库操作 (snake_case)
```

### 响应数据流

```
数据库查询结果 (snake_case)
    │
    ▼
┌─────────────────────────────────┐
│  DRF 序列化器                    │
│  - 数据验证                      │
│  - 数据转换                      │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  DRF 渲染器                      │
│  - CamelCaseJSONRenderer        │
│  - 将 snake_case 转为 camelCase  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  ResponseMiddleware             │
│  - 统一响应格式                  │
│  - {code, message, data}        │
└─────────────────────────────────┘
    │
    ▼
前端接收 (camelCase)
```

---

## WebSocket 支持

### Django Channels 配置

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://localhost:6379/4'],
        },
    },
}
```

### 前端 WebSocket 集成

```typescript
// composables/websocket/useStomp.ts
// 使用 STOMP 协议连接 WebSocket

// 功能：
// - 字典实时同步
// - 在线用户统计
// - 系统通知推送
```

---

## 缓存策略

### Redis 缓存使用

| 缓存类型 | 用途 | 过期时间 | 清除时机 |
|---------|------|---------|---------|
| Session | 用户会话 | 浏览器关闭 | 登出时 |
| User Info | 用户信息 | 30 分钟 | 用户信息变更 |
| Dict Data | 字典数据 | 10 分钟 | 字典变更 |
| Token Blacklist | Token 黑名单 | Token 过期时间 | 自动过期 |

### 降级策略

当 Redis 不可用时：
- Django：自动降级到 `LocMemCache`
- FastAPI：自动降级到内存缓存
- WebSocket：降级到 `InMemoryChannelLayer`

---

## 部署架构

### 开发环境

```
┌─────────────────┐
│  前端开发服务器  │  localhost:9527
│  (Vite Dev)     │
└────────┬────────┘
         │ 代理 /dev-api -> localhost:8769
         ▼
┌─────────────────┐
│  后端开发服务器  │  localhost:8769
│  (Django/FastAPI)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│SQLite │ │ Redis │
└───────┘ └───────┘
```

### 生产环境

```
┌─────────────────┐
│   Nginx 反向代理 │  :80/:443
└────────┬────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│  前端    │         │  后端    │
│  静态文件 │         │  Gunicorn│
│  /usr/share/nginx/html │  :8769  │
└─────────┘         └────┬────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
               ┌────────┐ ┌────────┐
               │ MySQL  │ │ Redis  │
               └────────┘ └────────┘
```

### Compose 模板

仓库根目录提供 `compose.yaml` 作为本地容器化联调和预部署模板：

- `frontend` profile 启动 Vite 前端，默认连接宿主机 `8769` 后端端口。
- `django` profile 启动 Django 后端，使用 `deploy/env/django.compose.env` 生成容器内 `.env.compose`。
- `fastapi` profile 启动 FastAPI 后端，使用 `deploy/env/fastapi.compose.env` 生成容器内 `.env`。
- `mysql` 与 `redis` 是共享基础设施服务。

Django 与 FastAPI 仍是替代关系；同一次 compose 运行应只选择 `django` 或 `fastapi` 其中一个后端 profile，避免两个服务争用 `8769` 端口。

常用命令：

```bash
docker compose --profile frontend --profile django up
docker compose --profile frontend --profile fastapi up
docker compose config
```

---

## 关键设计决策

### 1. 双后端替代式架构

**背景：** 项目同时维护 Django 和 FastAPI 两个后端实现，服务同一套前端和业务能力

**决策：** 将两套后端视为可替代实现，保持共享 API 完全兼容，前端无需区分

**影响：**
- 运行和部署时通常只启用其中一种后端实现
- API 变更需同步两个后端
- 测试需覆盖两个后端
- 文档需标注两个后端的差异

### 2. 命名自动转换

**背景：** Python 使用 snake_case，JavaScript 使用 camelCase

**决策：** 通过中间件自动转换，代码中保持各自习惯

**影响：**
- 不要手动转换命名
- 中间件顺序很重要
- 日志中看到的是 snake_case

### 3. 动态路由

**背景：** 权限控制需要根据用户角色显示不同菜单

**决策：** 后端返回菜单数据，前端动态生成路由

**影响：**
- 前端路由配置只包含静态路由
- 权限变更需刷新页面
- 路由缓存策略需考虑

---

**最后更新：** 2026-07-04
**维护者：** DV-Admin Team
