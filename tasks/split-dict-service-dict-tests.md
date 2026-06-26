# FastAPI 字典类型服务测试拆分

## 目标

- 将 `fastapi/tests/test_dict_service_dicts.py` 按职责拆为查询与写操作两个测试文件。
- 保持字典类型服务测试断言、fixture 使用和服务调用行为不变。
- 降低单文件维护成本，让后续字典类型查询与写操作测试可以分别扩展。

## 非目标

- 不修改 `dict_service` 运行时代码。
- 不调整字典类型 API、schema、数据库模型或前端调用。
- 不处理 `test_dict_service_item_flat.py` 的后续拆分。
- 不引入新的 mock、fallback、跳过测试或静默降级。

## 当前事实

- 当前分支基于 `master` 最新提交 `c0db00c` 创建。
- `fastapi/tests/test_dict_service_dicts.py` 当前为 251 行，集中覆盖字典类型分页/详情查询、创建、更新、删除和批量删除。
- 共享 fixture 位于 `fastapi/tests/dict_service_fixtures.py`，本轮继续复用，不改 fixture 契约。

## 决策日志

- 方案 A：按 query/mutation 拆成两个文件。
  - 优点：边界清晰、文件数量少、迁移风险低。
  - 缺点：mutation 文件会包含创建、更新、删除和批量删除。
- 方案 B：拆成 query/create/update/delete 四个文件。
  - 优点：职责最细。
  - 缺点：当前总行数 251，拆成四个文件会制造过多碎片，收益不足。
- 结论：采用方案 A。先把查询与写操作分离，保持简单且可维护。

## 执行计划

- [x] 串行：创建 `fastapi/tests/test_dict_service_dict_query.py`，迁移分页查询和详情查询测试。
- [x] 串行：创建 `fastapi/tests/test_dict_service_dict_mutation.py`，迁移创建、更新、删除和批量删除测试。
- [x] 串行：删除原 `fastapi/tests/test_dict_service_dicts.py`。
- [x] 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_dict_service_dict_query.py tests/test_dict_service_dict_mutation.py tests/test_dict_service_item_query.py tests/test_dict_service_item_mutation.py tests/test_dict_service_item_flat.py -q`
- `cd fastapi && uv run ruff check tests/test_dict_service_dict_query.py tests/test_dict_service_dict_mutation.py tests/test_dict_service_item_query.py tests/test_dict_service_item_mutation.py tests/test_dict_service_item_flat.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已建立任务计划。
- 已将字典类型服务测试拆为 query/mutation 两个职责文件。
- 已完成目标测试、FastAPI 聚合质量门禁、文档校验和 diff 检查。

## 验证结果

- `cd fastapi && uv run pytest tests/test_dict_service_dict_query.py tests/test_dict_service_dict_mutation.py tests/test_dict_service_item_query.py tests/test_dict_service_item_mutation.py tests/test_dict_service_item_flat.py -q`：49 passed，3 warnings。
- `cd fastapi && uv run ruff check tests/test_dict_service_dict_query.py tests/test_dict_service_dict_mutation.py tests/test_dict_service_item_query.py tests/test_dict_service_item_mutation.py tests/test_dict_service_item_flat.py`：All checks passed。
- `cd fastapi && make quality`：565 passed，5 warnings，覆盖率 88.05%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只拆分 `fastapi/tests/test_dict_service_dicts.py`，未修改 `dict_service` 运行时代码、字典类型 API、schema、数据库模型或前端调用；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后 query/mutation 两个测试文件分别为 96、158 行，均低于 300 行；Document-refresh: not-needed，原因：本轮是测试结构治理，不改变用户可见 API、数据库事实或产品文档内容；剩余风险是 `test_dict_service_item_flat.py` 仍有 208 行，可作为后续低优先级治理切片。
