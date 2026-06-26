# 拆分 FastAPI 用户写接口 OpenAPI 文案

## 目标

- 将 `fastapi/app/api/v1/system/user_routes/mutation.py` 中的大段 OpenAPI `description` 和 `responses` 拆入专用模块。
- 保持用户创建、更新、局部更新、单删和批量删除路由函数、权限声明、路径和响应模型不变。
- 降低用户写接口路由文件行数和文案噪声，让路由文件回到“路由声明 + 调用服务”的职责。

## 非目标

- 不修改用户写接口路径、方法、权限码、请求体或响应格式。
- 不修改 `user_service` 的业务逻辑。
- 不修改前端 API 调用或双后端契约目录。
- 不新增 fallback、mock 或静默兼容路径。

## 当前事实

- `fastapi/app/api/v1/system/user_routes/mutation.py` 当前为 286 行，主要体量来自 create、patch、delete、batch delete 的 OpenAPI 长文案和示例响应。
- `scripts/api_endpoint_contracts.py` 对用户写接口的 FastAPI 证据仍要求 `mutation.py` 中存在 `@router.post`、`@router.put`、`@router.delete` 和权限码片段。
- 运行时契约测试已覆盖 `users_create`、`users_update`、`users_delete`。

## 方案对比

- 方案 A：按 create/update/delete 拆成多个路由文件。可以明显降行数，但会影响契约证据路径和聚合入口，改动面偏大。
- 方案 B：只拆 OpenAPI 文案和响应示例到 `mutation_docs.py`。路由路径、权限和函数保留原文件，行为风险最小。

## 推荐方案

采用方案 B。它能解决当前文件的主要体量来源，同时不改变 API 行为、契约证据路径和服务调用链。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/api/v1/system/user_routes/mutation_docs.py`，承接 create、partial update、delete、batch delete 的 description 和 responses 常量。
- [x] P2 串行：更新 `mutation.py` 引用文案常量，保持所有路由函数、权限声明和服务调用不变。
- [x] P3 串行：运行用户写接口目标测试、契约校验、FastAPI 全量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/runtime_api_contracts/test_write_contracts.py tests/test_api_contracts.py tests/test_users.py tests/test_user_service_mutation.py tests/test_user_service_delete_password.py -q`
- `cd fastapi && uv run ruff check app/api/v1/system/user_routes/mutation.py app/api/v1/system/user_routes/mutation_docs.py`
- `python3 scripts/validate_api_contracts.py .`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
- `wc -l fastapi/app/api/v1/system/user_routes/mutation.py fastapi/app/api/v1/system/user_routes/mutation_docs.py`

## 进度记录

- [x] 已确认当前分支为 `codex/split-user-mutation-docs`，从最新 `master` 创建。
- [x] 已读取 `mutation.py`、相邻用户路由和用户写接口契约测试。
- [x] 已将用户写接口长 OpenAPI 文案和响应示例拆入 `mutation_docs.py`。

## 验证结果

- `cd fastapi && uv run pytest tests/runtime_api_contracts/test_write_contracts.py tests/test_api_contracts.py tests/test_users.py tests/test_user_service_mutation.py tests/test_user_service_delete_password.py -q`：32 passed。
- `cd fastapi && uv run ruff check app/api/v1/system/user_routes/mutation.py app/api/v1/system/user_routes/mutation_docs.py`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `wc -l fastapi/app/api/v1/system/user_routes/mutation.py fastapi/app/api/v1/system/user_routes/mutation_docs.py`：`mutation.py` 为 91 行，`mutation_docs.py` 为 222 行。
- `cd fastapi && make quality`：通过，554 passed，覆盖率 87.32%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只将用户写接口 OpenAPI 文案和响应示例拆入 `mutation_docs.py`，路由函数、权限声明、路径、响应模型和服务调用保持不变；安全检查未发现新增 secret、mock、fallback 或静默降级；测试与验证已覆盖用户写接口运行时契约、FastAPI 全量质量门禁、API 契约校验、文档校验、脚本编译、diff 检查和行数边界；复杂度检查通过，`mutation.py` 从 286 行降至 91 行，新增文案模块 226 行；Document-refresh: not-needed，原因：本轮只调整内部路由文案组织，不改变对外 API、数据库结构或用户可见行为；剩余风险是文案模块仍承载较多 OpenAPI 示例，后续若继续扩展用户写接口文档，应优先按接口类型继续拆分文案常量。
