# Django 操作日志能力缺口显式化

## 目标

在不补 Django 数据库操作日志模型和查询 API 的前提下，让前端日志管理页对 Django 后端不支持日志查询的情况给出显式不可用状态，并用测试锁定该能力边界。

## 非目标

- 不新增 Django `OperationLog` 模型。
- 不创建数据库迁移。
- 不改变 FastAPI 日志接口。
- 不把 Django 不支持伪装成空日志查询成功。

## 当前事实

- FastAPI 已提供 `OperationLog` 模型和 `/api/v1/system/logs/*` 查询能力。
- Django 当前只有 `OperationLogMiddleware` 文件日志输出，没有等价数据库查询 API。
- 前端日志页位于 `frontend/src/views/system/log/index.vue`，当前直接请求日志分页接口。

## 决策日志

- 采用小步治理：先显式化产品能力边界，不直接扩大 Django 后端功能面。
- 只把 HTTP 404/405 识别为日志能力不支持；其他错误继续暴露为真实失败。

## 执行计划

- [x] P1 串行：建立任务记录并更新活跃任务状态。
- [x] P2 串行：保留 HTTP 错误状态并新增日志能力识别 helper。
- [x] P3 串行：日志页展示后端不支持状态并补治理测试。
- [x] P4 串行：同步文档和技术债状态。
- [x] P5 串行：执行验证并完成 review-gate。

## 验证结果

- `node_modules/.bin/vitest run src/views/__tests__/log-capability-governance.spec.ts src/views/__tests__/log-style-migration.spec.ts`：2 files / 3 tests passed。
- `node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `node_modules/.bin/vue-tsc --noEmit`：通过。
- `node_modules/.bin/vitest run`：90 files / 261 tests passed。
- `node_modules/.bin/vite build`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `git diff --check`：通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只显式化前端日志页对 Django 操作日志能力缺口的处理，不新增 Django 模型、迁移或日志 API，不改变 FastAPI 日志接口；安全检查未发现新增 secret；测试覆盖包含日志能力 helper、日志页治理、前端质量、构建、文档和 API 契约；复杂度检查通过，新增文件均小于 300 行；Document-refresh: needed，原因：产品能力边界变化已同步到 `docs/API_ENDPOINTS.md`、`docs/ARCHITECTURE.md` 和 `docs/TECH_DEBT.md`；剩余风险是 Django 操作日志查询能力仍未实现，后续需单独决策是否补齐后端能力。
