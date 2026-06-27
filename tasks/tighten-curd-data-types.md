# 收紧 CURD 数据请求与解析类型边界

## 目标

- 收紧 `frontend/src/components/CURD/types.ts` 中数据请求、解析和导入导出 action 的返回类型。
- 移除 `usePageContentData.ts` 中 `applyPageData(data: any)` 的显式 `any`。
- 增加类型治理测试，防止 CURD 数据链路重新引入 `any`。

## 执行计划

- [x] 串行：新增 CURD 数据响应相关类型，替换 `IContentConfig` 中可控的 `Promise<any>` 和解析结果 `any`。
- [x] 串行：更新 `usePageContentData.ts` 的 `applyPageData` 参数类型。
- [x] 串行：新增或更新类型治理测试，覆盖 `types.ts` 和 `usePageContentData.ts` 中的数据链路。
- [x] 串行：运行前端目标测试、类型检查、质量门禁和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 组件边界

- `types.ts`：只调整数据请求/解析 action 的公开类型，不改变运行时逻辑。
- `usePageContentData.ts`：只调整数据响应参数类型，不改变分页、parseData 或数据写入行为。
- 测试：采用源码治理测试和现有 composable 行为测试，不新增 UI 行为。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在同一公共类型文件及其直接使用点，存在写冲突，串行更稳。

## 验证命令

- `cd frontend && pnpm run test:unit -- --run src/components/CURD/__tests__/use-page-content-data.spec.ts src/components/CURD/__tests__/curd-data-type-governance.spec.ts`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run test:unit`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只收紧 CURD 数据请求、解析、导出文件响应和表单提交 action 的 TypeScript 契约，不改变运行时分页、parseData、导入导出或 UI 行为。
- 安全检查：未新增 secret、mock、fallback 或静默降级；失败过的 type-check 通过响应泛型与导出文件响应结构修复，没有放宽回 `any`。
- 测试与验证：目标相关测试通过；前端 `lint:check`、`type-check`、`test:unit`（70 files，207 tests）、根目录文档校验和 `git diff --check` 均通过。
- 复杂度检查：`types.ts` 为 231 行，`usePageContentData.ts` 为 104 行，新增治理测试为 32 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只调整内部 TypeScript 类型边界，不改变用户可见功能、API 或数据库结构。
- 剩余风险：`IObject = Record<string, any>` 和组件映射中的 `any` 仍是既有技术债，应后续按更小边界继续治理。
