# 字典项字段长度约束统一计划

## 目标

- 统一 Django 与 FastAPI 字典项 `label/value` 字段长度约束，目标值采用 Django 当前契约 `32`。
- 让共享字段约束契约显式覆盖 `system.dictitems` / `DictItems` 的 `label/value`，防止后续漂移。
- 保持双后端字典项写接口的路径、权限和响应信封稳定。

## 非目标

- 本轮不处理 FastAPI `sort` 字段与 Django 注释掉的 `sort` 字段差异。
- 本轮不修改 Django `DictItems` 模型或 Django 迁移链。
- 本轮不修改前端字典项页面交互和 API 类型。
- 本轮不做静默截断、fallback 或双长度兼容逻辑。

## 当前事实

- `backend/drf_admin/apps/system/models.py::DictItems.label` 当前为 `models.CharField(max_length=32)`。
- `backend/drf_admin/apps/system/models.py::DictItems.value` 当前为 `models.CharField(max_length=32)`。
- `fastapi/app/db/models/system.py::DictItems.label` 当前为 `fields.CharField(max_length=50)`。
- `fastapi/app/db/models/system.py::DictItems.value` 当前为 `fields.CharField(max_length=50)`。
- `fastapi/app/schemas/system.py::DictItemBase` 和 `DictItemUpdate` 当前没有显式声明 `label/value` 的 `max_length`。
- `scripts/model_field_constraint_contracts.py` 当前只覆盖字典主表 `DictData.dict_code`，未覆盖字典项 `label/value`。
- `docs/DATABASE_SCHEMA.md` 当前把字典项 `label/value` 记录为 `varchar(32/50)`，说明两端仍存在长度差异。
- `docs/TECH_DEBT.md` 当前剩余模型差异仍包含“字典项长度约束和排序字段仍不同”。

## 设计原则

- 以 Django 当前模型为字典项长度约束的源头，FastAPI 向 Django 收敛。
- 先补契约测试暴露差异，再修改 FastAPI 模型和 schema。
- 字段长度治理和排序字段治理拆开，避免一个 PR 同时改变输入校验、数据库约束、排序行为和索引语义。
- 对超过 32 字符的旧 FastAPI 数据不做业务代码兼容；如真实库存在旧数据，应在部署迁移前显式清理。

## 决策驱动因素

- Django 与 FastAPI 是同一前端的替代实现，共享模型字段长度应一致。
- 字典项 `label/value` 是用户输入字段，应在 API 边界显式校验，而不是只依赖数据库层失败。
- FastAPI `sort` 当前被 service、schema、索引和测试使用，属于独立行为差异，不适合与长度约束一起收口。
- 前端当前没有字典项长度边界测试；后端 schema 先锁住输入边界能更快消除契约漂移。

## 方案对比

### 方案 A：只更新文档说明差异

- 做法：继续在 `docs/DATABASE_SCHEMA.md` 标注 `varchar(32/50)`。
- 优点：没有行为变更。
- 缺点：差异继续存在，数据迁移和双后端切换仍需要特殊处理。

### 方案 B：FastAPI 向 Django 收敛到 32

- 做法：共享字段约束契约增加字典项 `label/value=32`，FastAPI ORM 和 Pydantic schema 同步收敛到 `32`。
- 优点：直接解决长度漂移，API 边界和数据库边界一致，影响范围集中。
- 缺点：已有 FastAPI 数据或外部调用如果使用 33-50 字符，会被显式拒绝。

### 方案 C：Django 扩展到 50

- 做法：修改 Django 模型和迁移，把字典项 `label/value` 扩展到 `50`。
- 优点：对 FastAPI 旧数据更宽松。
- 缺点：需要 Django 迁移，扩大变更范围；也违背当前治理中“FastAPI 向 Django 契约收敛”的主线。

## 推荐方案

推荐方案 B。

本轮只处理 `label/value` 的长度约束，FastAPI 模型和 schema 向 Django 的 `32` 收敛，并用共享字段约束契约锁住。超过 32 字符的输入应在 FastAPI 请求校验阶段暴露为错误，避免静默截断。

## 执行计划

- [ ] P1 串行：RED 扩展 `scripts/model_field_constraint_contracts.py` 的字典项字段约束，并运行模型契约校验，复现 FastAPI `DictItems.label/value` 仍为 `50`。
- [ ] P2 串行：GREEN 修改 `fastapi/app/db/models/system.py::DictItems.label/value`，将 `max_length` 从 `50` 收敛到 `32`。
- [ ] P3 串行：GREEN 修改 `fastapi/app/schemas/system.py::DictItemBase` 和 `DictItemUpdate`，为 `label/value` 增加 `max_length=32`。
- [ ] P4 串行：补充或调整 FastAPI 字典项 schema / service 目标测试，确保 32 字符以内正常、超过 32 字符被显式拒绝。
- [ ] P5 串行：同步 `docs/DATABASE_SCHEMA.md`、`docs/TECH_DEBT.md` 和当前任务状态，移除字典项长度差异，只保留 `sort` 字段差异。
- [ ] P6 串行：执行模型契约校验、FastAPI 目标测试、FastAPI 质量门禁、Django 目标测试、根目录文档校验和 `git diff --check`。
- [ ] P7 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `scripts/model_field_constraint_contracts.py`
- `fastapi/app/db/models/system.py`
- `fastapi/app/schemas/system.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_dict_service.py`
- `fastapi/tests/test_dict_items.py`
- `fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py`
- `backend/drf_admin/utils/test_model_contracts.py`
- `backend/drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py`
- `docs/DATABASE_SCHEMA.md`
- `docs/TECH_DEBT.md`
- `tasks/todo.md`

## 验证矩阵

- RED：`python3 scripts/validate_model_contracts.py .`
- FastAPI 目标：`cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/runtime_api_contracts/test_dict_write_contracts.py tests/test_dict_service.py tests/test_dict_items.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- Django 目标：`cd backend && uv run pytest drf_admin/utils/test_model_contracts.py drf_admin/utils/runtime_api_contracts/test_dict_write_contracts.py -q`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 通用：`git diff --check`

## 风险与预想失败场景

- FastAPI schema 如果不加 `max_length=32`，ORM 层虽然收敛，但 API 边界仍会接受过长输入，直到数据库层失败。
- 既有测试样例如果生成超过 32 字符的 `label/value`，需要改成业务等价的短样例，而不是放宽契约。
- 已有 FastAPI 数据库中如果存在 33-50 字符的字典项，需要部署前显式清理；本轮不在业务代码中加入兼容分支。
- `sort` 字段仍然是剩余模型债务，本轮完成后不能把整个字典项模型治理声明为结束。

## HARD-GATE

用户已确认“按顺序推进”，本计划作为下一轮治理切片。若执行中发现 `label/value` 长度收敛必须同时改变前端交互或 `sort` 行为，应停止并回到规划阶段。

## 进度记录

- 待执行。

## Review 小结

- 待 review-gate 后补充。
