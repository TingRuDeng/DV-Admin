# Login 死模板清理

## 目标

- [x] 串行：确认 `Login.vue` 当前行数和已注释死模板。
- [x] 串行：删除登录组件中已注释的未启用模板、导入、事件和样式。
- [x] 串行：补充治理测试，防止 `Login.vue` 回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/views/login/components/Login.vue`
- 修改：`frontend/src/views/login/components/__tests__/login-form-rule-type-governance.spec.ts`
- 不涉及：登录提交、验证码刷新、默认凭据、路由跳转、注册/重置密码组件、后端 API

## 组件边界

- `Login.vue`：继续负责登录表单 UI、验证码、表单校验和登录提交。
- 本轮仅删除已注释且未运行的模板和样式，不引入新子组件。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/views/login/components/__tests__/login-form-rule-type-governance.spec.ts src/views/login/components/__tests__/login-defaults.test.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- 通过：`cd frontend && ./node_modules/.bin/vitest run src/views/login/components/__tests__/login-form-rule-type-governance.spec.ts src/views/login/components/__tests__/login-defaults.test.ts`，2 个测试文件、5 个用例通过。
- 通过：`cd frontend && ./node_modules/.bin/vue-tsc --noEmit`。
- 通过：`cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`。
- 通过：`cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`。
- 通过：`cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`。
- 通过：`cd frontend && ./node_modules/.bin/vitest run`，85 个测试文件、236 个用例通过。
- 通过：`python3 scripts/validate_docs.py . --profile generic`。
- 通过：`git diff --check`。
- 行数：`frontend/src/views/login/components/Login.vue` 为 229 行，低于 300 行硬限制。

## Review Gate

- 终态：finished
- Spec 符合度：符合，仅删除登录组件已注释死模板、注释导入、未使用事件草稿和未运行样式。
- 安全检查：未新增外部输入、认证逻辑、存储逻辑、网络请求或 secret。
- 测试与验证：目标测试、全量前端单测、类型检查、静态检查、格式检查、样式检查、文档校验和 diff 空白检查均通过。
- 复杂度检查：`Login.vue` 从 294 行降至 229 行，新增行数守卫测试防止回退到 300 行及以上。
- 文档刷新判断：Document-refresh: not-needed
- 原因：本轮不改变 API、数据库模型、架构流程或运行契约。
- 剩余风险：未验证浏览器真实登录流程；本轮删除的是未运行注释代码，风险较低。
- 潜在技术债：登录页仍同时承载表单 UI、验证码和提交流程，后续如继续扩展可再拆分组合式函数。
- 结论：通过。
