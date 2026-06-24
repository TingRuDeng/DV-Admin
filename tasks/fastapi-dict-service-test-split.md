# FastAPI 字典服务测试拆分计划

## 目标

- 将 `fastapi/tests/test_dict_service.py` 从 728 行拆分到多个职责清晰、单文件低于 300 行的测试文件。
- 保持现有 `DictService` 行为测试覆盖不变，先降低测试维护成本，再为后续拆分 `fastapi/app/services/system/dict_service.py` 做铺垫。
- 让字典主表、字典项嵌套路由、字典项扁平路由和按编码查询测试各自拥有清晰边界。

## 非目标

- 本轮不修改 `fastapi/app/services/system/dict_service.py` 的运行时代码。
- 本轮不修改 `fastapi/app/schemas/system.py` 或字典 API 路由。
- 本轮不改变任何测试断言语义、fixture 数据语义或业务排序规则。
- 本轮不引入 mock、fallback、静默兼容或跳过测试。

## 当前事实

- `fastapi/tests/test_dict_service.py` 当前 728 行，超过仓库单文件 300 行约束。
- 该文件同时覆盖字典主表 CRUD、字典项分页/列表、嵌套字典项 CRUD、扁平字典项 CRUD、批量删除和按编码查询。
- 共享 fixture `test_dict_data_for_service`、`test_dict_item_for_service` 当前位于同一测试文件顶部。
- `fastapi/app/services/system/dict_service.py::DictService` 当前 474 行，后续拆分服务前需要保留可读、可定位的目标测试。

## 设计原则

- 先拆测试，后拆实现；先让验证网更清楚，再动运行时代码。
- 只按业务职责拆文件，不做测试逻辑重写。
- fixture 只抽到共享夹具文件中一次，避免多个测试文件复制创建逻辑。
- 每个新测试文件保持小于 300 行，并让类名继续表达原测试意图。

## 决策驱动因素

- 拆 `DictService` 实现前，如果测试仍集中在 728 行文件里，失败定位成本高。
- 字典主表和字典项是两个自然边界，字典项内部又分嵌套路由、扁平路由和按编码查询。
- 只拆测试文件不会改变产品行为，适合作为低风险的第一轮结构治理。

## 方案对比

### 方案 A：一次性同时拆测试和 service

- 优点：一次完成全部字典模块结构治理。
- 缺点：同时移动测试和运行时代码，失败时难以判断是拆分测试、导入路径还是业务行为变化导致。

### 方案 B：先拆 `test_dict_service.py`

- 优点：风险低，行为不变；后续拆 service 时测试反馈更聚焦。
- 缺点：本轮不能直接降低 `dict_service.py` 的运行时代码复杂度。

### 方案 C：只在文档记录超大文件

- 优点：零代码变更风险。
- 缺点：不能解决 728 行测试文件的维护问题，也不能改善后续重构反馈质量。

## 推荐方案

采用方案 B。先把 `fastapi/tests/test_dict_service.py` 拆成多个测试文件和共享夹具文件，确保测试语义不变、文件大小达标、FastAPI 质量门禁通过。后续再单独规划拆分 `DictService` 实现。

## 执行计划

- [ ] P1 串行：RED 增加或执行文件大小治理检查，确认 `fastapi/tests/test_dict_service.py` 超过 300 行。
- [ ] P2 串行：抽出共享 fixture 到 `fastapi/tests/dict_service_fixtures.py` 或等价专用夹具模块，并确认导入路径清晰。
- [ ] P3 串行：拆出字典主表测试到 `fastapi/tests/test_dict_service_dicts.py`。
- [ ] P4 串行：拆出字典项嵌套路由测试到 `fastapi/tests/test_dict_service_items.py`。
- [ ] P5 串行：拆出字典项扁平路由与按编码查询测试到 `fastapi/tests/test_dict_service_item_flat.py`。
- [ ] P6 串行：删除或缩减原 `fastapi/tests/test_dict_service.py`，确保所有新测试文件低于 300 行。
- [ ] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 涉及文件

- `fastapi/tests/test_dict_service.py`
- `fastapi/tests/test_dict_service_dicts.py`
- `fastapi/tests/test_dict_service_items.py`
- `fastapi/tests/test_dict_service_item_flat.py`
- `fastapi/tests/dict_service_fixtures.py`
- `tasks/todo.md`

## 验证矩阵

- RED/目标：`cd fastapi && uv run pytest tests/test_dict_service.py -q`
- GREEN 目标：`cd fastapi && uv run pytest tests/test_dict_service_dicts.py tests/test_dict_service_items.py tests/test_dict_service_item_flat.py -q`
- FastAPI 全量：`cd fastapi && make quality`
- 文档：`python3 scripts/validate_docs.py . --profile generic`
- 通用：`git diff --check`
- 文件大小：`wc -l fastapi/tests/test_dict_service*.py fastapi/tests/dict_service_fixtures.py`

## 风险与预想失败场景

- fixture 放入普通模块后，pytest 可能不会自动发现；需要显式导入或放到合适的 fixture 文件。
- 拆分后如果文件名或测试名重复不清晰，失败定位反而变差。
- 如果只移动部分测试，原文件可能仍超过 300 行；必须用 `wc -l` 验证。
- FastAPI `make quality` 可能暴露 import order 或未使用导入，需要按现有 ruff/isort 规则修正。

## HARD-GATE

当前仅完成规划。用户确认前不进行测试文件拆分或运行时代码修改。

## 进度记录

- 规划中。

## Review 小结

- 待执行完成后补充。
