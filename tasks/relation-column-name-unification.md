# 关联表字段命名统一计划

## 目标

- 将 FastAPI 用户-角色关联表字段从 `user_id/role_id` 统一到 Django 字段 `users_id/roles_id`。
- 将 FastAPI 角色-权限关联表字段从 `role_id/permission_id` 统一到 Django 字段 `roles_id/permissions_id`。
- 让共享关联契约从“只约束 through 表名”扩展为“同时约束 through 表字段名”。
- 保持前端 API、权限码、JWT、用户角色关系和角色权限关系的业务语义不变。
- 明确已有 FastAPI 数据库的显式迁移边界，避免通过双字段兼容或静默 fallback 掩盖数据迁移风险。

## 非目标

- 本轮不修改 Django 模型，Django 两张关联表和字段已经是目标结构。
- 本轮不修改用户、角色、权限主表字段。
- 本轮不改变 `Users.roles` 或 `Roles.permissions` 的 API 字段语义。
- 本轮不处理字典项 `is_default/remark` 差异。
- 本轮不做生产数据库在线迁移脚本；如部署库已有旧 FastAPI 字段，必须另开迁移任务。
- 本轮不引入双字段读写、兼容视图或静默 fallback。

## 当前事实

- `docs/DATABASE_SCHEMA.md` 已移除关联表字段命名差异描述，并保留旧 FastAPI 字段显式迁移边界。
- `docs/DATABASE_SCHEMA.md` 的用户-角色关联表字段当前只按 Django 目标结构记录为 `users_id / roles_id`。
- `backend/drf_admin/apps/system/models.py::Roles.permissions` 由 Django 自动生成字段 `roles_id/permissions_id`。
- `backend/drf_admin/apps/system/models.py::Users.roles` 由 Django 自动生成字段 `users_id/roles_id`。
- `fastapi/app/db/models/system.py::Roles.permissions` 已统一为 `backward_key="roles_id"`、`forward_key="permissions_id"`。
- `fastapi/app/db/models/oauth.py::Users.roles` 已统一为 `backward_key="users_id"`、`forward_key="roles_id"`。
- `scripts/model_contracts.py::DjangoFastapiRelationContract` 已登记 Django/FastAPI through 表名和字段名。
- `fastapi/tests/test_import_django_model_contracts.py::test_fastapi_relation_through_tables_match_shared_contracts` 已验证 `relation_field.through/backward_key/forward_key`。

## 设计原则

- 先用 RED 测试锁定“共享关联表字段必须同名”的目标，再改 FastAPI ORM 和契约。
- 关联字段命名统一只触碰 ORM/契约/测试/文档层，不改变对外 API。
- 不通过双字段读写、兼容查询或静默迁移规避真实数据库结构差异。
- 每次只处理两张 M2M through 表的字段名，不混入字典项字段、主表或权限业务逻辑。
- 已有旧 FastAPI 数据库需要显式迁移，代码只表达新的目标结构。

## 决策驱动因素

- 长期可维护性：表名已统一后，字段名继续不一致会让 Django/FastAPI 共用数据库和数据迁移仍然复杂。
- 数据安全：直接改 M2M `backward_key/forward_key` 后，旧 FastAPI 数据库里的关联字段不会自动迁移。
- 验证可行性：现有模型契约测试和运行时 M2M 测试已经覆盖角色权限、用户角色和 fixture 导入链路。
- 发布风险：关联字段错误会影响登录权限、角色授权、用户角色关系和菜单权限判断，必须用运行时目标测试覆盖。

## 方案对比

### 方案 A：继续只记录字段差异

- 做法：保留 FastAPI `user_id/role_id/permission_id` 字段，只在文档中说明差异。
- 优点：零迁移风险。
- 缺点：表名统一后的数据库仍不能真正贴近 Django 结构，迁移和排障还要长期区分字段名。

### 方案 B：直接将 FastAPI M2M 字段统一到 Django 命名

- 做法：修改 FastAPI 两个 `ManyToManyField` 的 `backward_key/forward_key`，扩展共享关联契约并同步测试与文档。
- 优点：直接消除关联表字段命名差异，和上轮 through 表名统一形成完整闭环。
- 缺点：已有 FastAPI 数据库需要显式迁移旧字段，否则用户角色和角色权限关系会读不到。

### 方案 C：新增双字段兼容层

- 做法：FastAPI 同时兼容旧字段和 Django 命名字段。
- 优点：短期迁移看起来平滑。
- 缺点：会带来双写一致性、读优先级和回滚语义问题，属于长期复杂 fallback。

