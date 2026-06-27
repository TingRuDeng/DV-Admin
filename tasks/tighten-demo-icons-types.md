# demo icons 类型治理

## 目标

- [x] 串行：确认 `demo/icons.vue` 中剩余显式 `any` 的实际输入来源。
- [x] 串行：将图标代码生成函数参数收紧为实际字符串类型。
- [x] 串行：补充治理测试，防止函数参数回退到显式 `any`。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/views/demo/icons.vue`
- 新增：`frontend/src/views/__tests__/demo-icons-type-governance.spec.ts`
- 不涉及：图标资源加载、Element Plus 图标注册、页面布局、后端 API

## 决策

- SVG 图标列表改为只读字面量数组，保留模板中 `v-for` 的字符串输入语义。
- Element Plus 图标代码生成函数只依赖图标名称，参数类型收紧为 `string`。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/views/__tests__/demo-icons-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- `cd frontend && ./node_modules/.bin/vitest run src/views/__tests__/demo-icons-type-governance.spec.ts`：通过，1 个测试文件、1 个用例。
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`：通过。
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `cd frontend && ./node_modules/.bin/vitest run`：通过，85 个测试文件、233 个用例。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收紧 demo 图标代码生成函数参数类型，没有改变图标资源、页面布局或后端 API。
- 安全检查：通过；未新增外部输入处理、secret、mock、fallback 或静默降级。
- 复杂度检查：通过；`demo/icons.vue` 为 129 行，新增治理测试为 12 行，未触发文件大小或函数长度硬约束。
- Document-refresh: not-needed。原因：本轮不改变用户功能、API、数据库模型或架构事实。
- 剩余风险：未启动浏览器做 demo 图标页交互验证；当前以类型检查和单测约束类型回退。
- 潜在技术债：demo 页面仍属于示例能力，后续如继续生产化，需要单独确认示例 API 与真实业务契约的边界。
