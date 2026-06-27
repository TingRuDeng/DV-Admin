# 收紧 CURD 组件映射类型边界

## 目标

- 移除 `PageSearch.vue` 和 `PageModal.vue` 中组件映射 `Map<..., any>` 的显式 `any`。
- 为 CURD 动态组件映射提供共享类型，避免搜索表单和弹窗表单各自维护宽泛映射。
- 增加类型治理测试，防止映射类型重新回退。

## 执行计划

- [x] 串行：在 `types.ts` 中新增 CURD 动态组件映射类型。
- [x] 串行：更新 `PageSearch.vue` 和 `PageModal.vue` 的 component map / children map 类型。
- [x] 串行：新增或更新类型治理测试，锁定映射不再使用 `any`。
- [x] 串行：运行前端目标测试、类型检查、质量门禁和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `PageSearch.vue`：只调整搜索表单动态组件映射类型，不改变模板或事件。
- `PageModal.vue`：只调整表单组件和子选项组件映射类型，不改变提交、校验或公开方法。
- `types.ts`：只新增共享类型，不调整已有业务配置字段。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在同一类型文件和两个 Vue 组件，存在写冲突，串行更清晰。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/CURD/__tests__/curd-component-map-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只收紧 CURD 搜索表单和弹窗表单的动态组件映射类型，不改变模板结构、查询、提交、校验或表单数据流。
- 安全检查：未新增 secret、mock、fallback 或静默降级；移除了组件映射附近的 `@ts-ignore`，并补充显式 Element Plus 组件导入。
- 测试与验证：前端 `lint:check`、`type-check`、`test:unit`（71 files，209 tests）、根目录文档校验和 `git diff --check` 均通过。
- 复杂度检查：`PageModal.vue` 为 298 行，`PageSearch.vue` 为 189 行，`types.ts` 为 234 行，新增治理测试为 23 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只调整内部 TypeScript 类型边界，不改变用户可见功能、API 或数据库结构。
- 剩余风险：`defineSlots`、`setFormItemData` 和 `IObject` 中仍存在既有 `any`，应后续按独立边界继续治理。
