# PageContent 数据分页状态抽取

## 目标

将 `frontend/src/components/CURD/PageContent.vue` 中的数据获取、分页状态、搜索条件缓存和请求参数拼装抽到独立 composable，继续降低历史兼容层组件职责密度。

## 现状证据

- `PageContent.vue` 直接维护 `loading`、`pageData`、`showPagination`、`pagination` 和 `request`。
- `PageContent.vue` 的 `fetchPageData()` 同时处理搜索条件缓存、分页重置、请求参数拼装、响应解析和 loading 状态。
- `handleSizeChange()` 与 `handleCurrentChange()` 直接修改分页状态并触发刷新。

## 执行计划

- [x] P1 串行：新增 `frontend/src/components/CURD/usePageContentData.ts`，承接分页配置、请求参数拼装、数据获取和分页切换。
- [x] P2 串行：更新 `frontend/src/components/CURD/PageContent.vue`，改为通过 composable 获取 `loading`、`pageData`、`pagination`、`showPagination` 和刷新方法。
- [x] P3 串行：新增 `frontend/src/components/CURD/__tests__/use-page-content-data.spec.ts`，覆盖分页请求、非分页请求、parseData、重置页码和分页切换。
- [x] P4 串行：运行前端目标测试、类型检查、lint、聚合质量检查、构建、文档校验和 diff 检查。
- [ ] P5 串行：完成 review-gate，并在 `tasks/todo.md` 记录合并状态。

## 并行策略

本轮不启用 subagent。原因：改动集中在同一组件及其数据 composable，文件之间存在直接依赖，串行推进更稳。

## 验证命令

```bash
cd frontend && pnpm run test:unit -- use-page-content-data curd-deprecation-governance
cd frontend && pnpm run type-check
cd frontend && pnpm run lint:check
cd frontend && pnpm run quality
cd frontend && pnpm run build
python3 scripts/validate_docs.py . --profile generic
python3 -m py_compile scripts/validate_docs.py
git diff --check
```

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只抽取 `PageContent.vue` 的数据分页状态职责，不改变 CURD 兼容层对外 props、emits、`defineExpose()`、导入导出、删除修改或筛选事件契约；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证通过，覆盖目标 composable、CURD 退场守卫、前端类型、lint、完整质量门禁、构建、文档校验、脚本编译和 diff 检查；复杂度检查通过，`PageContent.vue` 从 486 行降至 423 行，新增 composable 95 行、测试 98 行；Document-refresh: not-needed，原因：本轮是内部职责拆分，不改变用户可见功能、API、数据库结构或产品文档事实；剩余风险是 `PageContent.vue` 仍超过 300 行，后续还可继续拆分导入导出业务编排或筛选状态。
