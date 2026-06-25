# FastAPI 用户服务测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_user_service.py` 从 531 行单文件拆分为职责清晰的小测试文件。
- 保持所有测试断言、夹具语义和 `user_service` 入口不变。
- 所有新增测试文件低于 300 行，并避免重复定义用户、部门、角色夹具。

## 非目标

- 不修改 `app/services/system/user_service.py` 或 `user_services/` 运行时代码。
- 不改变用户服务业务断言、错误类型、错误文案或导入导出数据样例。
- 不合并或改写 `fastapi/tests/test_user_import.py`；它是独立导入链路测试。

## 当前事实

- `fastapi/tests/test_user_service.py` 当前 531 行，包含共享夹具和 10 个测试类。
- 共享夹具包括 `test_dept_for_service`、`test_role_for_service`、`test_user_for_service`。
- 查询相关测试类：`TestUserServiceGetPage`、`TestUserServiceGet`、`TestUserServiceGetForm`、`TestUserServiceGetOptions`。
- 写操作相关测试类：`TestUserServiceCreate`、`TestUserServiceUpdate`、`TestUserServicePartialUpdate`。
- 删除、密码和导入导出测试类：`TestUserServiceDelete`、`TestUserServiceBatchDelete`、`TestUserServiceResetPassword`、`TestUserServiceImportExport`。

## 决策日志

- 方案 A：拆出 `user_service_fixtures.py`，再按 query、mutation、delete、import_export 拆测试文件。
  - 优点：夹具集中复用，文件职责清楚，新增测试文件体量可控。
  - 缺点：需要通过 `pytest_plugins` 或显式导入保证夹具可见。
- 方案 B：每个测试文件重复定义夹具。
  - 优点：单文件自包含。
  - 缺点：重复较多，后续夹具调整容易漂移。
- 方案 C：只拆导入导出测试，其他继续留在原文件。
  - 优点：改动最小。
  - 缺点：不能解决 531 行测试文件的主要维护问题。

推荐方案：采用方案 A。使用 `pytest_plugins = ("tests.user_service_fixtures",)` 让拆分后的测试文件复用同一组夹具。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/user_service_fixtures.py`，迁移共享夹具。
- [x] P3 串行：新增 `fastapi/tests/test_user_service_query.py`，迁移分页、详情、表单和选项测试。
- [x] P4 串行：新增 `fastapi/tests/test_user_service_mutation.py`，迁移创建、更新和局部更新测试。
- [x] P5 串行：新增 `fastapi/tests/test_user_service_delete_password.py`，迁移删除、批量删除和密码重置测试。
- [x] P6 串行：新增 `fastapi/tests/test_user_service_import_export.py`，迁移模板、导出和导入测试。
- [x] P7 串行：删除原 `fastapi/tests/test_user_service.py`，确保没有重复测试或孤儿引用。
- [x] P8 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P9 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_user_service_query.py tests/test_user_service_mutation.py tests/test_user_service_delete_password.py tests/test_user_service_import_export.py tests/test_user_import.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 用户服务测试拆分已完成：共享夹具迁入 `user_service_fixtures.py`，原 531 行 `test_user_service.py` 已拆为查询、写操作、删除密码、导入导出 4 个测试文件，所有新增测试文件均低于 300 行。验证通过：目标测试（34 passed）、FastAPI `make quality`（539 passed，覆盖率 85.44%）、文档校验和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮只拆分测试文件和任务状态，不修改运行时代码、业务断言、错误类型、错误文案或导入导出样例；安全检查未发现新增 secret、mock 或静默 fallback；复杂度检查通过；Document-refresh: not-needed，原因：本轮只调整内部测试组织，不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/tests/test_cache.py` 仍为 521 行，后续应单独拆分。
