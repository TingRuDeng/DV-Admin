# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [x] P1 串行：补 FastAPI 文件上传 / 删除契约失败测试
- [x] P2 串行：实现文件相对路径返回、归属校验和安全删除
- [x] P3 串行：同步前端 `FileInfo` / 上传组件删除参数
- [x] P4 串行：同步文件接口文档和契约校验
- [x] P5 串行：修复本地 Playwright 报告污染前端 quality
- [x] P6 串行：执行最小充分验证并完成 review gate
- [x] P1 串行：补 Django/FastAPI 端点契约目录失败测试
- [x] P2 串行：新增关键端点契约目录并保留共享入口
- [x] P3 串行：扩展 `scripts/validate_api_contracts.py` 校验证据文件
- [x] P4 串行：同步 API、架构上下文和任务状态文档
- [x] P5 串行：执行最小充分验证并完成 review gate

并行判断：前两轮改动分别集中在文件上传 / 删除契约链路和双后端关键端点契约目录；两者都会修改 API 文档、契约校验和任务状态，因此在汇总分支中按提交顺序串行整合。

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

本轮文件上传 / 删除契约治理已完成：FastAPI 上传响应新增 `path` 并按 `files/{user_id}` 隔离保存；删除接口改为只接受上传返回的相对路径，并校验目录边界与用户归属；前端文件上传和多图上传删除时改传 `path`，缺少路径时显式提示；文件接口文档、契约校验和 Playwright 报告的 Prettier ignore 治理已同步。验证通过：FastAPI `make quality`（504 passed，覆盖率 81.23%）、前端 `pnpm run quality`（64 files / 165 tests）、前端 `pnpm run build`、文档/API 契约校验和 `git diff --check`。

本轮进入双后端关键端点契约治理：新增 `scripts/api_endpoint_contracts.py` 作为关键端点契约目录，覆盖认证、用户、菜单、字典、字典项和文件接口的路径、方法、权限、分页和关键字段；Django/FastAPI 契约测试已开始共同断言该目录，`scripts/validate_api_contracts.py` 会校验证据文件中的路径、权限和调用片段，避免契约目录脱离真实代码。

双后端关键端点契约治理第一轮已完成：文档校验、API 契约校验、脚本编译、Django/FastAPI 目标契约测试、ruff 和 `git diff --check` 均通过；本轮未启动后端服务做运行时双实现对比，后续如继续推进应以该目录为输入补运行时采样契约测试。
