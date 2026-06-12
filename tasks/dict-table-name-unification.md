# 字典主表表名统一计划

## 目标

- 将 FastAPI 字典主表从 `system_dict_data` 统一到 Django 表名 `system_dicts`。
- 让共享模型契约从“登记表名差异”转为“约束字典主表表名一致”。
- 保持前端 API、schema 字段、字典项外键字段和权限契约不变。
- 明确本地开发数据与部署数据的迁移边界，避免直接改表名导致现有 FastAPI 数据不可见。

## 非目标

- 本轮不修改 Django 模型，Django `Dicts.Meta.db_table` 已是目标表名。
- 本轮不修改字典项外键字段 `dict_data` 或 API 响应里的 `dict` 字段。
- 本轮不处理角色-权限、用户-角色等关联表命名差异。
- 本轮不做生产数据库在线迁移脚本；如果需要生产迁移，必须另开部署迁移任务。
- 本轮不删除已经验证有调用依赖的 API 兼容别名。

## 当前事实

- `fastapi/app/db/models/system.py` 的 `DictData.Meta.table` 已统一为 `system_dicts`。
- `backend/drf_admin/apps/system/models.py` 的 `Dicts.Meta.db_table` 当前为 `system_dicts`。
- `scripts/model_contracts.py` 的 `DjangoFastapiModelContract(system.dicts)` 已声明 `django_table="system_dicts"`、`fastapi_table="system_dicts"`。
- `fastapi/tests/test_import_django_model_contracts.py::test_dict_data_table_name_matches_django_contract` 已约束两端表名一致。
- `docs/DATABASE_SCHEMA.md` 和 `docs/TECH_DEBT.md` 已移除字典主表表名差异描述，并保留旧 FastAPI 数据库的显式迁移边界。
- FastAPI 字典主表内部字段已经统一为 `dict_code/remark`，本轮不需要再处理 `code/desc` 字段别名。

## 设计原则

- 先用 RED 测试锁定“字典主表表名应该一致”的目标，再修改模型和契约。
- API 边界不变，表名变化只发生在 ORM/契约/测试/文档层。
- 不增加静默 fallback，不同时读写两张表来掩盖迁移风险。
- 开发环境数据迁移可以通过明确脚本或迁移说明处理；生产迁移不能混入本轮代码改名。
- 表名统一不与字典项外键命名统一混在一个 PR，避免迁移面失控。

## 决策驱动因素

- 长期可维护性：Django 与 FastAPI 作为替代实现时，共享业务表名越一致，fixture 导入和双端校验越简单。
- 数据安全：直接把 ORM 表名改成 `system_dicts` 后，已有 FastAPI 本地库里的 `system_dict_data` 不会自动迁移。
- 变更可验证性：字段名已统一，当前表名变更可以用模型契约、导入测试和运行时 API 样例独立验证。
- 发布风险：如果部署环境已有 FastAPI 数据，表名变更需要外部迁移步骤。

## 方案对比

### 方案 A：只继续登记差异

- 做法：保留 `system_dict_data`，只在文档中说明差异。
- 优点：零迁移风险。
- 缺点：不解决技术债，后续导入、文档和契约仍需长期区分两套表名。

### 方案 B：直接把 FastAPI ORM 表名改为 `system_dicts`

- 做法：修改 `DictData.Meta.table` 和共享契约 `fastapi_table`，测试与文档跟随更新。
- 优点：最直接地消除字典主表表名差异，改动面小，容易验证。
- 缺点：已有 FastAPI 数据库中的 `system_dict_data` 需要显式迁移；否则新 ORM 会读取空表或建新表。

### 方案 C：保留旧表名并增加兼容视图或双表读写

- 做法：FastAPI 同时兼容 `system_dict_data` 和 `system_dicts`。
- 优点：短期迁移看似平滑。
- 缺点：会引入双写/读优先级/一致性问题，属于复杂 fallback，容易形成长期债务。

## 推荐方案

推荐方案 B。

本轮先统一 ORM 表名和共享契约，并通过测试证明 API、fixture 导入和模型契约仍正常。对于已有 FastAPI 本地或部署数据，不在代码中做静默双表兼容，而是在计划和文档中明确迁移边界：需要迁移时应执行显式数据库迁移，将 `system_dict_data` 重命名为 `system_dicts` 或复制数据后切换。

## 执行计划

- [x] P1 串行：RED 补共享表名一致性测试，复现 `system.dicts` 的 Django/FastAPI 表名仍不一致。
- [x] P2 串行：GREEN 修改 FastAPI `DictData.Meta.table` 为 `system_dicts`，同步 `scripts/model_contracts.py` 的 `fastapi_table`。
- [x] P3 串行：修正数据库文档、技术债和字典治理计划，移除字典主表表名差异描述，保留迁移边界说明。
- [x] P4 串行：执行模型契约校验、FastAPI 目标测试、FastAPI `make quality`、Django 目标测试和根目录校验。
- [ ] P5 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `fastapi/app/db/models/system.py`
- `scripts/model_contracts.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_import_django_data.py`
- `fastapi/tests/test_import_django_data_golden.py`
- `fastapi/tests/test_dict_service.py`
- `fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py`
- `docs/DATABASE_SCHEMA.md`
- `docs/TECH_DEBT.md`
- `tasks/dict-model-unification.md`
- `tasks/todo.md`

## 验证矩阵

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q`
- FastAPI 目标：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/test_dict_service.py tests/runtime_api_contracts/test_dict_write_contracts.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- Django 目标：`cd backend && uv run pytest drf_admin/utils/test_model_contracts.py -q`
- 根目录：`python3 scripts/validate_model_contracts.py .`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 根目录：`python3 scripts/validate_route_components.py .`
- 根目录：`python3 scripts/validate_django_migrations.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- FastAPI 测试库初始化如果依赖旧表名，目标测试会暴露表不存在或数据为空。
- Django fixture 导入如果隐式依赖旧表名，golden fixture 导入测试会失败。
- 文档或模型契约校验如果仍要求 `system_dict_data`，根目录模型契约校验会失败。
- 已有 FastAPI 本地 SQLite/MySQL 数据不会随 ORM 表名自动迁移；这不是本轮用 fallback 掩盖的问题，必须通过显式迁移处理。

## HARD-GATE

用户确认前，不进行任何业务代码、测试代码或契约代码修改。本文件只是规划草案。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只统一 FastAPI 字典主表表名和共享模型契约，不修改 Django 模型、字典项外键、前端 API 或权限契约；安全检查未发现新增 secret、mock、双表读写或静默 fallback；测试与验证覆盖 RED/GREEN、FastAPI 目标测试、FastAPI `make quality`、Django 模型契约测试、根目录模型/API/文档/路由组件/Django 迁移校验和 `git diff --check`；Document-refresh: needed，原因：数据库表名事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧表 `system_dict_data`，需要通过显式迁移切换到 `system_dicts`。
