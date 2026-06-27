# PageContent 表格操作状态抽取

## 现状分析

- `frontend/src/components/CURD/PageContent.vue` 当前 404 行，仍同时承担表格渲染、行选择、删除确认、操作列分发、行内修改、导入导出和公开方法组合。
- 本轮只抽取表格选择、删除、操作列和行内修改逻辑，不触碰导入导出与分页筛选逻辑。

## 功能点

- [x] P1 串行：新增 `usePageContentTableActions.ts`，承接 `selectionData/removeIds/getSelectionData/handleSelectionChange/handleDelete/handleOperate/handleModify`。
- [x] P2 串行：更新 `PageContent.vue`，只保留表格动作 composable 组合和模板事件绑定。
- [x] P3 串行：新增 composable 单元测试，覆盖选择、批量删除、指定行删除、无删除配置、操作列透传、行内修改。
- [x] P4 串行：执行最小充分验证与 review-gate。
- [ ] P5 串行：提交、推送、创建 PR，远端门禁通过后合并并记录状态。

## 风险与决策

- 不并行：改动集中在同一组件和同一组状态，串行可避免写冲突。
- 删除确认仍使用 Element Plus 全局消息与确认框，保持现有交互语义。
- `catch(() => {})` 属于历史取消确认和请求失败行为，本轮不改变错误暴露策略，避免扩大行为面。

## 验证计划

- `cd frontend && pnpm run test:unit -- use-page-content-table-actions curd-deprecation-governance`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run quality`
- `cd frontend && pnpm run build`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## Review-gate 小结

终态：finished；Spec 符合度通过，本轮只抽取 `PageContent.vue` 的表格选择、删除、操作列分发和行内修改逻辑，导入导出、分页、筛选、公开类型和 `defineExpose()` 保持不变；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证已通过定向单测、类型检查、lint、前端 quality、前端 build、文档校验、脚本编译和 diff 检查；复杂度检查通过，新增 composable 88 行、测试 150 行、任务计划 31 行，`PageContent.vue` 从 404 行降至 345 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构、启动方式或产品文档事实；剩余风险是 `PageContent.vue` 仍超过 300 行，后续应继续抽取导入导出或列初始化职责。
