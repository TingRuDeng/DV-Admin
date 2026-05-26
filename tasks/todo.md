# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [x] P1 串行：修复 FastAPI RBAC 权限码漂移，补权限契约测试
- [x] P2 串行：禁止 FastAPI 通用上传 SVG，补上传安全测试
- [x] P3 串行：修复 Django 本地媒体路由与 Swagger 开关耦合，补 URLConf 测试
- [x] P4 串行：修复 Playwright 本地端口复用误测，并忽略本地报告目录
- [x] P5 串行：执行最小充分验证并补 Review 小结

并行判断：本轮改动涉及测试夹具、FastAPI 路由、Django URLConf、前端 E2E 配置和 `.gitignore`，文件间没有直接写冲突，但业务意图存在顺序依赖；按用户要求“按顺序处理”，本轮串行推进，不使用 subagent。

验证命令：
- `cd fastapi && uv run pytest tests/test_menus.py tests/test_dict_items.py tests/test_users.py tests/test_files.py`
- `cd backend && uv run pytest drf_admin/apps/system/test_media_urls.py`
- `cd frontend && VITE_APP_PORT=9530 pnpm run test:e2e:smoke`
- `python3 scripts/validate_docs.py . --profile generic && python3 scripts/validate_api_contracts.py .`
- `cd fastapi && make quality`
- `cd backend && uv run ruff check . && perl -e 'alarm shift; exec @ARGV' 60 uv run pytest`
- `cd frontend && pnpm run quality && pnpm run build`

## 已完成摘要

- [x] 项目上下文文档升级：补齐 `docs/README.md`、`docs/AI_CONTEXT.md` 与 `scripts/validate_docs.py` 校验入口。
- [x] 产品化治理 P0-P3：共享 API 契约、关键前端测试、WebSocket 管理器、后端门禁、request id/health、文档/API 契约校验已落地。
- [x] 前端类型治理 P4-P12：Token 刷新、API 请求泛型、Storage、WebSocket 定时器/注册表、全局路由/API、扩展字段、TagsView、Settings 类型边界已收口。
- [x] 深度审查 P0/P1：FastAPI 文件接口鉴权和上传边界、敏感日志排除、共享路由契约、前端权限空态、refresh token 请求体和通知默认值已修复。
- [x] 前端超大组件拆分：用户、角色、通知、菜单、字典、部门、设置、TagsView、MenuSearch、TextScroll、Profile、Dashboard、字典同步 demo 等拆分已合入。
- [x] 前端共享组件与测试收口：`tags-view-store` Promise resolve 边界、`TableSelect` 类型/行为测试、WebSocket STOMP helper、主题样式测试拆分和 CURD 兼容层复核已完成。

## Review 小结

本轮修复审查优先级前四项：FastAPI RBAC 权限码已对齐前端/Django 种子契约；通用文件上传已拒绝 SVG；Django 开发态媒体路由已脱离 Swagger 开关；Playwright 本地 smoke 已改为固定端口、禁止复用已有服务，并忽略本地 HTML 报告。验证已覆盖文档/API 契约、FastAPI `make quality`、Django ruff + pytest、前端 `pnpm run quality`、`pnpm run build` 和 `VITE_APP_PORT=9530 pnpm run test:e2e:smoke`。

当前主线无未完成执行计划；后续新任务按 `AGENTS.md` 要求重新写入活跃计划和验证结果。
