# 操作日志前端字段契约阶段 9

## 目标

- 将操作日志前端 API 类型纳入前端字段契约目录。
- 让 `LogPageVO` 显式声明后端 `logs_out` 已锁定的字段集合。

## 非目标

- 不修改后端日志查询、脱敏、数据范围和落库行为。
- 不修改日志页面 UI。
- 不扩展日志 API 功能。

## 当前事实

- `scripts/api_field_contracts.py` 已登记 `logs_out`，并绑定 `logs_page`。
- `frontend/src/api/system/log-api.ts` 当前只声明部分日志字段。
- `scripts/api_frontend_field_contracts.py` 当前尚未登记 `log-api.ts`。

## 决策日志

- 本轮只覆盖操作日志，不同时扩展 `file-api.ts` 或 `information-api.ts`。
- `LogPageVO.userId` 使用 `number | null`，与双后端日志输出可为空的事实一致。

## 执行计划

- [x] 补齐 `LogPageVO` 字段声明。
- [x] 新增 `logs_page_type` 前端字段契约。
- [x] 将 `log-api.ts` 加入前端字段契约治理测试。
- [x] 更新技术债治理进展。
- [x] 执行最小充分验证。

## 进度记录

- 2026-07-06：用户确认计划，创建 `codex/log-frontend-field-contract-stage9` 分支。
- 2026-07-06：补齐操作日志前端字段类型和字段契约登记。

## 验证结果

- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/api_frontend_field_contracts.py`：通过。
- `CI=true pnpm --dir frontend exec vitest run src/api/__tests__/api-frontend-field-contract-governance.spec.ts`：1 passed。
- `CI=true pnpm --dir frontend exec eslint src/api/system/log-api.ts src/api/__tests__/api-frontend-field-contract-governance.spec.ts`：通过。
- `CI=true pnpm --dir frontend run quality`：90 files passed，261 tests passed。
- `CI=true pnpm --dir frontend run build`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只补操作日志前端字段类型与字段契约登记，未修改 API 行为、页面 UI、脱敏规则或后端实现。
