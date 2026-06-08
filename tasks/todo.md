# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [x] P1 串行：新增 `fastapi/tests/test_import_django_model_contracts.py` 补共享模型契约目录缺失的失败测试
- [x] P2 串行：新增 `scripts/model_contracts.py`，集中声明 Django → FastAPI 模型、表名和字段映射
- [x] P3 串行：新增 `scripts/validate_model_contracts.py` 并纳入文档/契约验证记录
- [x] P4 串行：同步模型差异治理记录并执行 FastAPI、文档和根目录验证

并行判断：本轮会触达 FastAPI 导入映射测试、共享模型契约脚本、根目录校验脚本和技术债记录；这些文件围绕同一 Django → FastAPI 模型映射，存在强顺序依赖，为避免契约目录和真实导入脚本错位，采用串行推进。

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

本轮进入 Django fixture 导入 fail-fast 治理：`fastapi/app/db/import_django_data.py` 原先在 fixture 缺失、单条导入失败、FK/M2M 失败时会打印后继续，存在误报成功风险；本轮新增 fail-fast 测试并把导入流程拆成小 helper，确保关键失败抛出 `DjangoDataImportError`。

Django fixture 导入 fail-fast 治理已完成：缺少 fixture、单条导入失败、M2M 目标缺失三类失败测试已覆盖；`make quality` 通过（505 passed，覆盖率 83.41%），文档校验、API 契约校验、脚本编译和 `git diff --check` 均通过。

本轮进入运行时 API 契约抽样治理：新增 FastAPI 运行时抽样测试，复用 `scripts/api_endpoint_contracts.py` 中的关键端点目录校验认证信息、动态路由、用户/菜单/字典/字典项分页和文件上传删除闭环；同时修正 FastAPI 用户、字典和字典项分页路由，使其真实接受前端契约参数 `pageSize`。目标验证通过：`python3 scripts/validate_api_contracts.py .` 和 `uv run pytest tests/test_runtime_api_contracts.py -q`。

本轮进入 Django fixture 导入 golden 测试治理：新增小型 golden fixture，覆盖部门自关联、权限菜单自关联、字典/字典项外键、角色权限 M2M、用户部门 FK 和用户角色 M2M，确保导入链路不只 fail-fast，也能长期验证完整映射结果。

Django fixture 导入 golden 测试治理已完成：`uv run pytest tests/test_import_django_data_golden.py tests/test_import_django_data.py tests/test_import_django_data_fail_fast.py -q` 通过（22 passed），FastAPI `make quality` 通过（511 passed，覆盖率 84.06%），文档/API 契约校验、脚本编译和 `git diff --check` 均通过。

本轮动态路由组件契约治理已完成：前端动态路由解析缺失组件时改为显式抛错，不再静默落到 404；新增 `scripts/validate_route_components.py` 校验 FastAPI 测试权限种子、golden fixture 和 Django 初始化数据中默认角色可访问菜单组件必须存在于 `frontend/src/views`；CI 质量门禁已接入该校验。验证通过：前端 `pnpm run quality`（64 files / 166 tests）、前端 `pnpm run build`、FastAPI `make quality`（511 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 默认密码配置治理已完成：`Settings.default_password` 已移除代码默认弱口令，`DEFAULT_PASSWORD` 必须由环境变量或 `.env` 显式提供；`.env.example` 改为非弱占位值，用户新增/重置密码接口说明和技术债统计已同步。验证通过：`uv run pytest tests/test_config.py -q`（15 passed）、FastAPI `make quality`（512 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django 运行时 API 契约抽样治理已完成：新增 Django 关键读端点运行时抽样，复用共享端点目录校验认证信息、动态路由、用户/菜单/字典/字典项分页响应；RED 阶段暴露 `dictCode` 未真实过滤字典项，已通过 `DictItemsFilter` 显式映射到 `dict__dict_code` 修复，并把 Django 运行时测试纳入 `scripts/validate_api_contracts.py` 必备入口。验证通过：Django 目标测试（10 passed）、Django `uv run ruff check .`、Django `uv run pytest`（83 passed）、FastAPI 契约对照测试（6 passed）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮前端错误响应边界治理已完成：新增 `normalizeApiErrorEnvelope` 统一错误信封，`request.ts` 改为只消费归一化后的错误结果；FastAPI 参数校验明细 `data.errors[].message` 已优先展示，避免只显示泛化错误；前端 API 契约测试和 `scripts/validate_api_contracts.py` 已纳入该入口。验证通过：前端目标测试（11 passed）、`pnpm run quality`（64 files / 168 tests）、`pnpm run build`、Django/FastAPI 契约目标测试（各 6 passed）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django/FastAPI 模型差异契约治理已完成：新增 `scripts/model_contracts.py` 集中声明 Django → FastAPI 模型、表名和字段映射；新增 `scripts/validate_model_contracts.py` 并纳入 CI 文档校验阶段；FastAPI 导入契约测试开始对照共享模型契约，权限菜单 `keepAlive/alwaysShow` 映射已显式补齐。验证通过：模型契约校验、FastAPI 导入目标测试（23 passed）、FastAPI `make quality`（513 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。
