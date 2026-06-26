# PageContent 表格单元格渲染拆分任务

## 目标

- 将 `PageContent.vue` 内置表格单元格渲染分支拆为 `PageContentTableCell.vue`。
- 保持表格列配置、动态列显示、操作按钮权限、行内修改和自定义插槽行为不变。
- 继续降低 `PageContent.vue` 文件规模和模板复杂度。

## 组件边界

- `PageContent.vue`：保留表格数据、列循环、动态自定义插槽、权限计算、行操作和行内修改业务入口。
- `PageContentTableCell.vue`：负责 `image/list/url/switch/input/price/percent/icon/date/tool` 内置单元格渲染。

## 执行计划

- [x] 串行：新增 `PageContentTableCell.vue`，封装内置单元格渲染。
- [x] 串行：更新 `PageContent.vue`，将非 `custom` 分支交给新组件渲染。
- [x] 串行：通过事件把行内修改和操作按钮点击回传给父组件。
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
- Spec 符合度：通过；本轮只拆分内置表格单元格渲染，列循环、自定义插槽、行内修改、操作按钮事件、分页、导入导出和公开 API 保持在父组件或原路径。
- 安全检查：通过；本轮未新增 secret、mock、静默降级或无依据 fallback。
- 测试与验证：通过；目标单测、类型检查、lint、前端聚合质量、生产构建、文档入口脚本、脚本编译和 `git diff --check` 均已通过。
- 复杂度检查：通过；`PageContent.vue` 从 716 行降至 606 行，新组件 `PageContentTableCell.vue` 为 153 行。
- Document-refresh: not-needed；原因：本轮是内部组件结构拆分，不改变用户可见 API、数据库结构、启动方式或产品文档事实。
- 剩余风险：未做浏览器级表格交互烟测，当前验证覆盖静态类型、构建和既有单测。
