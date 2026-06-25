# FastAPI 用户服务拆分治理计划

## 目标

- 将 `fastapi/app/services/system/user_service.py` 从 598 行单类服务拆分为按职责组织的小模块。
- 保持 `from app.services.system.user_service import user_service` 兼容入口不变，避免影响既有 API 路由和测试。
- 不改变用户查询、创建、更新、删除、密码重置、导入导出、序列化字段或错误语义。

## 非目标

- 不修改用户 API 路径、权限码、请求参数或响应模型。
- 不调整数据库模型、迁移、角色关联表或默认密码配置。
- 不拆分 `fastapi/tests/test_user_service.py`；测试拆分后续单独治理。
- 不重写 Excel 导入算法；本轮只按职责移动和轻量抽取。

## 当前事实

- `fastapi/app/services/system/user_service.py` 当前 598 行，集中承载缓存清理、分页查询、详情表单、CRUD、状态更新、密码重置、Excel 导入、模板生成、导出和用户序列化。
- `fastapi/app/api/v1/system/user_routes/query.py`、`mutation.py`、`password.py`、`import_export.py` 都只通过 `user_service` 实例调用服务方法。
- `fastapi/tests/test_user_service.py` 覆盖 `get_page/get/get_form/create/update/partial_update/delete/batch_delete/get_options/reset_password/import_users/get_import_template/export_users`。
- `fastapi/tests/test_user_import.py` 单独覆盖用户导入和模板入口。

## 决策日志

- 方案 A：保留 `user_service.py` 为兼容聚合入口，新增 `user_services/` 子包，按查询、写操作、导入导出、序列化和缓存 helper 拆分。
  - 优点：外部导入路径不变，职责边界清楚，便于后续继续拆测试。
  - 缺点：需要设计组合服务或多继承 mixin，避免调用链变复杂。
- 方案 B：直接把 `UserService` 拆成多个独立服务实例，并改 API 路由分别导入。
  - 优点：依赖更显式。
  - 缺点：影响所有用户 API 路由和测试导入，改动范围大，本轮收益不匹配风险。
- 方案 C：只抽导入导出 helper，`UserService` 仍保留大部分方法。
  - 优点：改动最小。
  - 缺点：无法解决查询、写操作、序列化和导入导出混在同一类里的长期维护问题。

推荐方案：采用方案 A。保留对外 `user_service` 入口，内部通过职责 mixin 或组合 helper 拆分，兼顾兼容性和维护性。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `user_services/cache.py`，迁移 `_clear_user_cache`。
- [x] P3 串行：新增 `user_services/serializers.py`，迁移 `_serialize_user`、`_serialize_user_optimized`、`_serialize_user_form`。
- [x] P4 串行：新增 `user_services/query.py`，迁移 `get_page`、`get`、`get_form`、`get_options`。
- [x] P5 串行：新增 `user_services/mutation.py`，迁移 `create`、`update`、`partial_update`、`delete`、`batch_delete`、`reset_password`。
- [x] P6 串行：新增 `user_services/import_export.py` 和 `user_services/import_parser.py`，迁移并拆分 `import_users`、`get_import_template`、`export_users`。
- [x] P7 串行：将 `user_service.py` 收缩为兼容聚合入口并保留 `UserService`、`user_service` 导出。
- [x] P8 串行：执行用户服务目标测试、用户导入测试、FastAPI 质量门禁和 diff 检查。
- [ ] P9 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_user_service.py tests/test_user_import.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 用户服务职责拆分已完成：`user_service.py` 保留 `UserService` 与 `user_service` 兼容入口，缓存、序列化、查询、写操作、导入导出和 Excel 导入解析已拆入 `user_services/` 子模块。验证通过：用户服务目标测试（34 passed）、FastAPI `make quality`（539 passed，覆盖率 85.44%）、文档校验和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮不改变用户 API 路由、权限码、请求参数、响应模型、数据库模型或默认密码配置；安全检查未发现新增 secret、mock、静默 fallback 或硬编码凭据；复杂度检查通过，`user_service.py` 已降至 16 行，新增文件均低于 300 行；Document-refresh: not-needed，原因：本轮只调整内部服务模块组织，不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/tests/test_user_service.py` 仍为 531 行，测试拆分需后续单独治理。
