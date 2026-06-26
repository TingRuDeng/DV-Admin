# 拆分 FastAPI Django 数据导入模块

## 目标

- 将 `fastapi/app/db/import_django_data.py` 从接近 300 行的混合职责入口拆成更小的专用模块。
- 保持 `app.db.import_django_data` 的公开导入契约不变，包括 `import_data`、`init`、`main`、`MODEL_MAPPING`、`FIELD_MAPPING` 和 `map_field_name`。
- 保持 fail-fast 语义：fixture 缺失、单条导入失败、FK/M2M 关系失败必须抛出 `DjangoDataImportError`。

## 非目标

- 不修改 Django fixture 数据格式。
- 不修改数据库模型、表名、字段名或迁移。
- 不修改前端 API、后端业务接口或运行时导入行为。

## 当前事实

- `fastapi/app/db/import_django_data.py` 当前为 292 行，集中承担 fixture 读取、模型映射、字段转换、写入和关系补偿。
- 现有测试已经覆盖公开入口、模型映射、fail-fast 和 golden fixture 导入。
- `tasks/todo.md` 当前活跃项为“待选择：下一轮长期可持续性治理目标”，本轮选择该导入模块拆分作为下一项。

## 方案对比

- 方案 A：只拆出 fixture 读取 helper。影响最小，但主文件仍保留模型写入、字段转换和关系处理，长期收益不足。
- 方案 B：按职责拆为配置、状态、fixture 读取、写入转换、关系处理。入口文件只负责编排和兼容导出，能解决根因，且公开契约可保持稳定。

## 推荐方案

采用方案 B。它把变化限制在 `fastapi/app/db/` 内部，能让入口文件回到流程编排职责，同时避免改变外部调用路径。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/db/django_import_config.py`，承接模型映射、字段映射、导入顺序和字段名映射。
- [x] P1 串行：新增 `fastapi/app/db/django_import_state.py`，承接导入任务、上下文和写入缓冲 dataclass。
- [x] P1 串行：新增 `fastapi/app/db/django_fixture_reader.py`，承接 fixture 路径、读取和分组。
- [x] P1 串行：新增 `fastapi/app/db/django_import_writer.py`，承接单模型写入、字段转换和 FK 暂存。
- [x] P1 串行：新增 `fastapi/app/db/django_import_relations.py`，承接自引用 FK 和 M2M 关系处理。
- [x] P2 串行：收缩 `fastapi/app/db/import_django_data.py` 为编排入口和兼容导出。
- [x] P3 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_import_django_data_helpers.py tests/test_import_django_data_mapping.py tests/test_import_django_data_fail_fast.py tests/test_import_django_data_golden.py tests/test_import_django_model_contracts.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
- `wc -l fastapi/app/db/import_django_data.py fastapi/app/db/django_import_*.py fastapi/app/db/django_fixture_reader.py`

## 进度记录

- [x] 已确认当前分支为 `codex/split-import-django-data`，工作区干净。
- [x] 已读取目标模块和现有导入测试。
- [x] 已完成内部职责拆分，`import_django_data.py` 保留编排入口和兼容导出。

## 验证结果

- `cd fastapi && uv run pytest tests/test_import_django_data_helpers.py tests/test_import_django_data_mapping.py tests/test_import_django_data_fail_fast.py tests/test_import_django_data_golden.py tests/test_import_django_model_contracts.py -q`：24 passed。
- `cd fastapi && uv run ruff check app/db/import_django_data.py app/db/django_import_config.py app/db/django_import_state.py app/db/django_fixture_reader.py app/db/django_import_writer.py app/db/django_import_relations.py app/db/django_import_errors.py`：通过。
- `cd fastapi && make quality`：通过，551 passed，覆盖率 87.24%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_model_contracts.py .`：首次在远端 CI 暴露导入映射校验仍扫描旧入口文件，已改为扫描 `fastapi/app/db/django_import_config.py`，复跑通过。
- `cd backend && uv run pytest drf_admin/utils/test_model_contract_validator_structure.py -q`：4 passed。
- `cd backend && uv run ruff check drf_admin/utils/test_model_contract_validator_structure.py`：通过。
- `python3 scripts/validate_api_contracts.py .`、`python3 scripts/validate_route_components.py .`、`python3 scripts/validate_django_migrations.py .`：通过。
- `git diff --check`：通过。
- `wc -l fastapi/app/db/import_django_data.py fastapi/app/db/django_import_config.py fastapi/app/db/django_import_state.py fastapi/app/db/django_fixture_reader.py fastapi/app/db/django_import_writer.py fastapi/app/db/django_import_relations.py fastapi/app/db/django_import_errors.py`：入口文件 58 行，新增模块最大 119 行。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮按计划将 Django fixture 导入的配置、状态、读取、写入转换和关系处理拆入专用模块，`import_django_data.py` 保留编排入口和兼容导出；安全检查未发现新增 secret、mock、静默 fallback 或假成功路径；测试与验证已覆盖目标导入测试、FastAPI 全量质量门禁、模型契约校验、文档校验、diff 检查和行数边界；复杂度检查通过，所有相关文件均低于 300 行；Document-refresh: not-needed，原因：本轮只调整内部模块结构和内部契约校验入口，不改变对外 API、数据库结构或用户可见文档事实；剩余风险是后续如果继续扩展导入规则，应优先在新拆出的专用模块内追加测试，避免逻辑回流到入口文件。
