# 字典模型差异治理计划

## 目标

- 收敛 Django 与 FastAPI 字典主表的模型差异，优先处理 `system.dicts` 与 `DictData` 在表名、字段命名和字段约束上的不一致。
- 让共享模型契约从“记录差异”逐步转向“约束一致”，降低 Django fixture 导入、双后端切换和后续迁移成本。
- 在实现前明确数据库迁移、API 兼容和导入脚本影响边界。

## 非目标

- 本轮不一次性统一所有 Django/FastAPI 模型。
- 本轮不改变前端 API 字段契约，除非实现阶段证明确实必须同步。
- 本轮不删除已有兼容导入逻辑，除非先有测试证明旧路径已无必要。

## 当前事实

- `scripts/model_contracts.py` 的 `DjangoFastapiModelContract` 已声明 `system.dicts` 到 `DictData` 的映射，并要求 Django/FastAPI 字典主表同名为 `system_dicts`。
- `backend/drf_admin/apps/system/models.py` 中 `Dicts.dict_code` 是 `max_length=32` 且 `unique=True`。
- `fastapi/app/db/models/system.py` 中 `DictData.dict_code` 是 `max_length=32` 且 `unique=True`。
- `fastapi/app/db/models/system.py` 中 `DictData.remark` 已与 Django 保持同名，但长度仍为 FastAPI 侧 100、Django 侧 50。
- `docs/TECH_DEBT.md` 已把 Django 和 FastAPI 模型差异列为中优先级技术债，当前剩余重点是关联表命名不同。

## 设计原则

- 优先选择能消除根因的方案，而不是继续扩大别名映射。
- 不用静默 fallback 或假成功路径掩盖迁移风险。
- 先用测试暴露差异，再做最小实现。
- 对可能破坏已有 FastAPI SQLite/MySQL 数据的表名变更，必须有迁移策略或明确非生产边界。

## 方案对比

### 方案 A：只强化契约，不改模型

- 做法：新增“差异必须显式登记”的校验，继续允许 `system_dict_data` 表名差异。
- 优点：风险最低，不涉及数据库迁移。
- 缺点：只能记录债务，不能减少长期维护成本；与本轮“治理模型差异”的目标不匹配。

### 方案 B：统一 FastAPI 字典模型命名到 Django

- 做法：将 FastAPI `DictData` 的表名、关键字段和契约逐步对齐 Django：`system_dicts`、`dict_code`、`remark`。
- 优点：解决当前技术债的核心差异，减少导入脚本和契约别名复杂度。
- 缺点：涉及 FastAPI ORM 模型、schema/service/API、测试和潜在数据迁移，需要严格分步。

### 方案 C：引入新统一模型并保留旧模型兼容层

- 做法：新增统一字典模型，旧 `DictData` 保留为过渡适配。
- 优点：可以渐进迁移。
- 缺点：会同时存在两套模型语义，复杂度更高，容易形成长期兼容债。

## 推荐方案

推荐继续采用方案 B 的最小垂直切片，但不要把表名、字典项外键和关联表迁移混在一个 PR。

第一轮已处理可低风险验证的字段约束一致性：FastAPI `DictData.dict_code` 的 `max_length` 已对齐到 Django `Dicts.dict_code` 的 32，并补共享契约测试。第二轮已将 FastAPI `DictData` 内部字段从 `code/desc` 统一为 `dict_code/remark`，前端 API 仍保持 `dictCode/remark`。第三轮已将 FastAPI `DictData` 表名统一为 `system_dicts`，共享模型契约开始约束字典主表表名一致。

已有 FastAPI 数据库如果仍存在旧表 `system_dict_data`，需要通过显式数据库迁移切换到 `system_dicts`；业务代码不提供双表静默 fallback。

## 执行计划

