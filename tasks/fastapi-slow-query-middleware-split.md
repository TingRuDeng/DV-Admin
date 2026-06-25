# FastAPI 慢查询中间件拆分治理计划

## 目标

- 将 `fastapi/app/middleware/slow_query_middleware.py` 从 350 行职责混合文件拆分为小模块。
- 保留 `app.middleware.slow_query_middleware` 兼容导入入口，避免影响 `fastapi/app/middleware/__init__.py` 和外部引用。
- 为慢请求统计和数据库慢查询监控补充直接单元测试，锁定拆分后的行为。

## 非目标

- 不修改 `fastapi/app/main.py` 中间件注册顺序。
- 不改变慢请求、非常慢请求、异常慢请求和数据库慢查询的阈值判断语义。
- 不引入新的 fallback、mock 假成功路径或日志吞错逻辑。

## 当前事实

- `fastapi/app/middleware/slow_query_middleware.py` 当前 350 行，包含 `SlowQueryMiddleware`、`DatabaseQueryMonitor` 和全局 `db_query_monitor`。
- `SlowQueryMiddleware.dispatch` 负责跳过路径判断、请求耗时统计、慢请求日志和异常慢请求日志。
- `DatabaseQueryMonitor.log_query` 负责数据库查询计数、慢查询分级、SQL/参数截断和统计重置。
- `fastapi/app/middleware/__init__.py` 从 `app.middleware.slow_query_middleware` 导入 `SlowQueryMiddleware`、`DatabaseQueryMonitor` 和 `db_query_monitor`。
- 当前 `fastapi/tests` 未直接覆盖 `SlowQueryMiddleware` 或 `DatabaseQueryMonitor`。

## 决策日志

- 方案 A：新增 `slow_query/` 包，按 `request.py`、`database.py`、`constants.py` 拆分，旧 `slow_query_middleware.py` 只做兼容导出。
  - 优点：职责边界清晰，兼容入口稳定，后续可独立扩展请求监控和数据库监控。
  - 缺点：新增包和测试文件，改动比单文件内拆 helper 略多。
- 方案 B：只在原文件内提取 helper 函数。
  - 优点：改动小。
  - 缺点：文件仍接近或超过 300 行，职责仍混在同一文件，不能解决长期可维护性问题。
- 方案 C：顺手重写为统一统计服务。
  - 优点：抽象更统一。
  - 缺点：会改变设计边界和测试范围，容易引入非必要行为变化。

推荐方案：采用方案 A。本轮只做模块拆分与行为锁定测试，不改变运行时注册方式和日志语义。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/middleware/slow_query/constants.py`，迁移默认阈值和排除路径常量。
- [x] P3 串行：新增 `fastapi/app/middleware/slow_query/request.py`，迁移 `SlowQueryMiddleware`。
- [x] P4 串行：新增 `fastapi/app/middleware/slow_query/database.py`，迁移 `DatabaseQueryMonitor` 和 `db_query_monitor`。
- [x] P5 串行：收缩 `fastapi/app/middleware/slow_query_middleware.py` 为兼容导出入口。
- [x] P6 串行：新增 `fastapi/tests/test_slow_query_middleware.py`，覆盖请求统计、跳过路径和数据库查询统计。
- [x] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_slow_query_middleware.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile fastapi/app/middleware/slow_query/*.py fastapi/app/middleware/slow_query_middleware.py`
- `git diff --check`

## Review 小结

慢查询中间件拆分已完成：`slow_query_middleware.py` 已从 350 行收缩为 17 行兼容导出入口；HTTP 慢请求中间件、数据库慢查询监控器和常量分别拆入 `slow_query/request.py`、`slow_query/database.py`、`slow_query/constants.py`。历史导入路径 `app.middleware.slow_query_middleware` 保持可用。

验证通过：目标慢查询中间件测试 5 passed；FastAPI `make quality` 544 passed，覆盖率 86.45%；`python3 scripts/validate_docs.py . --profile generic` 通过；`python3 -m py_compile fastapi/app/middleware/slow_query/*.py fastapi/app/middleware/slow_query_middleware.py` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整慢查询中间件内部组织和补充目标测试，不改变中间件注册顺序、阈值判断语义或数据库慢查询统计口径；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，新增运行时代码文件均低于 300 行，旧兼容入口降至 17 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `logging_middleware.py` 仍为 329 行且覆盖率偏低，需要后续独立治理。
