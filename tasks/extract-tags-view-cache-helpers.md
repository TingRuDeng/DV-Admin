# TagsView store 缓存 helper 抽取

## 现状分析

- `frontend/src/store/modules/tags-view-store.ts` 当前 280 行，同时承担 Pinia 状态定义、标签增删、缓存数组增删、缓存 key 迁移和导航兜底。
- `frontend/src/store/modules/__tests__/tags-view-store.test.ts` 已覆盖主要 store 行为，但缓存数组规则仍嵌在 store action 内，不便独立验证。
- 本轮目标只抽离缓存数组的纯规则，不改变 `useTagsViewStore` 的返回 API、TagsView 组件调用方式、KeepAlive include 数据结构或路由导航行为。

## 执行计划

- [ ] 新增 `frontend/src/store/modules/tags-view-cache-helpers.ts`，承接缓存新增、删除、仅保留当前标签缓存、更新标签后同步缓存 key 和结果快照构造。
- [ ] 精简 `frontend/src/store/modules/tags-view-store.ts`，保留 Pinia 状态与 action 编排。
- [ ] 新增 `frontend/src/store/modules/__tests__/tags-view-cache-helpers.test.ts`，覆盖缓存 helper 纯规则和 store 文件行数守卫。
- [ ] 执行最小充分验证：目标 Vitest、前端静态检查、类型检查、全量单测、构建、文档校验和 diff 检查。

## 并行策略

- 不启用 subagent。原因：本轮改动集中在同一 store 状态边界，helper 与 store 测试需要同步调整，串行更能避免写冲突。

## 验收标准

- `frontend/src/store/modules/tags-view-store.ts` 明显低于 300 行，职责收敛为 Pinia action 编排。
- 缓存新增、删除、仅保留和更新同步规则有纯 helper 测试覆盖。
- 不改变 TagsView store 公开 action 名称、返回 Promise 形状、KeepAlive 缓存 key 规则或 TagsView 组件行为。

## 验证记录

- `node_modules/.bin/vitest run src/store/modules/__tests__/tags-view-cache-helpers.test.ts src/store/modules/__tests__/tags-view-store.test.ts`：2 files / 10 tests passed。
- `node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `node_modules/.bin/vue-tsc --noEmit`：通过。
- `node_modules/.bin/vitest run`：87 files / 250 tests passed。
- `node_modules/.bin/vite build`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review Gate

- 终态：finished。
- Spec 符合度：通过；只抽取 TagsView 缓存纯规则，未修改 store 公开 action、返回 Promise 形状、KeepAlive include 或 TagsView 组件交互。
- 安全检查：通过；未新增外部输入、secret、网络请求、SQL 或命令执行。
- 测试与验证：通过；目标测试、全量前端单测、类型检查、静态检查、构建和通用文档校验均已执行。
- 复杂度检查：通过；`tags-view-store.ts` 从 280 行降至 239 行，新增 helper 55 行，新增测试 79 行。
- Document-refresh: not-needed；本轮只调整内部前端 store 组织和任务记录，不改变产品文档、API、数据库或架构事实。
- 剩余风险：未启动浏览器人工操作 TagsView；当前以 store 单测、helper 单测、全量前端单测、构建和远端门禁作为最小充分验证。
- 潜在技术债：`tags-view-store.ts` 仍包含左/右关闭、全部关闭和导航兜底编排，后续可单独评估是否继续抽出关闭策略 helper。
- 结论：通过。
