# DV-Admin 系统架构

> 本文档描述系统的整体架构设计，是架构决策的权威文档。

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
2. `IpBlackListMiddleware` - IP 黑名单
3. `OperationLogMiddleware` - 操作日志
4. `ResponseMiddleware` - 响应格式化
5. `CamelCaseMiddleWare` - 驼峰/蛇形命名转换

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
- 自动 API 文档 (Swagger/ReDoc)
- 健康检查端点
- 慢查询监控
- 结构化日志

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

**权限验证流程：**
1. 用户登录后获取角色列表
2. 根据角色获取权限列表
3. 前端根据权限生成动态路由
4. API 请求时后端验证权限标识

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

**最后更新：** 2026-03-23
**维护者：** DV-Admin Team
