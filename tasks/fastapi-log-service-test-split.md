# FastAPI 日志服务测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_log_service.py` 从 363 行单文件拆分为职责清晰的小测试文件。
- 保持 `LogService` 现有分页、趋势、统计、删除、创建和时间辅助函数断言不变。
- 抽出日志测试共享数据夹具，避免拆分后重复构造操作日志样本。

## 非目标

- 不修改 `fastapi/app/services/system/log_service.py` 运行时代码。
- 不改变日志分页过滤、时间转换、访问趋势、访问统计、删除或创建行为。
- 不调整日志 API、数据库模型、日志中间件或敏感日志策略。

## 当前事实

- `fastapi/tests/test_log_service.py` 当前 363 行，是当前 FastAPI 自有测试中最大的单文件。
- 文件内包含 `TestLogServiceTimeHelpers`、`TestLogServiceGetPage`、`TestLogServiceGetVisitTrend`、`TestLogServiceGetVisitStats`、`TestLogServiceDelete`、`TestLogServiceCreate`。
- 共享夹具 `test_logs` 和 `test_logs_with_dates` 同时服务分页、趋势、统计和删除测试。
- `fastapi/app/services/system/log_service.py` 当前 293 行，本轮不处理运行时代码体量。

## 决策日志

- 方案 A：抽 `log_service_fixtures.py`，按 time、query、trend、stats、mutation 拆分测试文件。
  - 优点：边界与行为簇一致，夹具集中复用，新增文件体量可控。
  - 缺点：文件数量增加，需要确认 pytest 插件夹具加载正常。
- 方案 B：只拆访问趋势和访问统计测试，其他保留在原文件。
  - 优点：改动更小。
  - 缺点：原文件仍然偏大，分页、删除、创建仍集中在一个文件。
- 方案 C：同步拆分 `LogService` 运行时代码。
  - 优点：可同时降低服务实现文件体量。
  - 缺点：会把测试组织调整和运行时重构混在一起，扩大风险。

推荐方案：采用方案 A。本轮只拆测试文件和共享夹具，不修改运行时代码。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/log_service_fixtures.py`，迁移 `test_logs` 与 `test_logs_with_dates`。
- [x] P3 串行：新增 `fastapi/tests/test_log_service_time.py`，迁移时间辅助函数测试。
- [x] P4 串行：新增 `fastapi/tests/test_log_service_query.py`，迁移分页查询测试。
- [x] P5 串行：新增 `fastapi/tests/test_log_service_trend.py`，迁移访问趋势测试。
- [x] P6 串行：新增 `fastapi/tests/test_log_service_stats.py`，迁移访问统计测试。
- [x] P7 串行：新增 `fastapi/tests/test_log_service_mutation.py`，迁移删除和创建测试。
- [x] P8 串行：删除原 `fastapi/tests/test_log_service.py`，确保没有重复测试或孤儿引用。
- [x] P9 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P10 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_log_service_time.py tests/test_log_service_query.py tests/test_log_service_trend.py tests/test_log_service_stats.py tests/test_log_service_mutation.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

日志服务测试拆分已完成：原 363 行 `test_log_service.py` 已拆为时间辅助、分页查询、访问趋势、访问统计、删除与创建 5 个职责测试文件，并抽出 `log_service_fixtures.py` 复用日志样本夹具；运行时代码未修改。

验证通过：目标测试 24 passed；FastAPI `make quality` 539 passed，覆盖率 85.44%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整测试组织，不修改运行时代码、API、数据库结构或用户可见流程；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，新增测试文件均小于 300 行；Document-refresh: not-needed，原因：本轮不改变产品文档事实；剩余风险是 `fastapi/app/services/system/log_service.py` 当前接近 300 行，后续若继续增长应单独拆分运行时服务职责。
