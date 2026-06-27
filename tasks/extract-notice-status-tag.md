# Notice 状态标签组件抽取

## 目标

- [x] 串行：确认 `notice/index.vue` 当前状态标签重复模板和行数边界。
- [x] 串行：抽取通知目标类型和发布状态标签展示组件。
- [x] 串行：补充治理测试，防止 `notice/index.vue` 回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/views/system/notice/index.vue`
- 新增：`frontend/src/views/system/notice/components/NoticeStatusTag.vue`
- 修改：`frontend/src/views/__tests__/notice-style-migration.spec.ts`
- 不涉及：通知查询参数、表格请求、发布/撤回/删除动作、表单抽屉、详情弹窗、后端 API

## 组件边界

- `notice/index.vue`：继续负责页面组合、查询、表格请求和行级动作分发。
- `NoticeStatusTag.vue`：只负责通知目标类型和发布状态的标签文案、类型和样式类映射。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/views/__tests__/notice-style-migration.spec.ts src/views/system/notice/__tests__/notice-defaults.test.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- 通过：`cd frontend && ./node_modules/.bin/vitest run src/views/__tests__/notice-style-migration.spec.ts src/views/system/notice/__tests__/notice-defaults.test.ts`，2 个测试文件、5 个用例通过。
- 通过：`cd frontend && ./node_modules/.bin/vue-tsc --noEmit`。
- 通过：`cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`。
- 通过：`cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`。
- 通过：`cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`。
- 通过：`cd frontend && ./node_modules/.bin/vitest run`，85 个测试文件、238 个用例通过。
- 通过：`python3 scripts/validate_docs.py . --profile generic`。
- 通过：`git diff --check`。
- 行数：`frontend/src/views/system/notice/index.vue` 为 254 行，低于 300 行硬限制。
- 调试记录：首次 ESLint/Prettier 失败来自 `NoticeStatusTag.vue` SFC 块顺序和测试字符串引号格式；已按项目规则修正后重跑通过。

## Review Gate

- 终态：finished
- Spec 符合度：符合，仅抽取通知目标类型和发布状态标签展示组件。
- 安全检查：未新增外部输入、网络请求、认证逻辑、存储逻辑或 secret。
- 测试与验证：目标测试、全量前端单测、类型检查、静态检查、格式检查、样式检查、文档校验和 diff 空白检查均通过。
- 复杂度检查：`notice/index.vue` 从 291 行降至 254 行，新增 `NoticeStatusTag.vue` 为 52 行，并新增行数守卫。
- 文档刷新判断：Document-refresh: not-needed
- 原因：本轮不改变 API、数据库模型、架构流程或运行契约。
- 剩余风险：未做浏览器手动表格状态展示验证；状态映射来自原模板等价迁移，风险较低。
- 潜在技术债：通知页面的行级操作仍在页面内，后续如继续压缩可抽取通知动作 composable。
- 结论：通过。
