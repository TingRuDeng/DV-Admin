# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [x] P1 串行：确认 `fastapi/uv.lock` 与 `fastapi/pyproject.toml` 匹配
- [x] P2 串行：解除全局 ignore 对 `fastapi/uv.lock` 的影响并纳入仓库
- [x] P3 串行：执行 FastAPI 锁文件与质量门禁验证
- [x] P4 串行：提交并创建 PR

并行判断：本轮聚焦依赖锁定和 CI 一致性，改动范围集中在 `.gitignore`、`fastapi/uv.lock` 和任务记录；验证必须按顺序确认锁文件、安装、FastAPI 门禁和文档校验，因此串行推进。

## 已完成摘要

- [x] 项目上下文文档升级：补齐 `docs/README.md`、`docs/AI_CONTEXT.md` 与 `scripts/validate_docs.py` 校验入口。
- [x] 产品化治理 P0-P3：共享 API 契约、关键前端测试、WebSocket 管理器、后端门禁、request id/health、文档/API 契约校验已落地。
- [x] 前端类型治理 P4-P12：Token 刷新、API 请求泛型、Storage、WebSocket 定时器/注册表、全局路由/API、扩展字段、TagsView、Settings 类型边界已收口。
- [x] 深度审查 P0/P1：FastAPI 文件接口鉴权和上传边界、敏感日志排除、共享路由契约、前端权限空态、refresh token 请求体和通知默认值已修复。
- [x] 前端超大组件拆分：用户、角色、通知、菜单、字典、部门、设置、TagsView、MenuSearch、TextScroll、Profile、Dashboard、字典同步 demo 等拆分已合入。
- [x] 前端共享组件与测试收口：`tags-view-store` Promise resolve 边界、`TableSelect` 类型/行为测试、WebSocket STOMP helper、主题样式测试拆分和 CURD 兼容层复核已完成。

## Review 小结

本轮修复审查优先级前四项：FastAPI RBAC 权限码已对齐前端/Django 种子契约；通用文件上传已拒绝 SVG；Django 开发态媒体路由已脱离 Swagger 开关；Playwright 本地 smoke 已改为固定端口、禁止复用已有服务，并忽略本地 HTML 报告。验证已覆盖文档/API 契约、FastAPI `make quality`、Django ruff + pytest、前端 `pnpm run quality`、`pnpm run build` 和 `VITE_APP_PORT=9530 pnpm run test:e2e:smoke`。

本轮小范围治理已完成：FastAPI 测试数据库、同步 ASGI 客户端、权限种子已从 `conftest.py` 拆入专用夹具文件；Django 历史测试权限码已统一为 `system:permissions:*`；后端验证通过。

本轮进入 FastAPI 依赖锁定治理：`fastapi/uv.lock` 此前被全局 Git ignore 忽略，导致本地和 CI 依赖解析可能漂移；本轮将锁文件纳入仓库并补充验证记录。

FastAPI 依赖锁定治理已完成：`.gitignore` 已显式允许 `fastapi/uv.lock`，锁文件已纳入仓库；`uv lock --check`、`uv sync --locked --group dev`、`make quality`、文档校验、脚本编译和 diff 检查均通过。
