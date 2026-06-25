# FastAPI 日志 API 路由拆分治理计划

## 目标

- 将 `fastapi/app/api/v1/system/logs.py` 从 353 行职责混合文件拆分为小路由模块。
- 保持 `/api/v1/system/logs/page`、`/visit-trend`、`/visit-stats`、`/{ids}`、`/clear/{days}` 路径和权限不变。
- 保留 `app.api.v1.system.logs.router` 兼容入口，避免修改上层系统路由注册。

## 非目标

- 不修改 `log_service` 运行时行为。
- 不改变日志 API 路径、请求参数、响应格式、权限码或前端契约。
- 不调整日志测试断言或新增业务逻辑 fallback。

## 当前事实

- `fastapi/app/api/v1/system/logs.py` 当前 353 行，是当前 FastAPI 最大运行时代码文件。
- 文件内同时包含日志分页查询、访问趋势、访问统计、批量删除和历史清理 5 个端点。
- `fastapi/app/api/v1/system/__init__.py` 通过 `from app.api.v1.system.logs import router as logs_router` 注册日志路由。
- `fastapi/tests/test_logs.py` 已覆盖上述端点的未授权、授权访问和基础响应契约。

## 决策日志

- 方案 A：新增 `log_routes/` 包，按 `query.py`、`analytics.py`、`mutation.py` 拆分端点，`logs.py` 只聚合子路由。
  - 优点：上层导入兼容，端点按读、统计、写操作分组，单文件体量可控。
  - 缺点：新增包和文件，需要确认 `include_router` 不改变路径。
- 方案 B：直接把上层 `system/__init__.py` 改为注册多个子 router。
  - 优点：省掉聚合入口。
  - 缺点：影响上层路由注册，扩大变更面。
- 方案 C：只删除 OpenAPI 长描述压缩行数。
  - 优点：改动很小。
  - 缺点：没有解决路由职责耦合，只是把体量问题藏起来。

推荐方案：采用方案 A。本轮只拆路由组织，保留 `logs.py` 聚合入口和全部对外契约。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/api/v1/system/log_routes/query.py`，迁移日志分页端点。
- [x] P3 串行：新增 `fastapi/app/api/v1/system/log_routes/analytics.py`，迁移访问趋势和访问统计端点。
- [x] P4 串行：新增 `fastapi/app/api/v1/system/log_routes/mutation.py`，迁移批量删除和历史清理端点。
- [x] P5 串行：新增 `fastapi/app/api/v1/system/log_routes/__init__.py`，聚合子路由。
- [x] P6 串行：收缩 `fastapi/app/api/v1/system/logs.py` 为兼容路由入口。
- [x] P7 串行：执行目标日志 API 测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_logs.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

日志 API 路由拆分已完成：`logs.py` 已从 353 行收缩为 9 行兼容路由入口；日志分页、访问趋势/统计、批量删除/历史清理分别迁移到 `log_routes/query.py`、`log_routes/analytics.py`、`log_routes/mutation.py`，并通过 `log_routes/__init__.py` 聚合。上层 `app.api.v1.system.logs.router` 注册方式保持不变。

验证通过：目标日志 API 测试 11 passed；FastAPI `make quality` 539 passed，覆盖率 85.55%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整日志 API 路由组织，不改变日志 API 路径、请求参数、响应格式、权限码或前端契约；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后所有新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API 契约或产品文档事实；剩余风险是 OpenAPI 长描述较原文件更精简，若后续要求恢复完整接口说明，应单独做 API 文档内容校准。
