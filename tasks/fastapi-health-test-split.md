# FastAPI 健康检查测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_health.py` 从 315 行职责混合测试拆分为小测试文件。
- 保留现有断言语义，覆盖健康检查 HTTP 端点、数据库检查、Redis 检查和 readiness 聚合逻辑。
- 降低单个测试文件体量，避免健康检查测试继续堆叠。

## 非目标

- 不修改 `fastapi/app/api/health.py` 运行时代码。
- 不改变 `/health`、`/health/live`、`/health/ready` 响应契约。
- 不新增 mock 假成功、静默 fallback 或跳过测试逻辑。

## 当前事实

- `fastapi/tests/test_health.py` 当前 315 行，是当前 FastAPI 最大测试文件。
- 文件内同时包含 HTTP 端点测试、`check_database`、`check_redis` 和 `readiness_check` 的直接单元测试。
- `fastapi/app/api/health.py` 暴露 `/health`、`/health/ready`、`/health/live` 三个端点，并包含数据库和 Redis 依赖检查函数。

## 决策日志

- 方案 A：按职责拆为 `test_health_endpoints.py`、`test_health_database.py`、`test_health_redis.py`、`test_health_readiness.py`，删除原大文件。
  - 优点：职责边界清楚，单文件体量小，不改变测试行为。
  - 缺点：新增文件数量较多。
- 方案 B：只拆 Redis 和 readiness 两段。
  - 优点：改动较小。
  - 缺点：主文件仍较大，后续扩展容易再次超过 300 行。
- 方案 C：合并到 API 契约测试。
  - 优点：文件数量少。
  - 缺点：健康检查依赖状态和 API 契约职责混淆。

推荐方案：采用方案 A。本轮只拆测试组织，不改变运行时代码和断言语义。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/test_health_endpoints.py`，迁移 HTTP 端点测试。
- [x] P3 串行：新增 `fastapi/tests/test_health_database.py`，迁移数据库检查测试。
- [x] P4 串行：新增 `fastapi/tests/test_health_redis.py`，迁移 Redis 检查测试。
- [x] P5 串行：新增 `fastapi/tests/test_health_readiness.py`，迁移 readiness 聚合测试。
- [x] P6 串行：删除旧 `fastapi/tests/test_health.py`。
- [x] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_health_endpoints.py tests/test_health_database.py tests/test_health_redis.py tests/test_health_readiness.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 健康检查测试拆分已完成：原 315 行 `fastapi/tests/test_health.py` 已删除，HTTP 端点、数据库检查、Redis 检查、readiness 聚合分别迁移到 `fastapi/tests/test_health_endpoints.py`、`fastapi/tests/test_health_database.py`、`fastapi/tests/test_health_redis.py`、`fastapi/tests/test_health_readiness.py`。
- 验证通过：目标健康检查测试 `18 passed`；FastAPI `make quality` 通过，结果为 `551 passed`、覆盖率 `87.04%`；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。
- Review-gate：finished；Spec 符合度通过，本轮只调整测试组织，不修改 `fastapi/app/api/health.py`、健康检查 API 路径或响应契约；安全检查未发现新增 secret、mock 假成功、静默 fallback 或跳过测试；复杂度检查通过，新增测试文件均小于 300 行。
- Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构、启动方式或产品文档事实。
- 剩余风险：本轮只治理健康检查测试文件；后续继续做文件体量治理时，可优先评估 `fastapi/app/services/token_blacklist.py` 或 `fastapi/app/services/system/log_service.py` 等接近 300 行的业务文件。
