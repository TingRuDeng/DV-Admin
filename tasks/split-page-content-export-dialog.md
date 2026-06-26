# PageContent 导出弹窗组件拆分

## 目标

- 将 `frontend/src/components/CURD/PageContent.vue` 中的导出弹窗模板、导出表单状态和表单校验拆入独立组件。
- 继续降低 `PageContent.vue` 的模板和表单状态复杂度，保持导出行为和 CURD 兼容层公开 API 不变。

## 非目标

- 不修改 ExcelJS 工作簿生成、远程导出、本地当前页导出、选中数据导出或文件保存逻辑。
- 不修改导入弹窗、分页、筛选、删除、表格列渲染或 `defineExpose()`。
- 不修改 `IContentConfig`、`IToolsButton` 等公开类型。
- 不引入新的 mock、fallback 或静默降级。

## 当前事实

- `frontend/src/components/CURD/PageContent.vue` 当前 901 行，仍是最大手写 Vue 组件。
- 导出弹窗包含 ProDialog、el-form、字段选择、数据源选择、表单校验和关闭重置逻辑。
- 导出执行逻辑 `handleExports()` 依赖 `cols`、`selectionData`、`pageData`、`lastFormData` 和 `contentConfig.exportsAction`，仍适合留在父组件。

## 组件边界

- `PageContent.vue`：继续负责数据源选择后的导出执行、ExcelJS 写入、文件保存和公开方法。
- `PageContentExportDialog.vue`：只负责导出弹窗 UI、导出表单本地状态、校验、关闭重置，并在校验通过后上抛 submit payload。

## 设计原则

- Props down / Events up：父组件传入列配置、选中数量和远程导出可用性；子组件提交已校验的导出参数。
- 表单状态内聚：导出表单的 `filename`、`sheetname`、`fields`、`origin` 留在子组件内部。
- 行为稳定：导出数据选择、ExcelJS 写入和文件下载仍由父组件原函数处理。

## 方案对比

- 方案 A：只抽 `PageContentExportDialog.vue`，父组件保留导出执行。
  - 优点：低风险，UI 和执行逻辑边界清晰。
  - 缺点：`PageContent.vue` 仍保留导入弹窗和导出执行函数。
- 方案 B：抽导出 dialog + 导出执行 composable。
  - 优点：行数下降更多。
  - 缺点：会移动 ExcelJS、远程导出和文件保存逻辑，回归范围扩大。
- 方案 C：同时抽导出和导入弹窗。
  - 优点：模板下降更多。
  - 缺点：导入涉及 FileReader、上传组件、模板下载和两类导入 action，失败面更大。

## 推荐方案

- 采用方案 A。
- 淘汰方案 B/C 的原因：当前目标是持续小步降低超大组件风险，优先拆表单 UI，不重写导出执行路径。

## 执行计划

- [x] 串行：新增 `frontend/src/components/CURD/PageContentExportDialog.vue`。
- [x] 串行：更新 `PageContent.vue` 使用导出弹窗组件，并改造 `handleExports()` 接收 submit payload。
- [x] 串行：运行前端目标验证、聚合质量门禁和构建。
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

- 已完成只读分析，确认本轮只拆导出弹窗 UI 和表单校验。
- 已新增 `PageContentExportDialog.vue`，将导出表单状态、字段选择、数据源选择、校验和关闭重置移动到子组件。
- 已更新 `PageContent.vue`，父组件通过 `submit` 事件接收导出参数，`handleExports()` 继续执行原有 ExcelJS 写入和文件保存逻辑。
- 首轮 `lint:check` 发现一处 Prettier 换行问题，已按格式规则修正。

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
- Spec 符合度：符合，只拆导出弹窗 UI 和表单校验，未修改导入弹窗、分页、筛选、删除、表格列渲染、导出执行语义或公开类型。
- 安全检查：未新增外部输入通道、secret、mock、fallback 或静默降级；导出来源仍受原有 `contentConfig.exportsAction` 可用性控制。
- 测试与验证：目标单测、类型检查、lint、前端聚合质量门禁、生产构建、文档校验、脚本编译和 diff 检查均通过。
- 复杂度检查：`PageContent.vue` 从 901 行降至 813 行；新增 `PageContentExportDialog.vue` 135 行，职责集中在导出表单 UI 与校验。
- Document-refresh: not-needed
  原因：未变更 API、数据库模型、启动命令、架构流程或用户可见产品文档。
- 剩余风险：本地门禁已通过，远端 CI 尚未执行；`PageContent.vue` 仍为 800 行级组件，后续仍需拆导入弹窗或表格列渲染。
- 潜在技术债：导入弹窗仍留在父组件，且 `PageContent.vue` 仍承担表格数据编排和 ExcelJS 导出执行。
- 结论：通过。
