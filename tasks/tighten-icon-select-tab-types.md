# IconSelect 标签页事件类型治理

## 目标

- [x] 串行：确认 `IconSelect` 的 `tab-click` 事件来源和真实调用边界。
- [x] 串行：移除 `handleTabClick(tabPane: any)` 的显式 `any`。
- [x] 串行：补充治理测试，防止标签页事件类型回退。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/IconSelect/index.vue`
- 新增：`frontend/src/components/__tests__/icon-select-type-governance.spec.ts`
- 不涉及：图标加载、搜索逻辑、图标命名规则、CURD 表单组件映射、后端 API

## 决策

- 使用 Element Plus `TabsPaneContext` / `TabPaneName` 表达 `el-tabs` 的 `tab-click` 事件参数。
- 标签页缺少 `name` 时显式抛错，不做静默 fallback。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/icon-select-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
