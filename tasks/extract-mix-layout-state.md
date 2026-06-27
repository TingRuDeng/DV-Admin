# Mix 布局状态抽取

## 现状分析

- `frontend/src/layouts/modes/mix/index.vue` 当前 281 行，同时承担布局装配、侧栏路径拼接、激活菜单推导和路由变化同步。
- `frontend/src/layouts/components/Menu/MixTopMenu.vue` 已负责顶部菜单点击与初始化，本轮不触碰顶部菜单行为。
- 本轮目标只抽离 `mix/index.vue` 中可纯测的状态与路径同步逻辑，不改变模板结构、样式、菜单 store API 或路由契约。

## 执行计划

- [ ] 新增 `frontend/src/layouts/modes/mix/useMixLayoutState.ts`，承接 `isLogoCollapsed`、`activeLeftMenuPath`、`resolvePath` 和路由同步 watcher。
- [ ] 精简 `frontend/src/layouts/modes/mix/index.vue`，只保留布局组件装配与 composable 调用。
- [ ] 新增 `frontend/src/layouts/modes/mix/__tests__/use-mix-layout-state.spec.ts`，覆盖顶级路径提取、菜单路径解析、`activeMenu` 优先级和源文件行数守卫。
- [ ] 执行最小充分验证：目标 Vitest、前端质量检查、前端构建、文档校验和 diff 检查。

## 并行策略

- 不启用 subagent。原因：本轮改动集中在同一布局职责链，测试和实现共享上下文，串行更能避免写冲突。

## 验收标准

- `frontend/src/layouts/modes/mix/index.vue` 明显低于 300 行，且职责收敛为布局装配。
- 新增 helper/composable 有自动化测试覆盖。
- 不改变 Mix 布局菜单选择、侧栏折叠、Logo 折叠、TagsView 或 AppMain 行为。

## 验证记录

- `node_modules/.bin/vitest run src/layouts/modes/mix/__tests__/use-mix-layout-state.spec.ts`：5 passed。
- `node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `node_modules/.bin/vue-tsc --noEmit`：通过。
- `node_modules/.bin/vitest run`：86 files / 245 tests passed。
- `node_modules/.bin/vite build`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review Gate

- 终态：finished。
- Spec 符合度：通过；只抽取 Mix 布局状态与路径同步逻辑，未修改菜单 store API、模板结构或后端契约。
- 安全检查：通过；未新增外部输入、secret、网络请求、SQL 或命令执行。
- 测试与验证：通过；目标测试、全量前端单测、类型检查、静态检查、构建和通用文档校验均已执行。
- 复杂度检查：通过；`index.vue` 从 281 行降至 234 行，新增 composable 80 行，新增测试 64 行。
- Document-refresh: not-needed；本轮只调整内部前端布局组织和任务记录，不改变产品文档、API、数据库或架构事实。
- 剩余风险：未启动浏览器做 Mix 布局人工交互验证，当前以单测、类型检查和构建作为本轮最小充分验证。
- 潜在技术债：`MixTopMenu.vue` 仍有顶部菜单初始化和导航逻辑，后续可单独评估是否与 `useMixLayoutState` 进一步收敛。
- 结论：通过。
