# AI Context

> DV-Admin 是一个前端 + 双后端替代实现仓库；本文件用于让代理在最短上下文内定位权威文档与证据入口。

## 权威文档地图

| 文档 | 角色 | 何时读取 |
|---|---|---|
| `AGENTS.md` | 主规则入口 | 任何会改动文件的任务开始前 |
| `docs/README.md` | 主导航入口 | 进入仓库后选择阅读路径时 |
| `docs/ARCHITECTURE.md` | 架构边界 | 涉及跨模块影响、鉴权、缓存、路由约束 |
| `docs/API_ENDPOINTS.md` | API 概要契约 | 新增/修改接口、联调前 |
| `docs/DATABASE_SCHEMA.md` | 模型与迁移边界 | 涉及模型字段、关系、迁移 |
| `docs/KNOWN_PITFALLS.md` | 已知陷阱 | 排查 bug、处理历史兼容问题 |
| `docs/TECH_DEBT.md` | 债务跟踪 | 规划迭代与范围裁剪 |
| `docs/DOC_SYNC_CHECKLIST.md` | 文档收尾门禁 | 提交前验收 |

## 任务读取路径

- 前端页面/交互任务：`AGENTS.md` -> `docs/README.md` -> `docs/ARCHITECTURE.md` -> `frontend/README.md` -> 目标模块代码。
- Django 后端任务：`AGENTS.md` -> `docs/README.md` -> `backend/README.md` -> `docs/API_ENDPOINTS.md` / `docs/DATABASE_SCHEMA.md` -> 目标代码。
- FastAPI 后端任务：`AGENTS.md` -> `docs/README.md` -> `fastapi/README.md` -> `docs/API_ENDPOINTS.md` / `docs/DATABASE_SCHEMA.md` -> 目标代码。
- 文档收尾：`docs/DOC_SYNC_CHECKLIST.md` -> `python3 scripts/validate_docs.py`。

## 关键证据入口

- 前端端口与代理：`frontend/.env.development`、`frontend/vite.config.ts`
- 前端请求封装与 API 版本注入：`frontend/src/utils/request.ts`
- RouteMeta 与缓存键收口：`frontend/src/utils/route-meta.ts`、`frontend/src/utils/view-cache.ts`、`frontend/src/store/modules/tags-view-store.ts`
- Django 响应与命名中间件：`backend/drf_admin/settings.py`、`backend/drf_admin/utils/middleware.py`
- Django OAuth 刷新令牌协议：`backend/drf_admin/apps/oauth/views/oauth.py`
- FastAPI 响应包裹与异常：`fastapi/app/schemas/base.py`、`fastapi/app/core/exceptions.py`
- FastAPI OAuth / 健康检查：`fastapi/app/api/v1/oauth/auth.py`、`fastapi/app/api/health.py`

## 高风险误读点

- `backend/` 与 `fastapi/` 是替代实现，不是同请求链路上下游服务。
- API 成功业务码目前以 `20000` 为主，但 Django/FastAPI 错误响应字段并不完全同形（`msg/errors` vs `message`）。
- 页面层 ProTable 已约束为 request 驱动；`CURD` 目录仅保留兼容层。
- Playwright 配置默认 `5173`，但前端 Vite 开发端口来自 `VITE_APP_PORT`（当前 `9527`）；执行 E2E 前需确认端口策略。

## Optional

- 历史资料：`docs/archive/README.md`、`后续优化/README.md`
- 启动提示模板：`docs/AGENT_STARTER_PROMPT.md`
