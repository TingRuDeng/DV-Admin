# 收紧 InputTag 配置属性类型边界

## 目标

- 移除 `InputTag` 组件配置属性中的显式 `any`。
- 使用 Element Plus 组件 props 类型表达按钮、输入框和标签属性。
- 新增类型治理测试，防止 `InputTag` 配置属性重新回退到显式 `any`。

## 非目标

- 不修改 `InputTag` 的 UI、交互、滚动容器或标签新增删除行为。
- 不修改 CURD 对 `custom-tag` / `input-tag` 的调用方式。
- 不新增抽象或拆分组件。

## 当前事实

- `frontend/src/components/InputTag/index.vue` 的 `config.buttonAttrs/inputAttrs/tagAttrs` 均为 `Record<string, any>`。
- 组件模板只将 `buttonAttrs` 传给 `el-button`，将 `tagAttrs` 传给 `el-tag`；`inputAttrs` 当前保留在配置契约中但未透传。
- 当前没有专门覆盖 `InputTag` 配置属性类型的治理测试。

## 决策日志

- 方案 A：使用 Element Plus 的 `ButtonProps`、`InputProps`、`TagProps` 的 `Partial` 类型。优点是贴近实际组件契约，避免手写宽泛索引；缺点是 `buttonAttrs.btnText` 不是 Element Plus 属性，需要单独扩展。
- 方案 B：统一改成 `Record<string, unknown>`。优点是最小；缺点是不能表达真实组件契约，模板中自定义 `btnText` 仍需要额外窄化。
- 选择方案 A。原因：本轮目标是长期可维护的类型边界，复用组件 props 类型比简单替换为 `unknown` 更能表达真实意图。

## 执行计划

- [x] 串行：在 `InputTag` 中定义配置属性类型，移除 `Record<string, any>`。
- [x] 串行：保留 `buttonAttrs.btnText` 自定义展示文本能力，不改变默认文案。
- [x] 串行：新增治理测试，锁定 `InputTag` 配置属性不再出现显式 `any`。
- [x] 串行：运行目标测试、前端类型检查、前端质量门禁、文档校验和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `InputTag/index.vue`：只调整 props 类型声明和必要的展示文本类型。
- `__tests__`：新增类型治理测试，不测试标签交互行为。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在单个共享组件和一个治理测试，串行处理更直接。

## 验证矩阵

- `cd frontend && pnpm run test:unit -- --run src/components/__tests__/input-tag-type-governance.spec.ts`
- `cd frontend && pnpm run test:unit`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 终态：finished。
- Spec 符合度：通过。本轮只收紧 `InputTag` 配置属性类型，没有修改标签新增、删除、滚动容器或 CURD 调用方式。
- 安全检查：通过。本轮没有新增 secret、网络请求、SQL、Shell 拼接、mock 或静默 fallback。
- 测试与验证：通过。目标治理测试、前端全量单测、类型检查、lint、文档校验、运行时代码显式 `any` 扫描和 diff 检查均已通过。
- 复杂度检查：通过。`InputTag/index.vue` 为 72 行，新增治理测试为 22 行，均低于 300 行；新增类型为单一职责配置类型。
- Document-refresh: not-needed。原因：本轮只收紧内部 Vue 组件配置类型，不改变用户可见 API、数据库结构、启动流程或架构事实。
- 剩余风险：未做浏览器手工标签新增/删除回归；本轮没有改变标签列表更新逻辑，风险由类型检查、单测和远端前端门禁覆盖。
