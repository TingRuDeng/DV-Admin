# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [x] P1 串行：RED 更新 Playwright 治理测试，要求 smoke 覆盖部门管理 E2E
- [x] P2 串行：新增部门管理仅查询权限 E2E，验证新增、批量删除、行内新增、编辑、删除按钮被现有 `v-hasPerm` 移除
- [x] P3 串行：将部门管理 E2E 纳入 smoke 脚本，并确认治理测试转绿
- [x] P4 串行：执行目标 E2E、完整 smoke、前端质量和根目录必要校验
- [ ] P5 串行：同步任务状态、review-gate、提交、PR、CI 和合并

并行判断：本轮涉及治理测试、部门 E2E 和 smoke 脚本三处顺序依赖，且会连续修改 `frontend/package.json` 与 Playwright 治理测试；为保证 RED/GREEN 证据清晰，采用串行推进，不启用 subagent。

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

本轮 Django RBAC 权限边界契约治理已完成：新增 `backend/drf_admin/utils/test_rbac_permission_contract.py`，直接覆盖 `RBACPermission` 有权限放行、缺权限拒绝、无权限声明拒绝、白名单放行，并校验 `UsersViewSet` 自动生成的用户写操作权限码与共享端点契约一致。验证通过：目标测试（5 passed）、Django `uv run ruff check .`、Django `uv run pytest`（88 passed）、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django 用户写接口运行时契约治理已完成：`backend/drf_admin/utils/test_runtime_api_contracts.py` 已覆盖 `users_create/users_update/users_delete`，验证创建成功信封、更新落库和批量删除 `ids` 请求体契约；`scripts/validate_api_contracts.py` 已强制检查这些 Django 写接口运行时测试片段。验证通过：目标运行时契约测试（3 passed）、Django `uv run ruff check .`、Django `uv run pytest`（89 passed）、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

本轮错误码契约治理已完成：新增 `scripts/api_error_codes.py` 作为共享错误码契约目录，前端、Django、FastAPI 契约测试和 `scripts/validate_api_contracts.py` 已共同锁定 `40000/40001/40002` 的公共语义；FastAPI 登录失败、验证码失败已改为 `40000`，避免误触发前端 Access Token 刷新分支。验证通过：根目录文档/API/模型/路由组件契约校验、脚本编译、前端 `pnpm run quality`（64 files / 169 tests）、前端 `pnpm run build`、前端 `pnpm run test:e2e:smoke`（4 passed，沙箱监听失败后提权重跑通过）、Django `uv run ruff check .`、Django `uv run pytest`（90 passed）、FastAPI `make quality`（515 passed，覆盖率 83.76%）和 `git diff --check`。

本轮用户管理核心业务 E2E 已完成：新增 Playwright smoke 用例，使用显式 route mock 覆盖登录、动态路由、认证信息、部门、角色、用户列表和新增用户接口；`test:e2e:smoke` 已纳入该用例。验证通过：目标 E2E（1 passed）、完整 smoke E2E（5 passed）、前端 `pnpm run quality`（64 files / 170 tests）、前端 `pnpm run build`、根目录文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮 FastAPI 用户写接口运行时契约扩面已完成：`scripts/validate_api_contracts.py` 已把 `fastapi/tests/test_runtime_api_contracts.py` 纳入必备契约测试入口，并强制检查 `users_create/users_update/users_delete` 抽样片段；FastAPI 运行时测试已覆盖创建、更新、批量删除和删除后分页列表不可见。验证通过：RED 阶段契约校验失败符合预期，目标测试（3 passed）、`python3 scripts/validate_api_contracts.py .`、FastAPI `make quality`（516 passed，覆盖率 83.93%）、根目录文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮用户管理权限链路 E2E 已完成：`frontend/e2e/user-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增、批量删除、编辑、删除按钮会被 `v-hasPerm` 移除；认证 mock 支持按用例注入权限集合，未 mock 的接口继续返回 404 暴露遗漏。为避免本地 Playwright 登录 mock 并发竞争，`test:e2e:smoke` 改为 `--workers=1`，并由治理测试锁定。验证通过：RED 阶段受限权限仍显示新增按钮符合预期失败，目标 E2E（2 passed）、完整 smoke（6 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮角色管理权限链路 E2E 已完成：`frontend/e2e/role-management.spec.ts` 新增仅查询权限场景，RED 阶段确认 `新增角色` 仍可见；随后 `frontend/src/views/system/role/index.vue` 为新增、批量删除、分配权限、编辑、删除接入现有 `system:roles:*` 按钮权限码。`test:e2e:smoke` 已纳入角色管理用例，并由 Playwright 治理测试锁定。验证通过：目标 E2E（1 passed）、完整 smoke（7 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮菜单管理权限链路 E2E 已完成：`frontend/e2e/menu-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增菜单、新增、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入菜单管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/menu-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（8 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮文件上传 / 删除链路 E2E 已完成：`frontend/e2e/file-upload-delete.spec.ts` 新增浏览器级 smoke，用动态路由 mock 进入 demo 上传页，验证文件上传成功后删除请求使用后端返回的相对 `path`；`test:e2e:smoke` 已纳入该用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/file-upload-delete.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（9 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮部门管理权限链路 E2E 已完成：`frontend/e2e/dept-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增部门、批量删除、行内新增、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入部门管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/dept-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（10 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。
