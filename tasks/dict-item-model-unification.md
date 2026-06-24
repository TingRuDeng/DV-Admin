# 字典项模型差异治理计划

## 目标

- 收敛 Django 与 FastAPI 字典项模型的剩余结构差异，优先处理 FastAPI-only 字段 `is_default/remark`。
- 让 `system.dictitems` 到 `DictItems` 的共享模型契约从“文档说明差异”继续转向“测试约束一致”。
- 保持前端字典项管理页面和双后端字典项写接口契约稳定。

## 非目标

- 本轮不处理 `label/value` 长度从 FastAPI 50 到 Django 32 的约束差异。
- 本轮不处理 FastAPI `sort` 与 Django 当前注释掉的 `sort` 字段差异。
- 本轮不修改 Django 模型、Django 迁移链或前端页面交互。
- 本轮不增加双字段 fallback、mock 成功路径或静默兼容逻辑。

## 当前事实

- `backend/drf_admin/apps/system/models.py::DictItems` 只有 `label/value/status/tag_type/dict` 业务字段，不包含 `is_default/remark`。
- `fastapi/app/db/models/system.py::DictItems` 已移除 `is_default = fields.BooleanField(default=False)` 和 `remark = fields.CharField(max_length=100, default="")`。
- `fastapi/app/schemas/system.py::DictItemBase`、`DictItemUpdate`、`DictItemOut` 已移除 `is_default/remark`。
- `fastapi/app/services/system/dict_service.py::DictService.create_item_flat`、`update_item_flat` 和相关返回构造已停止读写 `is_default/remark`。
- `frontend/src/api/system/dict-items-api.ts::DictItemForm`、`DictItemPageVO` 不声明 `isDefault/is_default/remark`，当前生产页面 `frontend/src/views/system/dict/dict-item.vue` 和 `DictItemFormDrawer.vue` 也不展示或提交这两个字段。
- `docs/DATABASE_SCHEMA.md` 和 `docs/TECH_DEBT.md` 已移除字典项 `is_default/remark` 剩余差异描述，当前剩余差异集中在 `label/value` 长度约束和 `sort` 字段。

## 设计原则

- 优先删除未被前端契约使用的 FastAPI-only 字段，减少迁移和排障分支。
- 用 RED 测试先证明共享模型契约没有锁住 `DictItems` 字段一致性，再改模型。
- 不把字段删除、长度约束和排序字段治理混成一个 PR。
- 已有 FastAPI 数据库如果存在 `is_default/remark` 列，需要显式迁移或丢弃列，不在业务代码中继续读写旧列。

## 决策驱动因素

- Django 是当前模型命名和表结构对齐的参照端。
- 前端字典项 API 类型和页面没有使用 `is_default/remark`，删除这两个 FastAPI 字段的用户可见影响较低。
- FastAPI service/schema 仍读写这两个字段，直接删 ORM 字段前必须同步 schema/service/tests，否则运行时写接口会失败。
- `label/value` 长度和 `sort` 字段仍可能影响前端现有体验，应后续独立规划。

## 方案对比

### 方案 A：只在文档保留差异

- 做法：继续记录 `is_default/remark` 是 FastAPI-only 字段，不改模型。
- 优点：没有数据库迁移风险。
- 缺点：模型差异继续存在，导入、排障和契约验证都无法进一步收敛。

### 方案 B：删除 FastAPI-only 字段并同步 schema/service

- 做法：删除 FastAPI `DictItems.is_default/remark`，同步 `DictItemBase/Update/Out` 和 `DictService` 的读写逻辑，扩展共享契约和运行时测试。
- 优点：直接消除已确认的 FastAPI 扩展字段债，前端当前不依赖这两个字段。
- 缺点：已有 FastAPI 数据库需要显式处理旧列；如果外部调用方直接提交这两个字段，会在严格 schema 下暴露契约外输入。

### 方案 C：保留 ORM 字段，只从 API 隐藏

- 做法：保留数据库字段，但不在 schema/service 输出。
- 优点：短期对旧库最平滑。
- 缺点：数据库结构差异仍然存在，不能解决本轮根因，还会制造“接口看不到但库里还有”的隐性债。

## 推荐方案

推荐方案 B。

本轮只处理 `is_default/remark` 两个 FastAPI-only 字段。前端当前没有声明、展示或提交这两个字段，因此可以把影响控制在 FastAPI ORM、schema、service、测试和文档契约内。旧 FastAPI 数据库如已存在这两列，应通过显式迁移删除或忽略旧列；业务代码不继续读写这两个字段。

