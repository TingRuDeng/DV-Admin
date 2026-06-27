# TagsView 路由标签同步抽取

## 目标

- [x] 串行：确认 `TagsView/index.vue` 当前职责和行数边界。
- [x] 串行：抽取固定标签初始化、当前路由标签添加和更新逻辑。
- [x] 串行：补充治理测试，防止 `TagsView/index.vue` 回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/layouts/components/TagsView/index.vue`
- 新增：`frontend/src/layouts/components/TagsView/useTagsRouteSync.ts`
- 修改：`frontend/src/layouts/components/__tests__/tags-view-type-governance.spec.ts`
- 不涉及：标签项 UI、右键菜单 UI、TagsView store API、缓存键规则、后端 API

## 组件边界

- `TagsView/index.vue`：继续负责标签栏 UI 编排、滚轮横向滚动、标签关闭和菜单动作分发。
- `useTagsRouteSync.ts`：负责固定标签初始化、当前路由标签添加和当前标签 fullPath/query 更新。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/layouts/components/__tests__/tags-view-type-governance.spec.ts src/store/modules/__tests__/tags-view-store.test.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- 通过：`cd frontend && ./node_modules/.bin/vitest run src/layouts/components/__tests__/tags-view-type-governance.spec.ts src/store/modules/__tests__/tags-view-store.test.ts`，2 个测试文件、8 个用例通过。
- 通过：`cd frontend && ./node_modules/.bin/vue-tsc --noEmit`。
- 通过：`cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`。
- 通过：`cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`。
- 通过：`cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`。
- 通过：`cd frontend && ./node_modules/.bin/vitest run`，85 个测试文件、237 个用例通过。
- 通过：`python3 scripts/validate_docs.py . --profile generic`。
- 通过：`git diff --check`。
- 行数：`frontend/src/layouts/components/TagsView/index.vue` 为 216 行，低于 300 行硬限制。

## Review Gate

- 终态：finished
- Spec 符合度：符合，仅抽取固定标签初始化、当前路由标签添加和当前标签更新逻辑。
- 安全检查：未新增外部输入、网络请求、认证逻辑、存储逻辑或 secret。
- 测试与验证：目标测试、全量前端单测、类型检查、静态检查、格式检查、样式检查、文档校验和 diff 空白检查均通过。
- 复杂度检查：`TagsView/index.vue` 从 293 行降至 216 行，新增 `useTagsRouteSync.ts` 为 88 行，并新增行数守卫。
- 文档刷新判断：Document-refresh: not-needed
- 原因：本轮不改变 API、数据库模型、架构流程或运行契约。
- 剩余风险：未做浏览器手动标签栏交互验证；相关行为由既有 store 测试和治理测试覆盖，风险可控。
- 潜在技术债：标签关闭动作仍在 `index.vue` 内，后续如继续压缩可再抽取关闭动作 composable。
- 结论：通过。
