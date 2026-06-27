# 收紧登录表单规则类型边界

## 目标

- 移除登录与注册表单规则中的显式 `any`。
- 使用 Element Plus 表单规则类型表达动态规则对象。
- 新增类型治理测试，防止登录表单规则重新回退到显式 `any`。

## 非目标

- 不修改登录、注册、验证码、路由跳转或用户状态逻辑。
- 不调整登录页 UI、交互文案或样式。
- 不修改后端认证 API。

## 当前事实

- `frontend/src/views/login/components/Login.vue` 的 `loginRules` 使用 `Partial<Record<string, any>>`。
- `frontend/src/views/login/components/Register.vue` 的 `rules` 使用 `Partial<Record<string, any>>`，确认密码 validator 参数使用 `any`。
- `frontend/src/views/login/components/__tests__/login-defaults.test.ts` 目前只覆盖默认账号读取，没有覆盖表单规则类型治理。

## 决策日志

- 方案 A：直接使用 Element Plus 的 `FormRules` 类型。优点是贴近 `el-form` 的 `rules` 契约，改动最小；缺点是需要确认动态验证码字段仍可赋值。
- 方案 B：自定义登录规则类型。优点是字段更窄；缺点是会复制 Element Plus 契约，后续升级成本更高。
- 选择方案 A。原因：本轮目标是消除显式 `any`，不改变规则结构或校验行为，直接复用框架类型更稳。

## 执行计划

- [x] 串行：将 `Login.vue` 的 `Partial<Record<string, any>>` 改为 Element Plus 表单规则类型。
- [x] 串行：将 `Register.vue` 的规则对象和确认密码 validator 参数改为显式类型。
- [x] 串行：新增登录表单规则类型治理测试，锁定 `any` 不回流。
- [x] 串行：运行目标测试、前端类型检查、前端质量门禁、文档校验和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `Login.vue`：只调整表单规则类型声明。
- `Register.vue`：只调整表单规则类型声明和 validator 参数类型。
- `__tests__`：新增治理测试，不测试具体登录业务流程。

## 并行评估

- 本轮不启用 subagent。原因：两个 Vue 文件和一个测试文件存在同一目标类型治理，串行处理更清晰，避免计划与实现拆分成本高于收益。

## 验证矩阵

- `cd frontend && pnpm run test:unit -- --run src/views/login/components/__tests__/login-form-rule-type-governance.spec.ts`
- `cd frontend && pnpm run test:unit`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 终态：finished。
- Spec 符合度：通过。本轮只收紧登录与注册表单规则类型，没有修改登录、注册、验证码、路由跳转或用户状态逻辑。
- 安全检查：通过。本轮没有新增 secret、网络请求、SQL、Shell 拼接、mock 或静默 fallback。
- 测试与验证：通过。目标治理测试、前端全量单测、类型检查、lint、文档校验和 diff 检查均已通过。
- 复杂度检查：通过。`Login.vue` 为 294 行、`Register.vue` 为 222 行，均低于 300 行；`Login.vue` 已接近上限，后续继续改动前应优先拆分。
- Document-refresh: not-needed。原因：本轮只收紧内部 Vue 表单规则类型，不改变用户可见 API、数据库结构、启动流程或架构事实。
- 剩余风险：未做浏览器手工登录/注册回归；本轮没有改变运行时规则结构，风险由类型检查、单测和远端前端门禁覆盖。
