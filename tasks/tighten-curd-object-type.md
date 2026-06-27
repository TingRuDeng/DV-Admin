# 收紧 CURD 通用对象类型边界

## 目标

- 将 `types.ts` 中 `IObject = Record<string, any>` 收紧为 `Record<string, unknown>`。
- 对必要读取点做显式窄化，避免调用方继续从通用对象类型逃逸。
- 新增类型治理测试，防止 CURD 通用对象类型回退到显式 `any`。

## 执行计划

- [x] 串行：将 `IObject` 别名从 `any` 收紧为 `unknown`。
- [x] 串行：根据类型检查结果处理必要窄化，不改变运行时业务流程。
- [x] 串行：新增或更新类型治理测试，锁定 CURD 运行时代码不再出现显式 `any`。
- [x] 串行：运行前端目标测试、类型检查、质量门禁和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `types.ts`：只调整 CURD 通用对象值类型，不拆分类型文件。
- CURD 运行时代码：只做 TypeScript 窄化或类型声明调整，不改变渲染、请求、分页、筛选、导入导出或表单行为。
- `__tests__`：新增治理测试，防止本轮消除的显式 `any` 回流。

## 并行评估

- 本轮不启用 subagent。原因：`IObject` 是共享类型，影响面需要按类型检查串行收敛，避免多处并行写冲突。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/CURD/__tests__/curd-object-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 终态：finished。
- Spec 符合度：通过。本轮将 `IObject` 从 `Record<string, any>` 收紧为 `Record<string, unknown>`，并只在 CURD 读取点增加局部窄化 helper。
- 安全检查：通过。本轮没有新增 secret、网络请求、SQL、Shell 拼接、mock 或静默 fallback。
- 测试与验证：通过。`pnpm run test:unit -- --run src/components/CURD/__tests__/curd-object-type-governance.spec.ts`、`pnpm run test:unit`、`pnpm run type-check`、`pnpm run lint:check`、`python3 scripts/validate_docs.py . --profile generic`、`git diff --check` 均通过。
- 复杂度检查：通过。相关 CURD 文件均小于 300 行，新增 helper 均为单一职责函数。
- Document-refresh: not-needed。原因：本轮只收紧内部 TypeScript 类型边界，不改变用户可见 API、数据库结构、启动流程或架构事实。
- 剩余风险：未做浏览器交互回归；当前风险由组件单测、类型检查和 lint 覆盖，后续如修改 CURD 兼容层交互可补 Playwright 用例。
