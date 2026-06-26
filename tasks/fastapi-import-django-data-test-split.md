# FastAPI Django 数据导入测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_import_django_data.py` 从 327 行职责混合测试拆分为小测试文件。
- 保留现有断言语义，覆盖模型映射、字段映射、基础模型创建、关系创建、字段转换和导入辅助函数存在性。
- 降低单个测试文件体量，避免后续扩展继续堆叠到一个大文件。

## 非目标

- 不修改 `fastapi/app/db/import_django_data.py` 运行时导入逻辑。
- 不调整 golden fixture、fail-fast 测试或模型契约测试语义。
- 不新增 mock 假成功、静默 fallback 或跳过测试逻辑。

## 当前事实

- `fastapi/tests/test_import_django_data.py` 当前 327 行，是当前 FastAPI 最大测试文件。
- 文件内同时包含 `MODEL_MAPPING`/`FIELD_MAPPING` 断言、部门/权限/角色/字典/用户基础模型创建、FK/M2M 关系、自引用关系、更新、未知字段、导入顺序、`is_active` 字段转换和 helper 存在性测试。
- `fastapi/tests/test_import_django_data_fail_fast.py` 已覆盖缺 fixture、单条导入失败和 M2M 缺失的 fail-fast 行为。
- `fastapi/tests/test_import_django_data_golden.py` 已覆盖小型 Django fixture 的真实导入链路。

## 决策日志

- 方案 A：按测试职责拆成 `mapping`、`models`、`relations`、`helpers` 四个文件，删除原大文件。
  - 优点：职责清楚，单文件体量小，不改变测试行为。
  - 缺点：新增文件数量较多。
- 方案 B：只把后半段 helper 测试拆出去。
  - 优点：改动更小。
  - 缺点：主文件仍接近 300 行，不能解决长期体量问题。
- 方案 C：合并到 golden/fail-fast 测试。
  - 优点：文件数量少。
  - 缺点：职责混淆，会把直接模型创建测试和真实 fixture 导入测试混在一起。

推荐方案：采用方案 A。本轮只拆测试组织，不改变运行时代码和断言语义。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/test_import_django_data_mapping.py`，迁移映射和导入顺序测试。
- [x] P3 串行：新增 `fastapi/tests/test_import_django_data_models.py`，迁移基础模型创建、更新和字段转换测试。
- [x] P4 串行：新增 `fastapi/tests/test_import_django_data_relations.py`，迁移 FK、M2M 和自引用关系测试。
- [x] P5 串行：新增 `fastapi/tests/test_import_django_data_helpers.py`，迁移 helper 存在性测试。
- [x] P6 串行：删除旧 `fastapi/tests/test_import_django_data.py`。
- [x] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_import_django_data_mapping.py tests/test_import_django_data_models.py tests/test_import_django_data_relations.py tests/test_import_django_data_helpers.py tests/test_import_django_data_fail_fast.py tests/test_import_django_data_golden.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

Django 数据导入测试拆分已完成：原 327 行 `test_import_django_data.py` 已删除，映射/导入顺序、基础模型、关系和 helper 存在性测试分别迁移到 `test_import_django_data_mapping.py`、`test_import_django_data_models.py`、`test_import_django_data_relations.py`、`test_import_django_data_helpers.py`。既有 fail-fast、golden fixture 和模型契约测试未改动。

验证通过：目标导入测试组合 22 passed；FastAPI `make quality` 551 passed，覆盖率 87.04%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整测试组织，不修改 `fastapi/app/db/import_django_data.py` 运行时导入逻辑、golden fixture、fail-fast 测试或模型契约测试语义；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后最大目标测试文件为 152 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/tests/test_health.py` 仍超过 300 行，需要后续独立治理。
