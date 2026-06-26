# PageContent 工具栏配置逻辑抽取任务

## 目标

- 将 `PageContent.vue` 中的按钮默认配置、权限标识组合和工具栏按钮派生逻辑抽到 composable。
- 保持顶部工具栏、表格操作列、按钮权限判断和业务动作分发行为不变。
- 继续降低 `PageContent.vue` 脚本职责和文件规模。

## 组件边界

- `PageContent.vue`：保留页面数据、表格状态、业务动作分发、导入导出和对外方法。
- `usePageContentToolbarConfig.ts`：负责默认按钮配置、权限标识解析、按钮权限检查和 toolbar/table toolbar 派生。

## 执行计划

- [x] 串行：新增 `usePageContentToolbarConfig.ts`，迁移按钮配置和权限工具逻辑。
- [x] 串行：更新 `PageContent.vue`，从 composable 获取 `toolbarLeftBtn`、`toolbarRightBtn`、`tableToolbarBtn` 和 `hasButtonPerm`。
- [x] 串行：清理 `PageContent.vue` 中已迁移的配置状态、helper 和无用导入。
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
- Spec 符合度：通过；本轮只抽取按钮默认配置、权限标识组合、按钮权限判断和 toolbar/table toolbar 派生逻辑，顶部工具栏、表格操作列、业务动作分发和公开 API 保持不变。
- 安全检查：通过；本轮未新增 secret、mock、静默降级或无依据 fallback，未知默认按钮名继续暴露配置错误。
- 测试与验证：通过；目标单测、类型检查、lint、前端聚合质量、生产构建、文档入口脚本、脚本编译和 `git diff --check` 均已通过。
- 复杂度检查：通过；`PageContent.vue` 从 606 行降至 534 行，新 composable `usePageContentToolbarConfig.ts` 为 103 行。
- Document-refresh: not-needed；原因：本轮是内部工具栏配置逻辑抽取，不改变用户可见 API、数据库结构、启动方式或产品文档事实。
- 剩余风险：未做浏览器级工具栏点击烟测，当前验证覆盖静态类型、构建和既有单测。
