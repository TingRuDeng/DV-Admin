# FastAPI 日志服务拆分治理计划

## 目标

- 将 `fastapi/app/services/system/log_service.py` 从 293 行继续降到更可维护的体量。
- 抽出时间辅助、日志输出转换、访问统计聚合等无状态逻辑，降低 `LogService` 的职责密度。
- 保持 `app.services.system.log_service.log_service`、`LogService`、`local_now` 和 `normalize_local_time` 导入路径不变。

## 非目标

- 不修改日志 API 路由、请求参数、分页响应或统计响应契约。
- 不修改 `OperationLog` 数据模型、数据库表结构或查询语义。
- 不新增 mock 假成功、静默 fallback 或跳过测试逻辑。

## 当前事实

- `fastapi/app/services/system/log_service.py` 当前 293 行，是当前 FastAPI 最大文件。
- 文件内同时包含分页查询、访问趋势、访问统计、TOP 用户/路径聚合、删除、清理、创建和时间辅助函数。
- `fastapi/app/api/v1/system/log_routes/` 通过 `log_service` 调用该服务，测试已按 query、trend、stats、mutation、time 分层覆盖。

## 决策日志

- 方案 A：新增 `log_time.py`、`log_serializers.py`、`log_stats_helpers.py`，迁移无状态 helper，`log_service.py` 保留服务编排和兼容导入。
  - 优点：改动小，外部导入路径稳定，直接降低服务类职责密度。
  - 缺点：服务文件仍承载多个业务方法，后续若继续扩展仍需按查询/写操作进一步拆分。
- 方案 B：将 `log_service.py` 改成 package，按 query、analytics、mutation 拆服务类。
  - 优点：职责拆分更彻底。
  - 缺点：模块到 package 的迁移会影响导入路径、测试 patch 路径和调用方，当前只需治理体量与职责密度。
- 方案 C：只压缩注释或格式。
  - 优点：diff 小。
  - 缺点：不能改善职责边界，不解决长期可持续性问题。

推荐方案：采用方案 A。本轮保持运行时契约稳定，只拆无状态 helper。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/services/system/log_time.py`，迁移时间辅助函数并在 `log_service.py` 兼容导入。
- [x] P3 串行：新增 `fastapi/app/services/system/log_serializers.py`，迁移 `OperationLogOut` 转换。
- [x] P4 串行：新增 `fastapi/app/services/system/log_stats_helpers.py`，迁移访问趋势和 TOP 聚合 helper。
- [x] P5 串行：更新 `log_service.py` 委托 helper，并保持对外方法行为不变。
- [x] P6 串行：执行日志服务目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P7 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_log_service_query.py tests/test_log_service_trend.py tests/test_log_service_stats.py tests/test_log_service_mutation.py tests/test_log_service_time.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 日志服务拆分已完成：`fastapi/app/services/system/log_service.py` 从 293 行降至 205 行，新增 `log_time.py`、`log_serializers.py`、`log_stats_helpers.py` 承接时间辅助、输出转换和访问统计聚合 helper。
- 验证通过：日志服务目标测试 `24 passed`；FastAPI `make quality` 通过，结果为 `551 passed`、覆盖率 `87.13%`；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。
- Review-gate：finished；Spec 符合度通过，本轮保留 `app.services.system.log_service.log_service`、`LogService`、`local_now` 和 `normalize_local_time` 导入路径，不修改日志 API 路由、分页响应、统计响应、数据模型或查询语义。
- 安全检查未发现新增 secret、mock 假成功、静默 fallback 或跳过测试；复杂度检查通过，本轮新增文件分别为 20、31、72 行，目标文件 205 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只做内部服务职责拆分，不改变对外 API、数据库结构、日志契约或用户可见流程。
- 剩余风险：`fastapi/app/services/system/notice_service.py` 和 `fastapi/app/db/import_django_data.py` 仍为 292 行，后续可继续按职责拆分治理。
