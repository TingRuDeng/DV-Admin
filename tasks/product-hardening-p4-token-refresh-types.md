# P4 Token 刷新类型收口计划

## 目标

- 收紧 `frontend/src/composables/auth/useTokenRefresh.ts` 的 `any` 类型边界。
- 延续 P2 的 Token 刷新队列治理，避免请求重试依赖继续以 `any` 传播。
- 用守卫测试防止该模块重新引入 `any`。

## 非目标

- 不重写 `frontend/src/utils/request.ts` 响应拦截器。
- 不批量替换全部 API 文件中的 `request<any, T>`。
- 不调整 Token 刷新、登录跳转、请求重试或后端契约行为。

## 当前事实

- `useTokenRefresh.ts` 的 `PendingRequestOptions.httpRequest`、`resolve` 和 `refreshTokenAndRetry` 返回值仍使用 `any`。
- P2 已通过单测覆盖刷新失败 reject 和刷新成功重试两条行为路径。
- `docs/TECH_DEBT.md` 已把前端类型定义不完整列为中优先级技术债。

## 决策日志

- 采用“小切片类型收口”：先处理 P2 明确留下的 `useTokenRefresh` 类型债。
- 不做全量 API 泛型迁移，避免一次性触碰所有接口调用文件。

## 执行计划

- [x] 新增 `useTokenRefresh` 类型治理测试，并确认当前代码会失败。
- [x] 将 `httpRequest` 注入点改为最小函数接口，返回值使用 `unknown`。
- [x] 保持已有 Token 刷新行为测试通过。
- [x] 运行前端类型检查、目标单测和文档校验。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| 类型治理测试 | `pnpm --dir frontend run test:unit -- useTokenRefresh-type-governance` |
| Token 刷新行为 | `pnpm --dir frontend run test:unit -- useTokenRefresh` |
| 前端类型检查 | `pnpm --dir frontend run type-check` |
| 文档校验 | `python3 scripts/validate_docs.py . --profile generic` |

## HARD-GATE

用户已要求继续推进，本轮按 P4 小切片执行；如执行中发现需要触碰请求拦截器或全量 API 泛型迁移，则先停下重新规划。

## 进度记录

- 2026-05-18：确认 P0-P3 已合并，选定 P2 Review 遗留的 `useTokenRefresh` 类型债作为 P4 小切片。
- 2026-05-18：新增 `useTokenRefresh-type-governance` 守卫测试；RED 阶段失败并定位 4 处 `any`。
- 2026-05-18：将 `httpRequest` 注入点改为 `TokenRefreshHttpRequest`，Promise 结果改为 `unknown`；目标测试、行为测试和类型检查通过。
- 2026-05-18：`pnpm --dir frontend run quality`、`python3 scripts/validate_docs.py . --profile generic`、`git diff --check` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收口 `useTokenRefresh.ts` 的 P2 遗留类型债，未扩大到全量 API 泛型迁移。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径，Token 刷新失败仍显式 reject。
- 测试与验证：通过；类型治理测试先红后绿，原 Token 刷新行为测试、前端质量聚合、文档校验和 diff 检查均通过。
- 复杂度检查：通过；新增守卫测试 22 行，`useTokenRefresh.ts` 仅新增一个最小函数类型别名。
- Document-refresh: not-needed。原因：未改变 API、数据库、架构契约或用户可见行为，只更新本轮任务计划与验证记录。
- 剩余风险：全量 API 文件中的 `request<any, T>` 仍未处理，需后续按模块分批治理。
- 潜在技术债：请求层 `httpRequest` 泛型和接口层响应类型仍有较多 `any`，本轮只处理 Token 刷新重试链路。
- 结论：通过。
