# 收紧 CURD 表格列扩展类型边界

## 目标

- 移除 `types.ts` 中表格列配置扩展索引 `[key: string]: any`。
- 用明确的 `unknown` 承接历史扩展字段，避免调用方从类型层面绕过校验。
- 新增类型治理测试，防止表格列扩展索引回退到显式 `any`。

## 执行计划

- [x] 串行：在 `types.ts` 中新增表格列扩展值类型。
- [x] 串行：将表格列配置扩展索引从 `any` 收紧为共享扩展值类型。
- [x] 串行：新增类型治理测试，锁定本轮治理范围不再出现显式 `any`。
- [x] 串行：运行前端目标测试、类型检查、质量门禁和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `types.ts`：只调整表格列配置扩展索引类型，不整体替换 `IObject`。
- `__tests__`：新增治理测试，防止本轮消除的显式 `any` 回流。
- 不涉及：`PageContent.vue` 渲染逻辑、分页、筛选、导入导出、表单弹窗和后端 API。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在 `types.ts` 和一个治理测试，串行更直接。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/CURD/__tests__/curd-column-extra-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只收紧 CURD 表格列配置扩展索引类型，不改变 PageContent 渲染、分页、筛选、导入导出或后端 API。
- 安全检查：未新增 secret、mock、fallback 或静默降级；敏感词搜索命中仅来自历史任务摘要，不属于本轮新增源码。
- 测试与验证：目标类型治理测试、`type-check`、`lint:check`、前端 `test:unit`（73 files，212 tests）、根目录文档校验和 `git diff --check` 均通过。
- 复杂度检查：`types.ts` 为 249 行，新增治理测试为 14 行，新增任务文件为 38 行，均未超过 300 行。
- Document-refresh: not-needed，原因：本轮只调整内部 TypeScript 类型边界，不改变用户可见功能、API 或数据库结构。
- 剩余风险：`IObject = Record<string, any>` 仍是既有宽类型边界，应后续单独治理。
