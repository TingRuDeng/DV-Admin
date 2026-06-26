# FastAPI 请求日志中间件拆分治理计划

## 目标

- 将 `fastapi/app/middleware/logging_middleware.py` 从 329 行职责混合文件拆分为小模块。
- 保留 `app.middleware.logging_middleware.RequestLoggingMiddleware` 兼容导入入口，避免影响 `fastapi/app/middleware/__init__.py` 和 `fastapi/app/main.py`。
- 为路径排除、User-Agent 解析、请求体读取和兼容导入补充直接单元测试。

## 非目标

- 不修改 FastAPI 中间件注册顺序。
- 不改变请求 ID 生成、响应头写入、日志级别选择或敏感路径请求体排除语义。
- 不新增 mock 假成功、静默 fallback 或日志失败吞错逻辑。

## 当前事实

- `fastapi/app/middleware/logging_middleware.py` 当前 329 行，包含 `RequestLoggingMiddleware` 的路径排除、敏感 body 排除、客户端 IP、User-Agent 解析、请求体读取、响应体重建和主 `dispatch`。
- `fastapi/app/middleware/__init__.py` 从 `app.middleware.logging_middleware` 导入 `RequestLoggingMiddleware`。
- `fastapi/app/main.py` 通过 `app.middleware` 注册 `RequestLoggingMiddleware`。
- `fastapi/tests/test_logging_sensitive_paths.py` 当前只覆盖敏感 body 路径和自定义路径隔离。

## 决策日志

- 方案 A：新增 `request_logging/` 包，按 `constants.py`、`client.py`、`body.py`、`middleware.py` 拆分，旧 `logging_middleware.py` 只做兼容导出。
  - 优点：职责边界清晰，兼容入口稳定，后续可独立补 body、UA、响应日志测试。
  - 缺点：新增包和测试面，改动比单文件 helper 拆分略多。
- 方案 B：只在原文件内提取 helper 函数。
  - 优点：改动小。
  - 缺点：文件仍大且职责仍集中，不能解决长期维护问题。
- 方案 C：重写为统一日志事件服务。
  - 优点：抽象更统一。
  - 缺点：会扩大设计边界，影响现有日志字段和风险面。

推荐方案：采用方案 A。本轮只拆组织和锁行为，不改变运行时注册方式和日志字段语义。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/middleware/request_logging/constants.py`，迁移路径常量。
- [x] P3 串行：新增 `fastapi/app/middleware/request_logging/client.py`，迁移客户端 IP 与 User-Agent 解析。
- [x] P4 串行：新增 `fastapi/app/middleware/request_logging/body.py`，迁移请求体读取与响应体复制。
- [x] P5 串行：新增 `fastapi/app/middleware/request_logging/middleware.py`，迁移 `RequestLoggingMiddleware` 主流程。
- [x] P6 串行：收缩 `fastapi/app/middleware/logging_middleware.py` 为兼容导出入口。
- [x] P7 串行：扩展请求日志中间件目标测试。
- [x] P8 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P9 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_logging_sensitive_paths.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile fastapi/app/middleware/request_logging/*.py fastapi/app/middleware/logging_middleware.py`
- `git diff --check`

## Review 小结

请求日志中间件拆分已完成：`logging_middleware.py` 已从 329 行收缩为 9 行兼容导出入口；默认排除路径、客户端 IP 与 User-Agent 解析、body 读取/响应复制、主中间件流程分别拆入 `request_logging/constants.py`、`request_logging/client.py`、`request_logging/body.py`、`request_logging/middleware.py`。历史导入路径 `app.middleware.logging_middleware.RequestLoggingMiddleware` 保持可用。

验证通过：目标请求日志测试 11 passed；FastAPI `make quality` 551 passed，覆盖率 87.04%；`python3 scripts/validate_docs.py . --profile generic` 通过；`python3 -m py_compile fastapi/app/middleware/request_logging/*.py fastapi/app/middleware/logging_middleware.py` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整请求日志中间件内部组织和补充目标测试，不改变 FastAPI 中间件注册顺序、请求 ID 生成、响应头写入、日志级别选择或敏感路径请求体排除语义；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，新增运行时代码文件均低于 300 行，旧兼容入口降至 9 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/tests/test_import_django_data.py`、`fastapi/tests/test_health.py` 仍超过 300 行，需要后续独立治理。
