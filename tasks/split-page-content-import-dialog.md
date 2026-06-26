# PageContent 导入弹窗拆分任务

## 目标

- 将 `PageContent.vue` 内联导入弹窗拆为 `PageContentImportDialog.vue`。
- 保持导入业务执行、Excel 解析、模板下载、分页刷新和公开 API 行为不变。
- 继续降低 `PageContent.vue` 文件规模和职责耦合。

## 组件边界

- `PageContent.vue`：保留数据获取、导出、导入业务执行、Excel 解析、列表刷新和 CURD 对外能力。
- `PageContentImportDialog.vue`：负责导入弹窗 UI、上传控件、本地表单状态、校验、关闭重置和提交事件。

## 执行计划

- [x] 串行：新增 `PageContentImportDialog.vue`，封装导入弹窗展示和本地上传表单。
- [x] 串行：更新 `PageContent.vue`，通过 `v-model`、组件 ref 和事件接入导入弹窗。
- [x] 串行：清理 `PageContent.vue` 中已迁移的导入表单状态和 Element Plus 类型依赖。
- [x] 串行：运行前端质量门禁和仓库文档脚本校验。

## 验证计划

- `cd frontend && pnpm run test:unit -- curd-deprecation-governance`
- `cd frontend && pnpm run type-check`
- `cd frontend && pnpm run lint:check`
- `cd frontend && pnpm run quality`
- `cd frontend && pnpm run build`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只拆分导入弹窗 UI、本地上传状态、校验和关闭重置，导入业务执行、Excel 解析、模板下载、分页刷新和公开 API 保持在父组件。
- 安全检查：通过；本轮未新增 secret、mock、静默降级或无依据 fallback。
- 测试与验证：通过；目标单测、类型检查、lint、前端聚合质量、生产构建、文档入口脚本、脚本编译和 `git diff --check` 均已通过。
- 复杂度检查：通过；`PageContent.vue` 从 813 行降至 716 行，新组件 `PageContentImportDialog.vue` 为 139 行。
- Document-refresh: not-needed；原因：本轮是内部组件结构拆分，不改变用户可见 API、数据库结构、启动方式或产品文档事实。
- 剩余风险：未做浏览器级导入交互烟测，当前验证覆盖静态类型、构建和既有单测。
