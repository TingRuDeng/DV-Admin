# PageContent 远程筛选状态抽取

## 目标

将 `frontend/src/components/CURD/PageContent.vue` 中的远程筛选参数转换和缓存逻辑抽到独立 composable，继续降低历史兼容层组件职责密度。

## 现状证据

- `PageContent.vue` 直接维护 `filterParams`。
- `handleFilterChange()` 同时负责根据列配置转换 Element Plus 过滤值、合并筛选参数并触发 `filterChange` 事件。
- `getFilterParams()` 暴露筛选参数给外部调用，属于兼容层公开能力，需要保持不变。

## 执行计划

- [x] P1 串行：新增 `frontend/src/components/CURD/usePageContentFilters.ts`，承接筛选参数转换、缓存和读取。
- [x] P2 串行：更新 `frontend/src/components/CURD/PageContent.vue`，改为通过 composable 获取 `handleFilterChange` 和 `getFilterParams`，并保持外部事件 payload 不变。
- [x] P3 串行：新增 `frontend/src/components/CURD/__tests__/use-page-content-filters.spec.ts`，覆盖普通筛选、`filterJoin` 拼接、columnKey 兼容和增量合并。
- [x] P4 串行：运行前端目标测试、类型检查、lint、聚合质量检查、构建、文档校验和 diff 检查。
- [ ] P5 串行：完成 review-gate，并在 `tasks/todo.md` 记录合并状态。

## 并行策略

本轮不启用 subagent。原因：改动集中在同一组件及其筛选 composable，串行推进可避免同文件写冲突。

## 验证命令

```bash
cd frontend && pnpm run test:unit -- use-page-content-filters curd-deprecation-governance
cd frontend && pnpm run type-check
cd frontend && pnpm run lint:check
cd frontend && pnpm run quality
cd frontend && pnpm run build
python3 scripts/validate_docs.py . --profile generic
python3 -m py_compile scripts/validate_docs.py
git diff --check
```

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只抽取 `PageContent.vue` 的远程筛选状态职责，不改变 CURD 兼容层对外 props、emits、`filterChange` payload、`getFilterParams()`、导入导出、删除修改或 `defineExpose()`；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证通过，覆盖目标 composable、CURD 退场守卫、前端类型、lint、完整质量门禁、构建、文档校验、脚本编译和 diff 检查；复杂度检查通过，`PageContent.vue` 从 423 行降至 404 行，新增 composable 37 行、测试 67 行；Document-refresh: not-needed，原因：本轮是内部职责拆分，不改变用户可见功能、API、数据库结构或产品文档事实；剩余风险是 `PageContent.vue` 仍超过 300 行，后续还可继续拆分导入导出业务编排。
