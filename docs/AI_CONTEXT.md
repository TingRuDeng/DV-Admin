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
    - "docs/ADR-0001-FRONTEND-MODERNIZATION.md"
    - "docs/API_ENDPOINTS.md"
    - "docs/DATABASE_SCHEMA.md"
    - "frontend/package.json"
    - "backend/pyproject.toml"
    - "fastapi/pyproject.toml"
    - "scripts/validate_api_contracts.py"
    - "scripts/api_route_coverage_validation.py"
    - "scripts/validate_django_migrations.py"
    - "fastapi/scripts/validate_migrations.py"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/validate_api_contracts.py ."
    - "python3 scripts/validate_django_migrations.py ."
    - "python3 -m py_compile scripts/validate_docs.py scripts/validate_api_contracts.py scripts/api_route_coverage_validation.py scripts/validate_django_migrations.py"
  stale_when:
    - "项目技术栈、目录结构、端口或质量门禁变化"
    - "Django/FastAPI 替代关系、API 契约或文档入口变化"
    - "前端现代化 ADR 状态、实施阶段或壳层边界变化"
---
# AI Context

> DV-Admin 是 Vue 前端加 Django/FastAPI 双后端替代实现仓库；本文件只做短上下文路由，不替代源码和权威文档。

## Project Snapshot

- 项目形态：前后端分离的管理后台，前端统一接入一个选中的后端实现。
- 前端技术栈：Vue 3、TypeScript、Element Plus、Vite 8、Pinia、Vue Router 5；ADR-0001 七阶段已完成并停止批量页面迁移，后续特殊页只按明确问题逐页处理。
- 后端实现：`backend/` 是 Django/DRF；`fastapi/` 是 FastAPI/Tortoise ORM；二者是同域替代实现。
- 本仓库不是 Android 项目；未检测到 Gradle、AndroidManifest 或 Android 插件信号，因此使用 generic profile。

## Core Directories

- `frontend/src/`：前端页面、组件、路由、状态管理、请求封装和样式治理入口。
- `backend/drf_admin/`：Django 后端应用、设置、中间件、认证、权限和系统模块。
- `fastapi/app/`：FastAPI 后端 API、模型、schema、配置、异常与响应包裹。
- `docs/`：项目文档导航、架构、API、数据库、坑点、债务和上下文索引。
- `scripts/validate_docs.py`：project-context-bootstrap 上下文包校验脚本。
- `scripts/validate_api_contracts.py`：共享 API 契约入口、测试和文档同步校验脚本。
- `scripts/api_route_coverage_validation.py`：关键端点 `method + path` 到 Django/FastAPI 路由的静态覆盖校验脚本。
- `scripts/real_backend_playwright.py`：复用同一份 Playwright 用例连接 Django LiveServer 或 FastAPI Uvicorn 的真实浏览器 smoke 入口。
- `scripts/validate_django_migrations.py`：Django 迁移链跟踪校验脚本。
- `fastapi/scripts/validate_migrations.py`：FastAPI 空库、带既有数据的增量升级、迁移基线接管、模型漂移和数据库 smoke 校验脚本。

## Documentation Map

- `AGENTS.md`：代理工作规则、分支约束、质量门禁和文档同步要求。
- `docs/README.md`：文档导航入口与任务阅读路径。
- `docs/ARCHITECTURE.md`：系统架构、双后端替代关系、前端路由与缓存约定。
- `docs/ADR-0001-FRONTEND-MODERNIZATION.md`：前端现代化的已接受决策、兼容边界、后果与停止条件。
- `docs/FRONTEND_OPTIMIZATION_BACKLOG.md`：ADR-0001 七个串行阶段、状态和验收证据的唯一跟踪入口。
- `docs/API_ENDPOINTS.md`：核心 API 契约、认证接口和双后端差异。
- `docs/DATABASE_SCHEMA.md`：核心模型、表名差异和迁移边界。
- `docs/KNOWN_PITFALLS.md`：已验证陷阱和排查路径。
- `docs/TECH_DEBT.md`：已确认技术债务和治理范围。