## 执行计划

- [x] P1 串行：RED 增加 `fastapi/tests/test_import_django_model_contracts.py` 字典项 FastAPI-only 字段治理测试，复现 `DictItems.is_default/remark` 仍存在。
- [x] P2 串行：GREEN 删除 `fastapi/app/db/models/system.py::DictItems` 的 `is_default/remark` 字段。
- [x] P3 串行：GREEN 同步 `fastapi/app/schemas/system.py` 的 `DictItemBase`、`DictItemUpdate`、`DictItemOut`，移除 `is_default/remark`。
- [x] P4 串行：GREEN 同步 `fastapi/app/services/system/dict_service.py::DictService` 字典项创建、更新和返回构造，停止读写 `is_default/remark`。
- [x] P5 串行：修正 FastAPI 字典项目标测试、Django fixture golden 断言和运行时契约样例，确保双后端字典项写接口仍稳定。
- [x] P6 串行：同步 `docs/DATABASE_SCHEMA.md`、`docs/TECH_DEBT.md` 和 `tasks/dict-model-unification.md`，移除 `is_default/remark` 剩余差异描述，并记录旧列显式迁移边界。
- [ ] P7 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `fastapi/app/db/models/system.py`
- `fastapi/app/schemas/system.py`
- `fastapi/app/services/system/dict_service.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_import_django_data.py`
- `fastapi/tests/test_import_django_data_golden.py`
- `fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py`
- `backend/drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py`
- `docs/DATABASE_SCHEMA.md`
- `docs/TECH_DEBT.md`
- `tasks/dict-model-unification.md`
- `tasks/todo.md`

## 验证矩阵

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q`
- FastAPI 目标：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/runtime_api_contracts/test_dict_write_contracts.py tests/test_dict_service.py tests/test_dict_items.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- Django 目标：`cd backend && uv run pytest drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py -q`
- 根目录：`python3 scripts/validate_model_contracts.py .`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 根目录：`python3 scripts/validate_route_components.py .`
- 根目录：`python3 scripts/validate_django_migrations.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- FastAPI service 如果仍构造 `DictItemOut(is_default=..., remark=...)`，删除 schema 字段后目标测试会暴露响应构造失败。
- FastAPI ORM 删除字段后，如果测试 fixture 或运行时样例仍提交 `is_default/remark`，Pydantic 校验或 ORM 创建会暴露契约外字段。
- 已有 FastAPI 数据库不会自动删除旧列；本轮不通过 fallback 掩盖该迁移边界。
- 如果发现前端隐藏路径实际依赖 `remark`，应停止执行并回到规划阶段，而不是在 FastAPI 里保留半隐式字段。

## HARD-GATE

用户确认前，不进行业务代码、测试代码或契约代码修改。本文件只是规划草案。

## 进度记录

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q` 失败，新增测试捕获 `DictItems.is_default` 仍存在，符合预期。
- GREEN：FastAPI `DictItems` 模型、字典项 schema 和 `DictService` 已停止读写 `is_default/remark`；模型契约测试通过（14 passed）。
- 目标验证：FastAPI 字典项目标测试通过（84 passed），覆盖模型契约、Django fixture 导入、golden fixture、运行时字典写接口、字典 service 和字典项 API。
- 全量验证：FastAPI `make quality` 通过（535 passed，覆盖率 84.71%）；Django 字典写接口运行时契约测试通过（2 passed）；根目录模型/API/文档/路由组件/Django 迁移校验和 `git diff --check` 均通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只移除 FastAPI 字典项 `is_default/remark` 扩展字段，并同步 schema、service、目标测试、数据库文档和技术债，不修改 Django 模型、前端页面或字典项 `label/value/sort` 后续治理范围；安全检查未发现新增 secret、mock、扩展字段 fallback 或静默兼容；复杂度检查通过，本轮删除字段读写并新增一个目标契约测试，未新增复杂分支；Document-refresh: needed，原因：数据库字典项字段事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧列 `is_default/remark`，需要显式迁移删除或忽略，且 `fastapi/app/schemas/system.py`、`fastapi/app/services/system/dict_service.py`、`fastapi/tests/test_dict_service.py` 仍为既有超 300 行文件，后续应单独拆分治理。
