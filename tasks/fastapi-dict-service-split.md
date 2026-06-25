# FastAPI 字典服务拆分治理计划

## 目标

- 将 `fastapi/app/services/system/dict_service.py` 从单个 474 行服务文件拆分为职责清晰的小模块。
- 保持现有导入入口 `app.services.system.dict_service.dict_service` 不变，避免影响 API 层和测试层调用。
- 不改变数据库结构、对外 API、权限码、响应字段或缓存语义。

## 非目标

- 不拆分 `fastapi/app/schemas/system.py`，该文件后续单独治理。
- 不拆分 `fastapi/app/db/models/system.py`，避免本轮同时影响 ORM 注册边界。
- 不新增兼容 fallback，不引入 mock 成功路径，不调整业务行为。

## 当前事实

- `fastapi/app/services/system/dict_service.py` 当前 474 行，包含 `DictService`、缓存清理、字典类型 CRUD、字典项 CRUD、扁平字典项接口和按编码缓存查询。
- API 调用集中在 `fastapi/app/api/v1/system/dicts.py` 与 `fastapi/app/api/v1/system/dict_items.py`，均导入 `dict_service` 实例。
- 服务测试已拆分为 `fastapi/tests/test_dict_service_dicts.py`、`fastapi/tests/test_dict_service_items.py`、`fastapi/tests/test_dict_service_item_flat.py` 和 `fastapi/tests/dict_service_fixtures.py`。
- PR #172 已合并测试拆分，PR #173 已合并状态记录，远端三条质量门禁均通过。

## 决策日志

- 方案 A：按领域拆成 `dict_type_service.py`、`dict_item_service.py`、`dict_item_flat_service.py`，再由 `dict_service.py` 组合导出统一实例。
  - 优点：职责边界清楚，单文件容易低于 300 行；外部导入路径不变。
  - 缺点：会增加内部模块数量，需要显式共享缓存清理和输出构造 helper。
- 方案 B：保留单类，只把 helper 函数拆出到工具模块。
  - 优点：外部变化最少。
  - 缺点：主文件仍承载过多业务方法，不能真正解决服务职责膨胀。
- 方案 C：直接改 API 层分别依赖多个服务实例。
  - 优点：领域依赖更显式。
  - 缺点：影响 API 层和测试层导入面更大，本轮收益不足。

推荐方案：采用方案 A，但保留 `dict_service.py` 作为兼容聚合入口；先拆内部职责，再由现有测试证明行为不变。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/services/system/dict_cache.py`，承接缓存清理与按编码缓存读取共享逻辑。
- [x] P3 串行：新增 `fastapi/app/services/system/dict_type_service.py`，迁移字典类型分页、详情、创建、更新、删除和批量删除。
- [x] P4 串行：新增 `fastapi/app/services/system/dict_item_service.py`，迁移嵌套字典项分页、列表、创建、更新和删除。
- [x] P5 串行：新增 `fastapi/app/services/system/dict_item_flat_service.py`，迁移扁平字典项创建、更新、删除、批量删除和按编码查询。
- [x] P6 串行：将 `dict_service.py` 收缩为聚合服务入口，保持 `dict_service` 实例导出不变。
- [x] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [x] P8 串行：执行 review-gate。
- [ ] P9 串行：提交、推送、创建 PR 并等待 CI。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_dict_service_dicts.py tests/test_dict_service_items.py tests/test_dict_service_item_flat.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

Review-gate：finished。Spec 符合度通过，本轮只拆分 FastAPI 字典服务内部职责，不改变数据库结构、对外 API、权限码、响应字段或缓存语义；`dict_service` 导入入口保持不变。安全检查未发现本轮新增 secret、mock、fallback 或静默降级，敏感词扫描命中仅来自 `tasks/todo.md` 历史摘要。测试与验证通过：目标字典服务测试 49 passed；FastAPI `make quality` 通过，539 passed，覆盖率 84.84%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。复杂度检查通过，`dict_service.py` 从 474 行降至 15 行，新增服务文件均低于 300 行。Document-refresh: not-needed，原因：本轮是内部服务结构拆分，不改变用户可见 API、数据库结构或产品文档事实。剩余风险是 `fastapi/app/schemas/system.py` 与 `fastapi/app/db/models/system.py` 仍为既有超大文件，需要后续独立治理。
