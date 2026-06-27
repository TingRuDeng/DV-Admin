# 收紧 CURD 表单 API 类型边界

## 目标

- 移除 `PageModal.vue` 中 `defineSlots` 和 `setFormItemData` 的显式 `any`。
- 收紧 `types.ts` 中表单项 `options`、`initialValue`、`events` 的显式 `any`。
- 新增类型治理测试，防止 CURD 表单 API 边界回退。

## 执行计划

- [x] 串行：在 `types.ts` 中新增表单值、选项值、插槽参数和事件参数共享类型。
- [x] 串行：更新 `PageModal.vue` 的插槽和公开方法类型，不改变模板、提交或校验行为。
- [x] 串行：新增类型治理测试，锁定本轮治理范围不再出现显式 `any`。
- [x] 串行：运行前端目标测试、类型检查、质量门禁和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `PageModal.vue`：只调整插槽声明和公开方法参数类型，不改变弹窗、抽屉、校验、提交或表单初始化流程。
- `types.ts`：只新增并使用表单 API 相关共享类型，不在本轮整体替换 `IObject`。
- `__tests__`：新增治理测试，防止本轮消除的显式 `any` 回流。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在 `types.ts` 与 `PageModal.vue`，存在明显写冲突，串行更可控。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/CURD/__tests__/curd-form-api-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只收紧 CURD 表单 API 类型边界，不改变弹窗、抽屉、表单初始化、校验、提交或公开方法行为。
- 安全检查：未新增 secret、mock、fallback 或静默降级；敏感词搜索命中仅来自历史任务摘要，不属于本轮新增代码。
- 测试与验证：目标类型治理测试、`type-check`、`lint:check`、前端 `test:unit`（72 files，211 tests）、根目录文档校验和 `git diff --check` 均通过。
- 复杂度检查：`PageModal.vue` 为 300 行，`types.ts` 为 248 行，新增治理测试为 33 行，均未超过 300 行。
- Document-refresh: not-needed，原因：本轮只调整内部 TypeScript 类型边界，不改变用户可见功能、API 或数据库结构。
- 剩余风险：`IObject = Record<string, any>` 和表格列扩展索引仍是既有宽类型边界，应后续单独治理。
