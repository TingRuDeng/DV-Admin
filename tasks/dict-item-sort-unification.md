# 字典项排序字段差异治理计划

## 目标

- 移除 FastAPI 字典项模型、schema、service 和测试中的 FastAPI-only `sort` 字段。
- 让 Django 与 FastAPI 的 `system_dict_items` 字段集合继续向共享契约收敛。
- 保持前端字典项页面当前行为稳定：不新增排序输入、不展示排序列。

## 非目标

- 本轮不把 `sort` 字段加回 Django。
- 本轮不设计新的字典项拖拽排序、手动排序或前端排序交互。
- 本轮不改变字典主表、权限、用户角色关系或其他模型契约。
- 本轮不提供旧 `sort` 字段 fallback 或静默兼容路径。

## 当前事实

- `backend/drf_admin/apps/system/models.py::DictItems` 当前没有 `sort` 字段，只有一行注释掉的历史字段。
- `backend/drf_admin/apps/system/migrations/0002_alter_dictitems_options_remove_dictitems_sort_and_more.py` 已删除 Django `DictItems.sort`，并把排序改为 `["dict", "value"]`。
- `fastapi/app/db/models/system.py::DictItems` 当前仍有 `sort = fields.IntField(default=0)`，`Meta.ordering = ["sort"]`，并声明 `("dict_data_id", "sort")` 索引。
- `fastapi/app/schemas/system.py::DictItemBase`、`DictItemUpdate`、`DictItemOut` 当前仍声明 `sort`。
- `fastapi/app/services/system/dict_service.py::DictService` 当前创建、更新、返回字典项时读写 `sort`，并在分页、列表和按编码查询中按 `sort` 排序。
- `frontend/src/views/system/dict/dict-item.vue` 当前不展示排序列；`DictItemFormDrawer.vue` 当前不提供排序输入。
- `frontend/src/api/system/dict-items-api.ts::DictItemForm` 和 `DictItemPageVO` 当前把 `sort` 声明为可选字段，但生产页面没有提交该字段。
- `scripts/api_endpoint_dict_contracts.py` 的字典项创建契约只声明 `dict/label/value`，没有把 `sort` 作为共享请求字段。
- `docs/DATABASE_SCHEMA.md` 和 `docs/TECH_DEBT.md` 当前剩余差异只剩字典项排序字段。

## 设计原则

- 以 Django 当前迁移后的模型为收敛方向，不把已经移除的字段重新扩回 Django。
- 删除未进入前端页面和共享 API 契约的 FastAPI-only 字段，减少双后端切换和数据迁移分支。
- 排序行为改为与 Django 一致的稳定排序：按字典归属和字典项值排序，避免删除 `sort` 后列表顺序不确定。
- 通过 RED 测试先证明共享模型契约没有锁住 FastAPI-only `sort`，再修改模型和调用链。

## 决策驱动因素

- Django 迁移链已经显式删除 `sort`，说明当前 Django 端事实不是“遗漏字段”，而是“已移除字段”。
- 前端页面不展示、不编辑、不依赖 `sort`，继续保留 FastAPI-only `sort` 会增加无用户价值的迁移成本。
- FastAPI 当前按 `sort` 排序，删除字段必须同时改 service 排序和索引契约，不能只删 ORM 字段。
- FastAPI 测试大量构造 `sort`，需要集中修正测试样例，避免测试继续鼓励契约外字段。

## 方案对比

### 方案 A：给 Django 加回 `sort`

- 做法：新增 Django 模型字段和迁移，让 Django 向 FastAPI 收敛。
- 优点：FastAPI 改动少，保留现有排序能力。
- 缺点：会反向撤销 Django 迁移 `0002` 的历史决策；前端当前没有排序交互，新增字段缺少明确业务收益。

### 方案 B：删除 FastAPI `sort`

- 做法：删除 FastAPI `DictItems.sort`，同步 schema/service/tests/docs，排序改为与 Django 一致的 `dict_data_id/value` 或等价稳定顺序。
- 优点：沿着 Django 当前模型收敛，删除未进入前端和共享 API 契约的 FastAPI-only 字段。
- 缺点：已有 FastAPI 数据库如果存在 `sort` 列，需要显式迁移删除或忽略；外部调用方如果提交 `sort`，会暴露契约外字段。

### 方案 C：保留数据库字段，只从 API 隐藏

- 做法：FastAPI ORM 继续保留 `sort`，schema/service 不再输出或输入。
- 优点：短期旧数据库兼容最平滑。
- 缺点：数据库结构差异仍存在，模型契约治理无法收口，还会留下“接口看不到但库里有”的隐性债。

## 推荐方案

推荐方案 B。

本轮删除 FastAPI 字典项 `sort` 字段，并把字典项列表排序改为与 Django 等价的稳定顺序。旧 FastAPI 数据库如果仍存在 `sort` 列，应通过显式迁移删除或忽略；业务代码不继续读写该字段。

## 执行计划

