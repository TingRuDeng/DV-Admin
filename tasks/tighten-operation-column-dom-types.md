# OperationColumn DOM 测量类型收口

## 目标

- 收紧 `frontend/src/components/OperationColumn/index.vue` 的 DOM 测量类型边界。
- 移除 `getOperationMaxWidth()` 中的显式 `any`。
- 补充治理测试，防止该组件后续回退到弱类型 DOM 测量。

## 范围

- 修改：`frontend/src/components/OperationColumn/index.vue`
- 新增：`frontend/src/components/__tests__/operation-column-type-governance.spec.ts`
- 修改：`tasks/todo.md`
- 不涉及：表格操作列渲染行为、插槽协议、后端 API、路由、样式重构

## 执行计划

- [x] 串行：用 DOM 标准类型替换 `getElementsByClassName`/`querySelectorAll` 相关弱类型。
- [x] 串行：新增 OperationColumn 类型治理测试。
- [x] 串行：运行目标测试、前端类型检查、前端 lint、前端单测、文档校验和 diff 检查。
- [x] 串行：执行交付前 review-gate 并记录结论。

## 并行说明

本轮不启用 subagent。原因：改动集中在同一个 Vue 组件和一个对应测试文件，写冲突明显，串行更清晰。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/__tests__/operation-column-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished。
- Spec 符合度：通过，本轮只收紧 `OperationColumn` DOM 测量类型并新增治理测试。
- 安全检查：无新增 secret、外部输入处理、mock 或静默 fallback。
- 测试与验证：目标测试、前端类型检查、eslint、prettier、stylelint、完整前端单测、文档校验和 `git diff --check` 均通过。
- 复杂度检查：目标组件 90 行，新增测试 17 行，任务文件 38 行，均低于当前约束。
- Document-refresh: not-needed，原因：本轮不改变用户可见功能、API、数据库结构或产品文档事实。
- 剩余风险：前端其他历史组件仍有显式 `any`，需要后续按模块继续治理。
