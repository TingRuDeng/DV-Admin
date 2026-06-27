# Dict 字典值类型收口

## 目标

- 收紧 `frontend/src/components/Dict` 的字典值类型边界。
- 移除 `Dict/index.vue` 的 `ref<any>` 与 `handleChange(val: any)`。
- 移除 `DictLabel.vue` 中按字典值查询标签时的显式 `any`。
- 补充治理测试，防止字典值类型回退到显式 `any`。

## 范围

- 修改：`frontend/src/components/Dict/index.vue`
- 修改：`frontend/src/components/Dict/DictLabel.vue`
- 新增：`frontend/src/components/Dict/types.ts`
- 新增：`frontend/src/components/__tests__/dict-value-type-governance.spec.ts`
- 修改：`tasks/todo.md`
- 不涉及：字典接口、字典缓存、字典项数据结构、页面样式、后端 API

## 执行计划

- [x] 串行：新增共享字典值类型。
- [x] 串行：收紧 `Dict` 选择值、复选值和 change 事件类型。
- [x] 串行：收紧 `DictLabel` 标签查询值类型。
- [x] 串行：新增字典值类型治理测试。
- [x] 串行：运行目标测试、前端类型检查、前端 lint、前端单测、文档校验和 diff 检查。
- [x] 串行：执行交付前 review-gate 并记录结论。

## 并行说明

本轮不启用 subagent。原因：改动集中在同一 Dict 组件目录和一份对应治理测试，写冲突明显，串行更清晰。

## 验证命令

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/dict-value-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished。
- Spec 符合度：通过，本轮只收紧 Dict 字典值类型边界并新增治理测试。
- 安全检查：无新增 secret、mock 或静默 fallback；外部 `modelValue` 数组通过 `unknown[]` 归一化后只保留 `string | number`。
- 测试与验证：目标测试、前端类型检查、eslint、prettier、stylelint、完整前端单测、文档校验和 `git diff --check` 均通过。
- 复杂度检查：目标组件 162 行，`DictLabel` 67 行，新增类型文件 2 行，新增测试 26 行，均低于单文件 300 行。
- Document-refresh: not-needed，原因：本轮不改变用户可见功能、API、数据库结构或产品文档事实。
- 剩余风险：WangEditor、Breadcrumb、Notification 等历史组件仍有显式 `any`，需要后续继续治理。
