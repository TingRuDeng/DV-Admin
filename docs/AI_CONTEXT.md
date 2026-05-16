---
ai_summary:
  purpose: "为 AI 代理提供 DV-Admin 的短上下文地图、风险提示和校验入口。"
  read_when:
    - "进入仓库后需要快速判断任务阅读路径时"
    - "执行代码或文档改动前需要装配最小上下文时"
  source_of_truth:
    - "AGENTS.md"
    - "docs/README.md"
    - "docs/ARCHITECTURE.md"
    - "docs/API_ENDPOINTS.md"
    - "docs/DATABASE_SCHEMA.md"
    - "frontend/package.json"
    - "backend/pyproject.toml"
    - "fastapi/pyproject.toml"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 -m py_compile scripts/validate_docs.py"
  stale_when:
    - "项目技术栈、目录结构、端口或质量门禁变化"
    - "Django/FastAPI 替代关系、API 契约或文档入口变化"
---
# AI Context

> DV-Admin 是 Vue 前端加 Django/FastAPI 双后端替代实现仓库；本文件只做短上下文路由，不替代源码和权威文档。

## Project Snapshot

- 项目形态：前后端分离的管理后台，前端统一接入一个选中的后端实现。
- 前端技术栈：Vue 3、TypeScript、Element Plus、Vite 7、Pinia、Vue Router。
- 后端实现：`backend/` 是 Django/DRF；`fastapi/` 是 FastAPI/Tortoise ORM；二者是同域替代实现。
- 本仓库不是 Android 项目；未检测到 Gradle、AndroidManifest 或 Android 插件信号，因此使用 generic profile。

## Core Directories

- `frontend/src/`：前端页面、组件、路由、状态管理、请求封装和样式治理入口。
- `backend/drf_admin/`：Django 后端应用、设置、中间件、认证、权限和系统模块。
- `fastapi/app/`：FastAPI 后端 API、模型、schema、配置、异常与响应包裹。
- `docs/`：项目文档导航、架构、API、数据库、坑点、债务和上下文索引。
- `scripts/validate_docs.py`：project-context-bootstrap 上下文包校验脚本。

## Documentation Map

- `AGENTS.md`：代理工作规则、分支约束、质量门禁和文档同步要求。
- `docs/README.md`：文档导航入口与任务阅读路径。
- `docs/ARCHITECTURE.md`：系统架构、双后端替代关系、前端路由与缓存约定。
- `docs/API_ENDPOINTS.md`：核心 API 契约、认证接口和双后端差异。
- `docs/DATABASE_SCHEMA.md`：核心模型、表名差异和迁移边界。
- `docs/KNOWN_PITFALLS.md`：已验证陷阱和排查路径。
- `docs/TECH_DEBT.md`：已确认技术债务和治理范围。

## Common Task Reading Paths

- 前端页面或交互：`AGENTS.md` -> `docs/README.md` -> `docs/ARCHITECTURE.md` -> `frontend/README.md` -> 目标模块。
- Django 后端：`AGENTS.md` -> `docs/README.md` -> `backend/README.md` -> `docs/API_ENDPOINTS.md` 或 `docs/DATABASE_SCHEMA.md` -> 目标代码。
- FastAPI 后端：`AGENTS.md` -> `docs/README.md` -> `fastapi/README.md` -> `docs/API_ENDPOINTS.md` 或 `docs/DATABASE_SCHEMA.md` -> 目标代码。
- 文档上下文包：`docs/README.md` -> `docs/AI_CONTEXT.md` -> `scripts/validate_docs.py`。

## High-Risk Areas

- 不要把 `backend/` 与 `fastapi/` 理解成同一请求链路的上下游服务；本地联调通常二选一。
- 共享 API、分页、认证和错误响应变化需要同时核对前端、Django 和 FastAPI。
- 前端 Vite 端口来自 `frontend/.env.development`，Playwright 或脚本端口不能凭默认值推断。
- 页面层 ProTable、RouteMeta、KeepAlive 缓存键已有治理约束，改动前先读架构文档。

## Validation Commands

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 -m py_compile scripts/validate_docs.py`
- full: `pnpm --dir frontend run quality`
- full: `cd backend && uv run ruff check .`
- full: `cd backend && uv run pytest`
- full: `make -C fastapi quality`

## Stale when

- 技术栈、目录结构、默认端口或质量门禁变化。
- API 契约、模型关系、鉴权流程或双后端替代关系变化。
- 新增或迁移权威文档入口。
