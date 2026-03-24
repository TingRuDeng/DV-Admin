# DV-Admin 代理工作指南

> 本文件是代理在此仓库工作的**单一权威规则入口**。所有工作流规则、启动检查和约束都在此定义。

## 仓库概述

DV-Admin 是一个基于 RBAC 模型权限控制的中小型应用基础开发平台，采用前后端分离架构。

**核心组件：**
- **前端**：Vue 3 + TypeScript + Element Plus + Vite 7
- **后端实现 A（Django）**：Django 4.x + DRF + JWT + Channels（WebSocket）
- **后端实现 B（FastAPI）**：FastAPI + Tortoise ORM（异步，与 Django API 兼容）

**后端实现关系：**
- `backend/`（Django）与 `fastapi/`（FastAPI）是面向同一业务域和同一前端的两套**替代实现**
- 日常开发、联调和部署通常**二选一**，不需要同时启动两套后端
- 为了保证前端可在两套实现之间切换，涉及对外 API / 数据契约的变更时仍需保持兼容

**默认账户：**
- `admin/123456` - 超级管理员
- `visitor/123456` - 访客用户

---

## 启动检查清单

在开始任何开发工作前，必须完成以下检查：

### 1. 环境准备

**前端环境：**
```bash
cd frontend
pnpm install          # 安装依赖
./dev.sh start       # 启动开发服务器（默认端口 9527）
```

**后端环境（Django）：**
```bash
cd backend
uv sync               # 安装依赖
cp .env.example .env.dev
./dev.sh start        # 启动开发服务器
```

**后端环境（FastAPI）：**
```bash
cd fastapi
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env
./scripts/dev.sh      # 或 uv run uvicorn app.main:app --reload --port 8769
```

> Django 和 FastAPI 是替代关系。开发环境通常只选择其中一种后端启动；除非你在做兼容性对比或双实现同步，否则不需要两套后端同时运行。

### 2. 必读文件

根据任务类型，按顺序阅读：

| 任务类型 | 阅读顺序 |
|---------|---------|
| 前端开发 | `docs/README.md` → `frontend/src/` 目标模块 → 本文件 |
| 后端开发（Django） | `docs/README.md` → `backend/drf_admin/apps/` 目标模块 → 本文件 |
| 后端开发（FastAPI） | `docs/README.md` → `fastapi/app/api/v1/` 目标模块 → 本文件 |
| API 修改 | `docs/API_ENDPOINTS.md` → `docs/DATABASE_SCHEMA.md` → 目标代码 |
| 权限相关 | `docs/ARCHITECTURE.md` 权限章节 → `backend/drf_admin/apps/system/models.py` |

### 3. 验证环境

- [ ] 前端开发服务器正常运行（http://localhost:9527）
- [ ] 已选择的后端实现 API 服务正常运行（http://localhost:8769）
- [ ] 数据库连接正常
- [ ] 能够使用默认账户登录

---

## 工作流规则

### 代码修改规则

0. **分支 / 工作区隔离**
   - 任何会产生文件改动的任务，默认不得直接在 `master` / `main` 分支工作
   - 开始修改前，必须先检查当前分支；如果当前位于 `master` / `main`，应先创建非主分支或独立 `git worktree`
   - 分支前缀不强制，可遵循当前团队约定（如 `feature/*`、`fix/*`、`chore/*`、`codex/*`）
   - 多智能体并行工作时，优先为每个智能体分配独立 worktree，避免互相污染工作区
   - 远端受保护分支只能作为最终合并目标，不能作为日常直接修改分支

1. **API 契约不可随意变更**
   - 修改 API 路径、参数、响应格式前，必须检查前端调用点
   - 使用 `grep -r "api/xxx" frontend/src/` 搜索前端调用
   - Django 和 FastAPI 是替代实现；只要变更影响共享对外契约，就必须保持两套实现的 API 兼容性

2. **数据库模型变更**
   - 修改模型后必须创建并执行迁移
   - Django：`uv run python manage.py makemigrations --env dev`
   - FastAPI：修改 `app/db/models/` 后重启服务自动同步（开发环境）
   - 生产环境必须手动管理迁移

3. **权限相关变更**
   - 修改权限逻辑前，必须阅读 `docs/ARCHITECTURE.md` 权限章节
   - 新增 API 必须考虑是否需要权限控制
   - 权限白名单在 `backend/drf_admin/settings.py` 的 `WHITE_LIST` 中

4. **前端状态管理**
   - 用户状态：`frontend/src/store/modules/user-store.ts`
   - 权限路由：`frontend/src/store/modules/permission-store.ts`
   - 字典缓存：`frontend/src/store/modules/dict-store.ts`

### 测试规则

本仓库以 `.github/workflows/quality-gates.yml` 为合并前强制门禁。

**前端测试：**
```bash
cd frontend
pnpm run quality       # 聚合质量检查 (lint + type-check + test:unit)
pnpm run build         # 构建检查（含类型检查）
pnpm run lint          # 代码检查（eslint + prettier + stylelint）
pnpm run test:unit     # 单元测试
```

