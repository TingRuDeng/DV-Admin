# P0 产品化治理执行计划

## 目标

- 补齐成熟产品发布前最关键的安全、契约和质量门禁闭环。
- 优先处理已经有代码证据的问题：富文本渲染、E2E 配置失配、CI 门禁缺口、双后端响应契约漂移。
- 每一项改动都必须能被自动化命令验证。

## 非目标

- 不做大规模 UI 重设计。
- 不统一 Django 与 FastAPI 的全部模型差异。
- 不继续推进 RouteMeta、KeepAlive/cacheKey、ProTable/ProForm 页面收口；这些已经有基础闭环，本轮只补成熟产品门禁。
- 不引入 mock 成功路径或静默降级。

## 当前事实

- `frontend/src/views/system/notice/components/MyNotice.vue`、`frontend/src/views/system/notice/index.vue`、`frontend/src/components/Notification/index.vue` 存在 `v-html` 富文本渲染入口。
- `frontend/playwright.config.ts` 使用 `http://localhost:5173`，但 `frontend/.env.development` 默认端口是 `9527`。
- `.github/workflows/quality-gates.yml` 当前未运行 `frontend` 的 `test:e2e`，也未运行 `scripts/validate_docs.py`。
- Django 响应中间件输出 `{msg, errors, code, data}`；FastAPI `ResponseModel` 输出 `{code, message, data}`。
- `frontend/src/utils/request.ts` 当前只解构 `code/data/msg/errors`，错误文案对 FastAPI `message` 支持不足。
- 当前工作区已有未提交文档改动，本任务执行时应避免覆盖这些改动。

## 决策日志

- 采用“小步硬化”方案：先把高风险点纳入测试和 CI，再继续扩展产品能力。
- 不在本轮重写请求层或后端响应模型；先增加前端兼容读取和契约测试，降低破坏面。
- 富文本安全优先选择前端统一净化组件/工具，并补测试守卫；后端内容治理留到下一阶段。
- 建议在独立分支或 worktree 中实施，避免污染当前文档升级工作区。

## 执行计划

- [x] 建立隔离工作区：从最新 `origin/master` 创建 `codex/product-hardening-p0`。
- [x] 富文本安全收口：新增统一安全 HTML 渲染工具或组件，并替换通知相关 `v-html` 入口。
- [x] 富文本测试：补充恶意 HTML、允许标签、空内容等用例。
- [x] E2E 配置修复：让 Playwright 端口读取 `VITE_APP_PORT` 或统一到前端默认端口。
- [x] CI 门禁增强：加入文档校验和最小 E2E smoke；必要时先限定为稳定 smoke，不扩大到全流程。
- [x] 请求错误兼容：让 `frontend/src/utils/request.ts` 同时支持 `msg/errors/message`，并补响应处理测试。
- [x] 双后端契约测试：增加最小响应 envelope 契约检查，覆盖 Django/FastAPI 已知差异的前端兼容行为。
- [x] 清理生产调试输出：先处理明显页面调试日志，不扩大到 WebSocket 全量重构。
- [x] 运行最小充分验证并记录结果。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| 文档门禁 | `python3 scripts/validate_docs.py` |
| 前端类型与单测 | `pnpm --dir frontend run type-check`、`pnpm --dir frontend run test:unit` |
| E2E 配置 | `pnpm --dir frontend run test:e2e` |
| CI 配置语法 | 检查 `.github/workflows/quality-gates.yml` 结构和命令可执行性 |
| 后端契约影响 | 根据实际改动运行 Django/FastAPI 相关测试 |

## 风险与失败场景

- E2E 可能依赖后端和测试数据；如果本地不可稳定运行，需要先把 smoke 范围收窄到可控登录前页面或明确测试数据准备。
- 富文本净化如果过严，可能影响通知内容展示；如果过松，则不能解决 XSS 风险。
- CI 加 E2E 后可能增加耗时，需要先做最小 smoke，再逐步扩展。
- 当前工作区已有未提交文档改动，执行阶段应使用隔离分支或 worktree。

## 进度记录

- 2026-05-16：完成 P0 执行前规划，等待用户确认后进入编码。
- 2026-05-16：从 `origin/master` 创建 `codex/product-hardening-p0`，开始执行富文本安全收口。
- 2026-05-16：完成 `SafeHtml` 与 `sanitizeHtml`，通知详情改为统一安全渲染；`pnpm --dir frontend run test:unit -- safe-html notice-html-safety`、`pnpm --dir frontend run type-check` 通过。
- 2026-05-16：修复 Playwright 端口来源并新增 `test:e2e:smoke`；`pnpm --dir frontend run test:e2e:smoke` 通过。
- 2026-05-16：前端请求错误文案兼容 Django `msg/errors` 与 FastAPI `message`；`pnpm --dir frontend run test:unit -- api-error`、`pnpm --dir frontend run type-check` 通过。
- 2026-05-16：CI 前端门禁加入文档校验和登录页 smoke E2E；明显页面调试 `console.log` 已清理，WebSocket 日志治理保留到后续专项。
- 2026-05-16：完成最小充分验证：`python3 scripts/validate_docs.py . --profile generic`、`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke` 均通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过。所有 P0 执行项已完成，未扩大到后端模型统一或 WebSocket 专项重构。
- 安全检查：通过。通知详情裸 `v-html` 已替换为 `SafeHtml`，富文本入口通过 `sanitizeHtml` 做白名单净化；未新增 secret、mock 或静默降级。
- 测试与验证：通过。`python3 scripts/validate_docs.py . --profile generic`、`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke` 均通过。
- 复杂度检查：通过。新增工具和测试文件职责单一，未出现大文件或大函数扩张。
- Document-refresh: needed。原因：P0 执行计划本身需要同步完成状态和验证结果，已更新本文件。
- 剩余风险：WebSocket 相关 `console.log` 仍保留，需后续连接管理专项统一处理；当前 E2E 只覆盖登录页 smoke，未覆盖登录后完整业务流。
- 潜在技术债：前端富文本净化当前在客户端兜底，后续仍应在后端保存或发布边界增加内容安全策略。
- 结论：通过。