- [x] P1 串行：RED 增加模型契约测试，复现 FastAPI `DictItems.sort` 仍存在。
- [x] P2 串行：GREEN 删除 `fastapi/app/db/models/system.py::DictItems.sort`，同步 `Meta.ordering` 和索引定义。
- [x] P3 串行：GREEN 删除 `fastapi/app/schemas/system.py` 中字典项 create/update/out 的 `sort` 字段。
- [x] P4 串行：GREEN 修改 `fastapi/app/services/system/dict_service.py::DictService`，停止读写 `sort`，并把字典项排序改为稳定的 `dict_data_id/value` 或等价顺序。
- [x] P5 串行：修正 FastAPI 字典项 service、运行时契约、fixture 导入和 golden fixture 测试，移除 `sort` 断言和样例输入。
- [x] P6 串行：同步 `frontend/src/api/system/dict-items-api.ts`，移除字典项类型中的可选 `sort` 字段。
- [x] P7 串行：同步 `docs/DATABASE_SCHEMA.md`、`docs/TECH_DEBT.md`、当前任务文件和 `tasks/todo.md`，标记模型差异收敛状态。
- [x] P8 串行：执行模型契约校验、FastAPI 目标测试、FastAPI 质量门禁、Django 目标测试、前端类型/质量检查、根目录校验和 diff 检查。
- [x] P9 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `fastapi/app/db/models/system.py`
- `fastapi/app/schemas/system.py`
- `fastapi/app/services/system/dict_service.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_import_django_data.py`
- `fastapi/tests/test_import_django_data_golden.py`
- `fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py`
- `fastapi/tests/test_dict_service.py`
- `fastapi/tests/test_dict_items.py`
- `frontend/src/api/system/dict-items-api.ts`
- `docs/DATABASE_SCHEMA.md`
- `docs/TECH_DEBT.md`
- `tasks/todo.md`

## 验证矩阵

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q`
- 根目录：`python3 scripts/validate_model_contracts.py .`
- FastAPI 目标：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/runtime_api_contracts/test_dict_write_contracts.py tests/test_dict_service.py tests/test_dict_items.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- Django 目标：`cd backend && uv run pytest drf_admin/utils/test_model_contracts.py drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py -q`
- 前端：`cd frontend && pnpm run quality`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- FastAPI service 如果仍按 `sort` 排序或返回 `sort`，删除 ORM/schema 字段后目标测试会暴露运行时失败。
- FastAPI fixture 导入和 golden fixture 如果继续提交 `sort`，导入测试会暴露契约外字段。
- 前端类型移除 `sort` 后，如果隐藏页面路径仍读取该字段，前端 type-check 会暴露遗漏。
- 已有 FastAPI 数据库不会自动删除旧列；本轮不通过 fallback 掩盖该迁移边界。

## HARD-GATE

用户已确认“按顺序推进”，本计划作为下一轮治理切片。若执行中发现前端真实业务依赖字典项排序交互，应停止并回到规划阶段，而不是静默保留 FastAPI-only 字段。

## 进度记录

- RED：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py -q` 失败，新增断言捕获 `DictItems.sort` 仍存在，符合预期。
- GREEN：FastAPI `DictItems.sort` 已删除；字典项 schema/service 停止读写 `sort`；字典项列表排序改为 `dict_data_id/value` 或字典内 `value`；FastAPI 字典项测试、运行时契约样例、fixture golden 和前端 API 类型已移除字典项 `sort`。
- 目标验证：`python3 scripts/validate_model_contracts.py .` 通过；`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/runtime_api_contracts/test_dict_write_contracts.py tests/test_dict_service.py tests/test_dict_items.py -q` 通过（88 passed）。
- 完整验证：`cd fastapi && make quality` 通过（539 passed，覆盖率 84.70%）；`cd backend && uv run pytest drf_admin/utils/test_model_contracts.py drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py -q` 通过（6 passed）；`cd frontend && pnpm run quality` 通过（64 个测试文件、172 个测试）；`python3 scripts/validate_docs.py . --profile generic`、`python3 scripts/validate_api_contracts.py .`、`git diff --check` 均通过。
- 最终轻量复核：文档措辞修正后，`python3 scripts/validate_docs.py . --profile generic`、`python3 scripts/validate_model_contracts.py .`、`python3 scripts/validate_api_contracts.py .`、`git diff --check` 均通过。
- 远端交付：PR #168 已合并，merge commit 为 `2d71dbe`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只移除 FastAPI 字典项 `sort` 扩展字段，并同步 schema、service、目标测试、前端 API 类型、数据库文档和技术债；安全检查未发现新增 secret、mock、静默兼容或 fallback；复杂度检查通过，本轮以删除字段读写和稳定排序替换为主，没有新增复杂分支；Document-refresh: done，数据库字段事实、排序/索引说明和技术债状态已同步；剩余风险是已有 FastAPI 数据库如果仍存在旧列 `sort`，需要显式迁移删除或忽略，且 `fastapi/app/schemas/system.py`、`fastapi/app/services/system/dict_service.py`、`fastapi/tests/test_dict_service.py` 仍为既有超 300 行文件，后续应单独拆分治理。
