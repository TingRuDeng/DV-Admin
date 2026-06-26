# PageContent 工具栏组件拆分

## 目标

- 将 `frontend/src/components/CURD/PageContent.vue` 顶部左右工具栏模板拆入独立组件。
- 降低 `PageContent.vue` 的模板体积，并保持 CURD 兼容层现有公开 API 和事件行为不变。

## 非目标

- 不修改 `fetchPageData()`、分页、筛选、导入导出、删除、编辑或表格列渲染逻辑。
- 不修改 `IContentConfig`、`IToolsButton` 等公开类型。
- 不引入新的 mock、fallback 或静默降级。
- 不改变 CURD 兼容层弃用治理策略。

## 当前事实

- `frontend/src/components/CURD/PageContent.vue` 当前 936 行，是当前仓库中最大的手写 Vue 组件。
- 顶部工具栏模板包含左侧按钮、右侧按钮和列筛选 popover，职责相对独立。
- `frontend/src/components/__tests__/curd-deprecation-governance.spec.ts` 已限制 CURD 兼容层只能在兼容目录内部使用。
- 本轮拆分若新增子组件放在 `frontend/src/components/CURD/` 下，不会扩大兼容层外部使用面。

## 组件边界

- `PageContent.vue`：继续负责数据编排、表格状态、分页、导入导出和对外 `defineExpose()`。
- `PageContentToolbar.vue`：只负责渲染左右工具栏、列显示筛选和把点击事件上抛。

## 设计原则

- Props down / Events up：工具栏按钮、列配置和删除禁用状态由父组件传入，点击通过 `toolbar` 事件上抛。
- 保持行为稳定：沿用原来的 `v-hasPerm`、按钮 attrs、filter popover 和列 `show` 绑定。
- 最小拆分：不在本轮抽 composable，不重写按钮生成逻辑，避免扩大风险。

## 方案对比

- 方案 A：只抽 `PageContentToolbar.vue`。
  - 优点：边界清晰、风险低、无需改数据流。
  - 缺点：`PageContent.vue` 仍保留较多表格和导入导出逻辑。
- 方案 B：同时抽工具栏和表格列渲染组件。
  - 优点：行数下降更多。
  - 缺点：会触碰 slot、行操作、编辑控件和权限判断，风险明显更高。
- 方案 C：先抽导入导出 composable。
  - 优点：能减少脚本复杂度。
  - 缺点：涉及 ExcelJS、FileReader、表单校验和文件保存，验证成本更高。

## 推荐方案

- 采用方案 A。
- 淘汰方案 B/C 的原因：本轮目标是做低风险第一刀，先降低模板体积并建立后续拆分边界。

## 执行计划

- [x] 串行：新增 `frontend/src/components/CURD/PageContentToolbar.vue`。
- [x] 串行：更新 `frontend/src/components/CURD/PageContent.vue` 使用工具栏组件。
- [x] 串行：运行前端目标测试和质量门禁。
- [x] 串行：执行 review-gate 并记录结果。

## 验证矩阵

- `cd frontend && pnpm run test:unit -- curd-deprecation-governance`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run quality`
- `cd frontend && pnpm run build`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已完成只读分析，确认本轮只拆顶部工具栏组件。
- 已新增 `PageContentToolbar.vue`，`PageContent.vue` 改为传入工具栏按钮、列配置和删除禁用状态，并接收 toolbar / columnShowChange 事件。
- 首次 `lint:check` 发现新组件块顺序不符合仓库 ESLint 规则，已调整为项目要求的 `<template>`、`<script setup>`、`<style>` 顺序。

## 验证结果

- `cd frontend && pnpm run test:unit -- curd-deprecation-governance`：64 files / 172 tests passed。
- `cd frontend && pnpm run type-check`：通过。
- `cd frontend && pnpm run lint:check`：通过。
- `cd frontend && pnpm run quality`：通过，64 files / 172 tests passed。
- `cd frontend && pnpm run build`：通过，Vite 完成 2418 个模块转换。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：符合，只拆顶部工具栏组件，未修改数据获取、分页、筛选、导入导出、删除、编辑或表格列渲染逻辑。
- 安全检查：未新增外部输入处理、secret、mock、fallback 或静默降级；权限指令 `v-hasPerm` 保持原逻辑。
- 测试与验证：目标单测、类型检查、lint、前端聚合质量门禁、生产构建、文档校验、脚本编译和 diff 检查均通过。
- 复杂度检查：`PageContent.vue` 从 936 行降至 901 行；新增 `PageContentToolbar.vue` 78 行，职责单一。
- Document-refresh: not-needed
  原因：未变更 API、数据库模型、启动命令、架构流程或用户可见产品文档。
- 剩余风险：本地已验证，远端 CI 尚未执行；`PageContent.vue` 仍是 900 行级组件，后续需要继续拆表格列渲染和导入导出。
- 潜在技术债：CURD 兼容层仍处于弃用治理路径，本轮仅降低内部维护风险，不扩大外部使用面。
- 结论：通过。