**后端测试（Django）：**
Django 后端已接入可执行的 Ruff + pytest 门禁；为避免历史问题一次性阻塞 CI，当前对 E501、F401、I001、F403、F405 采用临时 defer，后续再分阶段收紧规则。
```bash
cd backend
uv sync --group dev
uv run ruff check .    # 代码风格检查
uv run pytest          # 运行测试
```

**后端测试（FastAPI）：**
FastAPI 已提供可执行的质量门禁入口 `make quality`；当前类型检查覆盖 schema 层。其分页响应契约已与 frontend / Django 对齐为 `list/total`，内部保留少量只读兼容访问器用于过渡。
```bash
cd fastapi
uv sync --group dev
make quality           # 聚合质量检查 (ruff + mypy + pytest + coverage)
```

### 提交规则

- 提交前必须运行 `pnpm run lint`（前端）或 `ruff check`（后端）
- 遵循 Conventional Commits 规范
- 前端使用 `pnpm run commit` 进行交互式提交

---

## 关键约束

### 不可随意修改的内容

1. **API 命名约定**
   - 后端使用蛇形命名（snake_case）
   - 前端使用驼峰命名（camelCase）
   - **自动转换由中间件处理**，不要手动转换
   - Django：`djangorestframework_camel_case.middleware.CamelCaseMiddleWare`
   - FastAPI：响应格式统一为 `{code, message, data}`

2. **认证机制**
   - 使用 JWT 双 token 机制（access + refresh）
   - Access Token 默认 30 分钟过期
   - Refresh Token 默认 7 天过期
   - Token 存储在前端 `AuthStorage` 中

3. **RBAC 权限模型**
   - 用户 → 角色 → 权限 三层关系
   - 权限类型：CATALOG（目录）、MENU（菜单）、BUTTON（按钮）、EXTLINK（外链）
   - 权限标识格式：`模块:操作`（如 `system:user:add`）

4. **数据库表命名**
   - 表名前缀：`system_`（系统模块）、`oauth_`（认证模块）
   - 多对多关系表：`system_users_to_system_roles`

### 必须保持兼容的内容

1. **两个后端的 API 兼容性**
   - Django 和 FastAPI 后端是替代实现，前端应可切换使用
   - 共享业务接口的 URL 路径、请求参数、响应格式必须保持一致

2. **前端 API 调用**
   - 所有 API 调用在 `frontend/src/api/` 目录下
   - 使用统一的 `httpRequest` 实例

---

## 常见任务指南

### 新增 API 端点

1. **Django 后端：**
   - 在 `backend/drf_admin/apps/` 对应模块的 `views/` 创建视图
   - 在 `urls.py` 注册路由
   - 如需权限控制，在 `permissions` 表添加记录

2. **FastAPI 后端：**
   - 在 `fastapi/app/api/v1/` 对应模块创建端点
   - 在 `__init__.py` 注册路由
   - 在 `app/schemas/` 定义请求/响应模型

3. **前端调用：**
   - 在 `frontend/src/api/` 创建或更新 API 文件
   - 使用 `httpRequest` 发起请求

### 新增数据库模型

1. **Django：**
   - 在 `backend/drf_admin/apps/` 对应模块的 `models.py` 定义模型
   - 运行 `makemigrations` 和 `migrate`
   - 在 `admin.py` 注册管理界面（可选）

2. **FastAPI：**
   - 在 `fastapi/app/db/models/` 定义模型
   - 在 `app/schemas/` 定义对应的 Pydantic 模型

### 新增前端页面

1. 在 `frontend/src/views/` 创建页面组件
2. 在 `frontend/src/router/index.ts` 添加路由（或通过后端动态路由）
3. 如需权限控制，在后端添加菜单/权限记录

---

## 文档同步规则

当代码变更时，必须同步更新以下文档：

| 代码变更类型 | 必须更新的文档 |
|-------------|---------------|
| API 路径/参数变更 | `docs/API_ENDPOINTS.md` |
| 数据库模型变更 | `docs/DATABASE_SCHEMA.md` |
| 架构/流程变更 | `docs/ARCHITECTURE.md` |
| 发现新的陷阱 | `docs/KNOWN_PITFALLS.md` |
| 技术债务 | `docs/TECH_DEBT.md` |

**文档同步检查清单：** `docs/DOC_SYNC_CHECKLIST.md`

---

## 紧急情况处理

### 数据库迁移失败

```bash
# Django
find ./ -type d -name "migrations"|grep -v "venv" |xargs rm -rf
uv run python manage.py makemigrations oauth system --env dev
uv run python manage.py migrate --env dev
```

### Token 失效

- 清除浏览器 localStorage
- 重新登录

### Redis 连接失败

- Django/FastAPI 会自动降级到内存缓存
- 检查 Redis 服务状态：`redis-cli ping`

---

## 联系与支持

- **项目文档入口：** `docs/README.md`
- **架构设计：** `docs/ARCHITECTURE.md`
- **已知问题：** `docs/KNOWN_PITFALLS.md`
- **技术债务：** `docs/TECH_DEBT.md`

---

**最后更新：** 2026-03-23
**维护者：** DV-Admin Team
