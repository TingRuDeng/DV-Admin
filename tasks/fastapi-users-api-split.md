# FastAPI 用户 API 拆分治理计划

## 目标

- 将 `fastapi/app/api/v1/system/users.py` 从 720 行混合路由文件拆分为按职责组织的小模块。
- 保持 `from app.api.v1.system.users import router` 兼容入口不变，避免影响系统总路由和契约脚本证据路径。
- 不改变 URL 路径、HTTP 方法、权限码、请求参数、响应模型或业务行为。

## 非目标

- 不修改 `user_service` 业务逻辑。
- 不调整前端 API 调用、Django 后端接口或共享 API 契约。
- 不清理已有 OpenAPI 长描述文本；本轮只移动端点定义。

## 当前事实

- `fastapi/app/api/v1/system/users.py` 当前 720 行，包含用户分页、选项、详情、创建、更新、局部更新、删除、批量删除、密码重置、模板、导出和导入端点。
- `fastapi/app/api/v1/system/__init__.py` 只从 `app.api.v1.system.users` 导入 `router` 并挂载到 `/system/users`。
- `scripts/api_endpoint_contracts.py` 的用户契约证据仍指向 `fastapi/app/api/v1/system/users.py`，因此本轮需要保留该文件作为聚合入口。
- 相关接口测试集中在 `fastapi/tests/test_users.py` 和导入导出测试 `fastapi/tests/test_user_import.py`；服务层测试在 `fastapi/tests/test_user_service.py`。

## 决策日志

- 方案 A：新增 `fastapi/app/api/v1/system/user_routes/`，按查询、写操作、密码重置、导入导出拆分子 router，再由 `users.py` include 子 router。
  - 优点：外部导入入口不变，路由职责清晰，`users.py` 可收缩为聚合入口。
  - 缺点：需要确认子 router include 顺序不改变路径匹配。
- 方案 B：直接把 `users.py` 改名为包目录 `users/`。
  - 优点：命名更自然。
  - 缺点：同路径文件到目录迁移影响更大，契约脚本和历史引用更容易受影响。
- 方案 C：只删除 OpenAPI 长描述，保留所有函数在同一文件。
  - 优点：改动最小。
  - 缺点：不能解决路由职责混杂，后续用户接口变更仍集中冲突。

推荐方案：采用方案 A。它保留兼容入口，拆分粒度与端点职责一致，影响范围最小。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `user_routes/query.py`，迁移列表、选项和详情端点。
- [x] P3 串行：新增 `user_routes/mutation.py`，迁移创建、更新、局部更新、删除和批量删除端点。
- [x] P4 串行：新增 `user_routes/password.py`，迁移密码重置端点。
- [x] P5 串行：新增 `user_routes/import_export.py`，迁移模板、导出和导入端点。
- [x] P6 串行：将 `users.py` 收缩为兼容聚合入口，并保持子 router 挂载顺序稳定。
- [x] P7 串行：执行用户 API 目标测试、API 契约校验、FastAPI 质量门禁、文档校验和 diff 检查。
- [x] P8 串行：执行 review-gate。
- [ ] P9 串行：提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_users.py tests/test_user_import.py -q`
- `python3 scripts/validate_api_contracts.py .`
- `python3 scripts/validate_docs.py . --profile generic`
- `cd fastapi && make quality`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分 FastAPI 用户 API 内部文件结构，并保留 `from app.api.v1.system.users import router` 兼容入口；不改变 URL 路径、HTTP 方法、权限码、请求参数、响应模型或业务行为。安全检查未发现本轮新增 secret、mock、fallback 或静默降级，敏感词扫描命中仅来自 `DEFAULT_PASSWORD` 接口说明和 `tasks/todo.md` 历史摘要。测试与验证通过：用户目标测试与权限契约测试 7 passed；FastAPI `make quality` 通过，539 passed，覆盖率 85.08%；`python3 scripts/validate_api_contracts.py .` 通过；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。复杂度检查通过，`users.py` 从 720 行收缩为 31 行兼容聚合入口，新增子路由文件均低于 300 行。Document-refresh: not-needed，原因：本轮是内部 API 文件结构拆分，不改变用户可见 API、数据库结构或产品文档事实。剩余风险是 FastAPI `auth.py` 和 `user_service.py` 仍为既有大文件，需要后续独立规划治理。
