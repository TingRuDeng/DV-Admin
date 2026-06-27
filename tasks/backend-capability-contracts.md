# API 能力边界契约

## 目标

把操作日志“FastAPI 独占能力”从文档描述推进为可校验契约，避免后续误把 `/api/v1/system/logs/*` 当作双后端共享 API。

## 非目标

- 不补 Django `OperationLog` 模型。
- 不新增数据库迁移。
- 不改前端日志页行为。
- 不改 FastAPI 日志接口实现。

## 当前事实

- FastAPI 已提供 `OperationLog` 模型和 `/api/v1/system/logs/*` 查询、统计、删除接口。
- Django 当前只有 `OperationLogMiddleware` 文件日志输出，没有等价数据库审计日志模型或可查询 API。
- 前端日志页已对日志分页接口 404/405 显示后端能力不可用提示。

## 决策日志

- 采用能力边界契约，不把单后端独占接口混入共享 API 契约。
- 首批只登记操作日志域，后续发现新的单后端独占能力再扩展目录。

## 执行计划

- [x] P1 串行：建立任务记录并更新活跃任务状态。
- [x] P2 串行：新增 API 能力边界契约目录。
- [x] P3 串行：扩展 API 契约校验器和双后端治理测试。
- [x] P4 串行：同步文档和技术债状态。
- [x] P5 串行：执行验证并完成 review-gate。

## 验证结果

- `python3 -m py_compile scripts/api_capability_contracts.py scripts/validate_api_contracts.py scripts/api_contract_validation_rules.py`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `cd backend && uv run pytest drf_admin/utils/test_api_capability_contracts.py`：1 passed。
- `cd fastapi && uv run pytest tests/test_api_capability_contracts.py`：1 passed。
- `cd backend && uv run ruff check .`：通过。
- `cd fastapi && uv run ruff check . --ignore I`：通过。
- `git diff --check`：通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只新增 API 能力边界契约、根校验入口、双后端治理测试和文档同步，不新增 Django `OperationLog` 模型、迁移或日志 API，不改变前端日志页行为，也不改 FastAPI 日志接口实现；安全检查未发现新增 secret；复杂度检查通过，新增文件均小于 300 行；Document-refresh: needed，原因：能力边界契约入口和操作日志债务进展已同步到 `docs/API_ENDPOINTS.md`、`docs/ARCHITECTURE.md` 和 `docs/TECH_DEBT.md`；剩余风险是 Django 操作日志查询能力仍未实现，后续需单独决策是否补齐后端能力。