## Common Task Reading Paths

- 前端页面或交互：`AGENTS.md` -> `docs/README.md` -> `docs/ARCHITECTURE.md` -> `frontend/README.md` -> 目标模块。
- 前端现代化：`docs/ARCHITECTURE.md` -> `docs/ADR-0001-FRONTEND-MODERNIZATION.md` -> `docs/FRONTEND_OPTIMIZATION_BACKLOG.md` -> 当前实现。
- Django 后端：`AGENTS.md` -> `docs/README.md` -> `backend/README.md` -> `docs/API_ENDPOINTS.md` 或 `docs/DATABASE_SCHEMA.md` -> 目标代码。
- FastAPI 后端：`AGENTS.md` -> `docs/README.md` -> `fastapi/README.md` -> `docs/API_ENDPOINTS.md` 或 `docs/DATABASE_SCHEMA.md` -> 目标代码。
- 文档上下文包：`docs/README.md` -> `docs/AI_CONTEXT.md` -> `scripts/validate_docs.py`。
- API 契约治理：`docs/API_ENDPOINTS.md` -> `scripts/api_contracts.py` -> `scripts/api_endpoint_contracts.py` -> `scripts/api_route_coverage_validation.py` -> Django/FastAPI/前端契约测试。

## High-Risk Areas

- 不要把 `backend/` 与 `fastapi/` 理解成同一请求链路的上下游服务；本地联调通常二选一。
- 共享 API、分页、认证和错误响应变化需要同时核对前端、Django 和 FastAPI。
- 共享响应或关键端点契约变化必须同步 `scripts/api_contracts.py`、`scripts/api_endpoint_contracts.py`、`scripts/validate_api_contracts.py` 和三端契约测试。
- 新增 FastAPI 路由文件或移动路由装饰器时，必须同步 `scripts/api_route_coverage_validation.py` 的路由文件清单，避免关键端点逃逸 `method + path` 覆盖校验。
- Django 模型变化必须提交完整 migration 链，并运行 `scripts/validate_django_migrations.py`。
- FastAPI 模型变化必须提交 `app/db/migrations/` 版本化迁移，并运行 `make -C fastapi migration-check`；生产环境不得用 `generate_schemas()` 替代迁移，必须通过一次性迁移容器或单例 Job 成功迁移后再启动 API。
- 前端 Vite 端口来自 `frontend/.env.development`，Playwright 或脚本端口不能凭默认值推断。
- 双后端可替换性同时由静态契约、各后端真实 HTTP 测试和无 API Mock 的双后端 Playwright smoke 证明；普通 Mock E2E 不能替代真实栈门禁。
- 页面层 ProTable、RouteMeta、KeepAlive 缓存键已有治理约束，改动前先读架构文档。
- 前端现代化不得顺带修改双后端菜单字段、组件路径、共享 API、JWT/Pinia/字典/WebSocket/Pro 组件协议；触发 ADR 停止条件时重新评审。

## Validation Commands

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 scripts/validate_api_contracts.py .`
- quick: `python3 scripts/validate_django_migrations.py .`
- quick: `make -C fastapi migration-check`
- quick: `python3 -m py_compile scripts/validate_docs.py scripts/api_contracts.py scripts/api_endpoint_contracts.py scripts/api_route_coverage_validation.py scripts/validate_api_contracts.py scripts/validate_django_migrations.py`
- full: `pnpm --dir frontend run quality`
- full: `cd backend && uv run ruff check .`
- full: `cd backend && uv run pytest`
- full: `make -C fastapi quality`

## Stale when

- 技术栈、目录结构、默认端口或质量门禁变化。
- API 契约、模型关系、鉴权流程或双后端替代关系变化。
- 新增或迁移权威文档入口。
- ADR-0001 状态、现代化阶段、壳层/业务核心边界或性能停止条件变化。
