# 字典字段命名统一计划

## 目标

- 将 FastAPI 字典主表内部字段从 `code/desc` 逐步统一到 Django 语义 `dict_code/remark`。
- 保持前端 API 契约不变：请求继续接受 `dictCode/remark`，响应继续输出 `dictCode/remark`。
- 减少 Django fixture 导入时的字段别名映射，降低双后端模型迁移和数据同步复杂度。

## 非目标

- 本轮不修改 FastAPI 表名 `system_dict_data`。
- 本轮不修改字典项外键字段 `dict_data`。
- 本轮不改变前端调用、API 路径、响应字段或权限契约。
- 本轮不移除所有历史字段兼容逻辑；删除兼容路径必须有测试证明无调用依赖。

## 当前事实

- `fastapi/app/db/models/system.py` 中 `DictData` 当前字段是 `code` 与 `desc`，表名仍为 `system_dict_data`。
- `backend/drf_admin/apps/system/models.py` 中 Django `Dicts` 字段是 `dict_code` 与 `remark`，表名为 `system_dicts`。
- `fastapi/app/schemas/system.py` 中 `DictDataBase`、`DictDataUpdate` 和 `DictDataOut` 已通过 Pydantic alias 接受 `dictCode/remark` 并序列化为前端字段，因此内部 ORM 字段名调整不必改变前端 API。
- `fastapi/app/db/import_django_data.py` 当前 `FIELD_MAPPING` 仍包含 `dict_code -> code`，说明导入链路依赖字段别名。
- `scripts/model_contracts.py` 当前 `field_aliases` 仍记录 `dict_code -> code`、`remark -> desc`，说明共享模型契约仍在登记差异而不是约束一致。

## 设计原则

- 先统一内部模型语义，再考虑表名迁移。
- API 边界保持稳定，内部字段变化通过 schema/service 层吸收。
- 使用 RED 测试先暴露别名债，再最小实现。
- 不增加静默 fallback；如果旧字段仍需兼容，必须显式、有测试、有清理计划。

## 方案对比

### 方案 A：继续保留 `code/desc`，只强化别名契约

- 优点：风险最低，不影响 service 和测试。
- 缺点：继续扩大模型差异债，无法减少导入脚本和契约别名复杂度。

### 方案 B：一次性统一字段名和表名

- 优点：能一次性解决字典主表大部分差异。
- 缺点：同时触碰 ORM 字段、表名、数据迁移、导入脚本和索引契约，风险过大，不利于定位失败。

### 方案 C：先统一 ORM 字段名，表名后置

- 优点：能消除 `dict_code -> code`、`remark -> desc` 字段别名债，同时不触碰数据库表名迁移。
- 缺点：需要修改 service、schema 输出组装、导入脚本、模型契约和测试。

## 推荐方案

推荐方案 C。

本轮优先将 FastAPI `DictData.code` 改为 `DictData.dict_code`，`DictData.desc` 改为 `DictData.remark`；schema 继续对外暴露 `dictCode/remark`。表名 `system_dict_data` 保持不变，避免把字段命名治理和数据库表迁移混在一个 PR。

## 执行计划

- [ ] P1 串行：RED 补共享字段别名治理测试，复现 `system.dicts` 仍存在 `dict_code -> code`、`remark -> desc` 映射。
- [ ] P2 串行：GREEN 更新 FastAPI `DictData` 字段名、schema/service/import 映射和模型契约。
- [ ] P3 串行：修正 FastAPI 字典相关测试、golden fixture 断言和运行时契约样例。
- [ ] P4 串行：执行模型契约校验、FastAPI 目标测试、FastAPI `make quality`、Django 目标测试和根目录校验。
- [ ] P5 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `scripts/model_contracts.py`
- `scripts/model_field_contracts.py`
- `scripts/model_field_constraint_contracts.py`
- `scripts/model_index_contracts.py`
- `fastapi/app/db/models/system.py`
- `fastapi/app/db/import_django_data.py`
- `fastapi/app/services/system/dict_service.py`
- `fastapi/app/schemas/system.py`
- `fastapi/tests/test_import_django_model_contracts.py`
- `fastapi/tests/test_import_django_data.py`
- `fastapi/tests/test_import_django_data_golden.py`
- `fastapi/tests/test_dict_service.py`
- `fastapi/tests/runtime_api_contracts/test_dict_write_contracts.py`
- `tasks/todo.md`

## 验证矩阵

- RED：`uv run pytest tests/test_import_django_model_contracts.py -q`
- FastAPI 目标：`uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py tests/test_dict_service.py tests/runtime_api_contracts/test_dict_write_contracts.py -q`
- FastAPI 全量：`make quality`
- Django 目标：`uv run pytest drf_admin/utils/test_model_contracts.py -q`
- 根目录：`python3 scripts/validate_model_contracts.py .`
- 根目录：`python3 scripts/validate_docs.py . --profile generic`
- 根目录：`python3 scripts/validate_api_contracts.py .`
- 根目录：`python3 scripts/validate_route_components.py .`
- 根目录：`python3 scripts/validate_django_migrations.py .`
- 通用：`git diff --check`

## 风险与预想失败场景

- Tortoise ORM 字段改名可能影响查询条件、反向关系、索引声明和序列化组装。
- 如果 schema 仍输出 `code/desc`，会破坏前端 API 契约；必须用运行时 API 契约测试覆盖。
- Django fixture 导入脚本如果仍保留 `dict_code -> code`，会把数据写入不存在字段；必须由导入测试暴露。
- 如果测试中直接访问 `DictData.code`，需要改为内部字段 `dict_code`，但对外断言仍应使用 `dictCode`。

## HARD-GATE

用户确认前，不进行任何业务代码、测试代码或契约代码修改。本文件只是规划草案。