## 推荐方案

推荐方案 B。

本轮通过测试和契约把 FastAPI M2M through 字段改为 Django 命名，并在文档里明确迁移边界。旧 FastAPI 数据库如果已有 `user_id/role_id/permission_id` 字段，应在部署迁移中显式重命名或复制数据到目标字段，不在业务代码中增加双字段静默兼容。

## 执行计划

- [x] P1 串行：RED 扩展共享关联契约字段名测试，复现两张 M2M through 表字段仍不一致。
- [x] P2 串行：GREEN 修改 `scripts/model_contracts.py::DjangoFastapiRelationContract`，登记 Django/FastAPI through 字段名。
- [x] P3 串行：GREEN 修改 FastAPI `Roles.permissions` 和 `Users.roles` 的 `backward_key/forward_key`。
- [x] P4 串行：执行并修正 FastAPI M2M 目标测试，覆盖角色权限分配、用户角色关系、Django fixture 导入和运行时权限链路。
- [x] P5 串行：同步数据库文档、技术债和字典模型治理计划，移除关联表字段命名差异描述，保留显式迁移边界说明。
- [x] P6 串行：执行模型契约校验、FastAPI 目标测试、FastAPI `make quality`、Django 目标测试和根目录校验。
- [ ] P7 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `fastapi/app/db/models/system.py`
- `fastapi/app/db/models/oauth.py`
- `scripts/model_contracts.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_import_django_data.py`
- `fastapi/tests/test_import_django_data_golden.py`
- `fastapi/tests/runtime_api_contracts/test_write_contracts.py`
- `fastapi/tests/test_role_service.py`
- `fastapi/tests/test_role_service_more.py`
- `fastapi/tests/test_user_service.py`
- `backend/drf_admin/utils/test_model_contracts.py`
- `docs/DATABASE_SCHEMA.md`
- `docs/TECH_DEBT.md`
- `tasks/dict-model-unification.md`
- `tasks/todo.md`

## 验证矩阵

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q`
- FastAPI 目标：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/runtime_api_contracts/test_write_contracts.py tests/test_role_service.py tests/test_role_service_more.py tests/test_user_service.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- Django 目标：`cd backend && uv run pytest drf_admin/utils/test_model_contracts.py -q`
- 根目录：`python3 scripts/validate_model_contracts.py .`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 根目录：`python3 scripts/validate_route_components.py .`
- 根目录：`python3 scripts/validate_django_migrations.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- FastAPI 测试库初始化如果仍按旧字段名建 through 表，目标测试会暴露角色权限或用户角色关系读写失败。
- Django fixture 导入如果隐式依赖旧 FastAPI 字段名，golden fixture 导入测试会失败。
- 运行时权限链路如果缺少角色权限关系，登录后的菜单、按钮权限和 RBAC 判断会出现回归。
- 已有 FastAPI 本地 SQLite/MySQL 数据不会随 ORM 字段名自动迁移；这不是本轮用 fallback 掩盖的问题，必须通过显式迁移处理。

## HARD-GATE

用户确认前，不进行任何业务代码、测试代码或契约代码修改。本文件只是规划草案。

## 进度记录

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q` 首次失败于共享关联契约缺少字段名入口，补齐契约字段后继续失败于 FastAPI ORM 仍使用 `role_id`，符合预期。
- GREEN：FastAPI `Roles.permissions` 和 `Users.roles` 的 `backward_key/forward_key` 已统一到 Django 命名，共享关联契约已同步；模型契约测试通过（13 passed）。
- 目标验证：FastAPI M2M 目标测试通过（112 passed），覆盖 Django fixture 导入、golden fixture、运行时写接口、角色服务和用户服务。
- 全量验证：FastAPI `make quality` 通过（534 passed，覆盖率 84.74%）；Django 模型契约测试通过（4 passed）；根目录模型/API/文档/路由组件/Django 迁移校验和 `git diff --check` 均通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只统一 FastAPI 两张 M2M through 表字段名和共享关联契约，不修改 Django 模型、主表、前端 API、权限码或业务响应；安全检查未发现新增 secret、mock、双字段读写或静默 fallback；复杂度检查通过，本轮扩展一个目标契约测试并修改两个 M2M key 常量，未新增超长函数；Document-refresh: needed，原因：数据库关联字段事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧字段 `user_id/role_id/permission_id`，需要显式迁移到 Django 命名字段，且字典项字段差异仍需后续独立治理。
