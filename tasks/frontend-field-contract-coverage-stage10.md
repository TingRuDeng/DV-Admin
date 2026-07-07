# 前端字段契约覆盖守卫阶段 10

## 目标

- 用关键端点证据反向校验前端字段契约覆盖，减少硬编码文件清单维护成本。
- 显式登记不适用普通业务对象字段契约的前端响应端点。

## 非目标

- 不修改 API 行为。
- 不修改前端页面。
- 不为文件上传或登录 token 响应强行建立普通对象字段契约。

## 当前事实

- `scripts/api_frontend_field_contracts.py` 已覆盖高价值系统 API 类型。
- `frontend/src/api/__tests__/api-frontend-field-contract-governance.spec.ts` 仍维护硬编码 API 文件清单。
- `auth_login` 与 `files_upload` 均有前端 API 证据和响应字段，但它们不是普通业务对象字段集合。

## 决策日志

- 将覆盖完整性校验放入 `scripts/api_field_contract_validation.py`，随 `python3 scripts/validate_api_contracts.py .` 执行。
- `auth_login` 和 `files_upload` 作为前端字段契约显式豁免。
- Vitest 只保留入口与关键豁免片段检查，不再维护完整 API 文件清单。

## 执行计划

- [x] 新增前端字段契约豁免目录。
- [x] 接入关键端点证据驱动的前端字段契约覆盖校验。
- [x] 更新 Django/FastAPI 字段契约测试断言。
- [x] 弱化前端治理测试的硬编码文件清单。
- [x] 更新技术债治理进展。
- [x] 执行最小充分验证。

## 进度记录

- 2026-07-07：用户确认计划，创建 `codex/frontend-field-contract-coverage-stage10` 分支。
- 2026-07-07：新增前端字段契约豁免与覆盖完整性守卫。

## 验证结果

- `python3 -m py_compile scripts/api_frontend_field_contracts.py scripts/api_field_contract_validation.py`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `uv run pytest drf_admin/utils/test_api_field_contracts.py -q`：2 passed。
- `uv run pytest tests/test_api_field_contracts.py -q`：2 passed，存在既有 FastAPI 测试环境 warning。
- `CI=true pnpm --dir frontend exec vitest run src/api/__tests__/api-frontend-field-contract-governance.spec.ts`：1 passed。
- `CI=true pnpm --dir frontend run quality`：90 files / 261 tests passed。
- `uv run ruff check drf_admin/utils/test_api_field_contracts.py`：通过。
- `uv run ruff check tests/test_api_field_contracts.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只修改前端字段契约治理脚本、对应测试、技术债和任务记录，未修改业务 API 行为或前端页面。
- `auth_login` 与 `files_upload` 作为非普通业务对象响应显式豁免；`logs_page` 保持受前端字段契约覆盖。
- 根校验器现在会基于关键端点前端证据反查前端字段契约或豁免，避免新增端点静默逃逸。
