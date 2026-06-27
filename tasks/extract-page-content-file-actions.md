# PageContent 文件动作抽取

## 现状分析

- `frontend/src/components/CURD/PageContent.vue` 当前 345 行，仍承担导入导出弹窗状态、模板下载、单文件导入、批量 Excel 导入、远程导出、本地导出和公开 `exportPageData`。
- 本轮只抽取文件导入导出动作，不触碰表格渲染、分页、筛选、表格操作和 toolbar 分发。

## 功能点

- [x] P1 串行：新增 `usePageContentFileActions.ts`，承接导入导出弹窗状态、导入导出处理、模板下载和公开导出方法。
- [x] P2 串行：更新 `PageContent.vue`，通过 composable 组合文件动作并保留弹窗模板契约。
- [x] P3 串行：新增 composable 单元测试，覆盖远程导出、本地导出、选中导出、模板下载、单文件导入、批量导入空表与读取失败。
- [x] P4 串行：执行最小充分验证与 review-gate。
- [ ] P5 串行：提交、推送、创建 PR，远端门禁通过后合并并记录状态。

## 风险与决策

- 不并行：改动集中在同一组件与文件动作依赖，串行更适合控制行为兼容。
- 保留现有错误提示、日志文案、文件名解析和刷新时机，避免导入导出行为漂移。
- `PageContent.vue` 目标降到 300 行以内，后续再处理列初始化或 toolbar 分发。

## 验证计划

- `cd frontend && pnpm run test:unit -- use-page-content-file-actions curd-deprecation-governance`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run quality`
- `cd frontend && pnpm run build`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## Review-gate 小结

终态：finished；Spec 符合度通过，本轮只抽取 `PageContent.vue` 的文件导入导出动作，表格渲染、分页、筛选、表格操作、toolbar 分发、公开类型和 `defineExpose()` 保持不变；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证已通过定向单测、类型检查、lint、前端 quality、前端 build、文档校验、脚本编译和 diff 检查；复杂度检查通过，`PageContent.vue` 从 345 行降至 223 行，新增 composable 184 行、测试 227 行，新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库结构、启动方式或产品文档事实；剩余风险是 `PageContent.vue` 已低于 300 行，但列初始化和 toolbar 分发仍留在组合层，后续可再按价值决定是否抽取。