- [x] P1 串行：RED 补共享字典字段约束一致性测试，复现 `DictData.code.max_length=50` 与 `Dicts.dict_code.max_length=32` 漂移。
- [x] P2 串行：GREEN 将 FastAPI 字典编码字段长度契约与 Django 对齐，并更新 `scripts/model_field_constraint_contracts.py`。
- [x] P3 串行：执行模型契约校验、FastAPI 目标测试、FastAPI `make quality`、Django 目标测试和根目录校验。
- [x] P4 串行：review-gate、提交、PR、CI 和合并。
- [x] P5 串行：将 FastAPI `DictData` 内部字段从 `code/desc` 统一为 `dict_code/remark`。
- [x] P6 串行：同步 schema/service/import 映射、共享模型契约和字典相关测试。
- [x] P7 串行：执行 FastAPI 目标测试、FastAPI `make quality`、Django 目标测试、根目录校验、review-gate、PR、CI 和合并。
- [x] P8 串行：将 FastAPI `DictData` 表名从 `system_dict_data` 统一为 `system_dicts`。
- [x] P9 串行：同步共享模型契约、数据库文档、技术债和字典治理计划。

## 涉及文件

- `scripts/model_field_constraint_contracts.py`
- `scripts/validate_model_contracts.py`
- `scripts/model_fastapi_validation.py`
- `fastapi/app/db/models/system.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `backend/drf_admin/utils/test_model_contracts.py`
- `tasks/todo.md`

## 验证矩阵

- RED：`uv run pytest tests/test_import_django_model_contracts.py -q`
- GREEN：`python3 scripts/validate_model_contracts.py .`
- FastAPI：`make quality`
- Django：`uv run pytest drf_admin/utils/test_model_contracts.py -q`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 根目录：`python3 scripts/validate_route_components.py .`
- 根目录：`python3 scripts/validate_django_migrations.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- 如果 FastAPI 现有测试或 fixture 使用超过 32 位的字典编码，改动会暴露真实数据约束冲突，应先修测试数据或业务约束，不应放宽回 50。
- 如果 schema/API 层把 `code` 作为前端稳定字段使用，本轮不触碰字段名，避免把约束治理扩大成 API 迁移。
- 如果后续推进表名统一，需要单独设计迁移脚本和兼容窗口，不能与本轮字段长度约束混在一个 PR。

## HARD-GATE

用户确认前，不进行任何业务代码、测试代码或契约代码修改。本文件只是规划草案。

## 进度记录

- RED：`uv run pytest tests/test_import_django_model_contracts.py -q` 失败，新增测试捕获 `DictData.code.max_length=50` 与 `Dicts.dict_code.max_length=32` 漂移。
- GREEN：FastAPI `DictData.code` 与共享 FastAPI 字段约束契约已对齐为 `max_length=32`；目标测试通过（9 passed）。
- 调试：FastAPI 全量门禁首次失败于字典写接口运行时样例，根因是更新样例 `dictCode` 长度为 37，超过新的 32 位约束；已缩短测试样例前缀并用常量断言生成结果不超过 32。
- 验证：模型契约校验、Django 目标测试（4 passed）、FastAPI 字典写接口运行时目标测试（2 passed）、FastAPI `make quality`（530 passed，覆盖率 84.75%）、Django ruff、Django `uv run pytest`（104 passed）、文档/API/路由组件/Django 迁移校验和 `git diff --check` 均通过。
- 字段命名统一：FastAPI `DictData` 内部字段已改为 `dict_code/remark`；共享模型契约已移除 `system.dicts` 的 `dict_code -> code`、`remark -> desc` 字段别名；Django fixture 导入改为同名字段写入；目标测试（76 passed）、FastAPI `make quality`（531 passed，覆盖率 84.74%）、Django 模型契约测试（4 passed）、根目录校验和远端 CI 均通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只处理字典编码字段长度约束一致性，不改变 API 字段名、表名或前端契约；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证覆盖 RED/GREEN、模型契约、双后端目标测试、Django 全量测试、FastAPI 全量质量门禁和根目录校验；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库文档描述或迁移流程；剩余风险是 `fastapi/app/db/models/system.py` 仍为 342 行，属于既有模型文件拆分技术债，后续应单独规划处理。

Review-gate：finished；Spec 符合度通过，字段命名统一轮次只处理字典主表内部字段名，不修改表名 `system_dict_data`、字典项外键、前端调用或 API 路径；安全检查未发现新增 secret、mock 或静默 fallback；Document-refresh: needed，原因：数据库文档和技术债需要同步反映 `dict_code/remark` 已成为双后端同名字段；剩余风险是 FastAPI 字典表名仍与 Django `system_dicts` 不一致，需要后续独立迁移计划处理。
