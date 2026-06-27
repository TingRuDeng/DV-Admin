# PageModal 组件映射表抽取

## 目标

- [x] 串行：确认 `PageModal.vue` 当前行数和静态组件映射职责。
- [x] 串行：将 `componentMap` 与 `childrenMap` 抽到专用 helper。
- [x] 串行：补充治理测试，防止 `PageModal.vue` 回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/CURD/PageModal.vue`
- 新增：`frontend/src/components/CURD/pageModalComponentMaps.ts`
- 修改：`frontend/src/components/CURD/__tests__/curd-component-map-type-governance.spec.ts`
- 不涉及：表单模板结构、弹窗/抽屉行为、slot 协议、`defineExpose()` 公开 API、后端 API

## 组件边界

- `PageModal.vue`：继续负责表单弹窗/抽屉组合、表单状态和提交编排。
- `pageModalComponentMaps.ts`：只负责提供 PageModal 的静态表单组件映射表，不持有响应式状态。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/CURD/__tests__/curd-component-map-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- `cd frontend && ./node_modules/.bin/vitest run src/components/CURD/__tests__/curd-component-map-type-governance.spec.ts`：通过，1 个测试文件、3 个用例。
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`：通过。
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `cd frontend && ./node_modules/.bin/vitest run`：通过，85 个测试文件、234 个用例。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `git diff --check`：通过。
- `wc -l frontend/src/components/CURD/PageModal.vue frontend/src/components/CURD/pageModalComponentMaps.ts`：`PageModal.vue` 245 行，`pageModalComponentMaps.ts` 54 行。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只抽取静态组件映射表，没有改变表单模板结构、弹窗/抽屉行为、slot 协议、`defineExpose()` 公开 API 或后端 API。
- 安全检查：通过；未新增外部输入处理、secret、mock、fallback 或静默降级。
- 复杂度检查：通过；`PageModal.vue` 从 300 行降至 245 行，新增 helper 为 54 行，均低于 300 行硬约束。
- Document-refresh: not-needed。原因：本轮不改变用户功能、API、数据库模型或架构事实。
- 剩余风险：未启动浏览器做 PageModal 交互验证；当前由组件映射治理测试、类型检查和全量单测覆盖。
- 潜在技术债：`PageModal.vue` 仍有 drawer/dialog 两套模板重复结构，后续如继续治理，应单独规划表单内容模板抽取。
