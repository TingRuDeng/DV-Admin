# 关联表命名统一计划

## 目标

- 将 FastAPI 角色-权限关联表从 `system_roles_permissions` 统一到 Django 表名 `system_roles_to_system_permissions`。
- 将 FastAPI 用户-角色关联表从 `system_users_roles` 统一到 Django 表名 `system_users_to_system_roles`。
- 让共享关联表契约从“登记 through 表差异”转为“约束 Django/FastAPI through 表一致”。
- 保持前端 API、权限码、JWT、导入字段映射和业务响应格式不变。
- 明确已有 FastAPI 数据库的显式迁移边界，避免通过双表 fallback 掩盖数据迁移风险。

## 非目标

- 本轮不修改 Django 模型，Django 两张关联表已经是目标命名。
- 本轮不修改用户、角色、权限主表表名。
- 本轮不改变 `Users.roles` 或 `Roles.permissions` 的 API 字段语义。
- 本轮不做生产数据库在线迁移脚本；如部署库已有旧 FastAPI through 表，必须另开迁移任务。
- 本轮不引入双表读写、兼容视图或静默 fallback。

## 当前事实

- `backend/drf_admin/apps/system/models.py::Roles.permissions` 使用 `db_table="system_roles_to_system_permissions"`。
- `backend/drf_admin/apps/system/models.py::Users.roles` 使用 `db_table="system_users_to_system_roles"`。
- `fastapi/app/db/models/system.py::Roles.permissions` 已统一为 `through="system_roles_to_system_permissions"`。
- `fastapi/app/db/models/oauth.py::Users.roles` 已统一为 `through="system_users_to_system_roles"`。
- `scripts/model_contracts.py::DJANGO_FASTAPI_RELATION_CONTRACTS` 已要求两组 through 表与 Django 命名一致。
- `backend/drf_admin/utils/test_model_contracts.py::test_django_relation_through_tables_match_shared_contracts` 已校验 Django 侧 through 表等于共享契约。
- `fastapi/tests/test_import_django_model_contracts.py::test_fastapi_relation_through_tables_match_shared_contracts` 已校验 FastAPI 侧 through 表等于共享契约。
- `docs/DATABASE_SCHEMA.md` 和 `docs/TECH_DEBT.md` 已移除关联表命名差异描述，并保留关联字段差异和旧 FastAPI through 表迁移边界。

## 设计原则

- 先用 RED 测试锁定“共享关联表必须同名”的目标，再改 FastAPI 模型和契约。
- 关联表命名统一只触碰 ORM/契约/测试/文档层，不改变对外 API。
- 不通过双表读写、兼容查询或静默建表规避迁移问题。
- 每次只处理两张 M2M through 表，不混入字段名、主表或权限业务逻辑变更。
- 已有旧 FastAPI 数据库需要显式迁移，代码只表达新的目标结构。

## 决策驱动因素

- 长期可维护性：双后端替代实现共享同一业务域时，M2M 表名一致能降低 fixture 导入、数据库文档和排障成本。
- 数据安全：直接改 through 表名后，旧 FastAPI 数据库里的关联数据不会自动迁移。
- 验证可行性：现有共享关联契约和双端测试已经能定位 through 表差异，适合补一致性断言后小步推进。
- 发布风险：M2M 关联数据影响登录权限、角色授权和用户角色关系，必须用目标测试覆盖运行时权限链路。

## 方案对比

### 方案 A：继续登记差异

- 做法：保留 FastAPI 现有 `system_roles_permissions` 和 `system_users_roles`，只在文档和契约里继续说明差异。
- 优点：零迁移风险。
- 缺点：不解决技术债，后续导入、调试和数据库文档仍要长期区分两套命名。

### 方案 B：直接将 FastAPI through 表统一到 Django 命名

- 做法：修改 FastAPI 两个 `ManyToManyField(..., through=...)` 和共享关联契约，测试与文档跟随更新。
- 优点：直接消除关联表命名差异，改动面清晰，符合双后端契约收敛方向。
- 缺点：已有 FastAPI 数据库需要显式迁移旧关联表，否则用户角色和角色权限关系会读不到。

### 方案 C：新增双表兼容层

- 做法：FastAPI 同时兼容旧表和 Django 命名表。
- 优点：短期迁移看起来平滑。
- 缺点：会带来双写一致性、读优先级和回滚语义问题，属于长期复杂 fallback。

## 推荐方案

推荐方案 B。

本轮通过测试和契约把 FastAPI through 表改为 Django 命名，并在文档里明确迁移边界。旧 FastAPI 数据库如果已有 `system_roles_permissions` 或 `system_users_roles`，应在部署迁移中显式重命名或复制数据到目标表，不在业务代码中增加双表静默兼容。

## 执行计划

- [x] P1 串行：RED 补共享关联表同名测试，复现 `Roles.permissions` 与 `Users.roles` 的 Django/FastAPI through 表仍不一致。
- [x] P2 串行：GREEN 修改 FastAPI `Roles.permissions` 和 `Users.roles` 的 `through` 表名，同步 `scripts/model_contracts.py`。
- [x] P3 串行：执行并修正 FastAPI M2M 目标测试，重点覆盖角色权限分配、用户角色关系、Django fixture 导入和运行时权限链路。
- [x] P4 串行：同步数据库文档、技术债和字典模型治理计划，移除关联表命名差异描述，保留显式迁移边界说明。
- [x] P5 串行：执行模型契约校验、FastAPI 目标测试、FastAPI `make quality`、Django 目标测试和根目录校验。
- [ ] P6 串行：review-gate、提交、PR、CI 和合并。

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

- FastAPI 测试库初始化如果仍按旧 through 表名建表，目标测试会暴露角色权限或用户角色关系读写失败。
- Django fixture 导入如果隐式依赖旧 FastAPI through 表名，golden fixture 导入测试会失败。
- 运行时权限链路如果缺少角色权限关系，登录后的菜单、按钮权限和 RBAC 判断会出现回归。
- 已有 FastAPI 本地 SQLite/MySQL 数据不会随 ORM through 表名自动迁移；这不是本轮用 fallback 掩盖的问题，必须通过显式迁移处理。

## HARD-GATE

用户确认前，不进行任何业务代码、测试代码或契约代码修改。本文件只是规划草案。

## 进度记录

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q` 失败，新增测试捕获 `system_roles_permissions` 与 `system_roles_to_system_permissions` 不一致。
- GREEN：FastAPI `Roles.permissions` 和 `Users.roles` 的 through 表已统一到 Django 命名，共享关联契约已同步；模型契约测试通过（12 passed）。
- 目标验证：FastAPI M2M 目标测试通过（111 passed），覆盖 Django fixture 导入、golden fixture、运行时写接口、角色服务和用户服务。
- 全量验证：FastAPI `make quality` 通过（533 passed，覆盖率 84.74%）；Django 模型契约测试通过（4 passed）；根目录模型/API/文档/路由组件/Django 迁移校验和 `git diff --check` 均通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只统一 FastAPI 两张 M2M through 表名和共享关联契约，不修改 Django 模型、主表、前端 API、权限码或业务响应；安全检查未发现新增 secret、mock、双表读写或静默 fallback；复杂度检查通过，本轮新增一个目标契约测试并修改两个 through 表名常量，未新增超长函数；Document-refresh: needed，原因：数据库关联表事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧表 `system_roles_permissions` 或 `system_users_roles`，需要显式迁移到 Django 命名表，且关联表字段命名差异仍需后续独立治理。
