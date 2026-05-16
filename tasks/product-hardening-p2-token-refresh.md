# P2 Token 刷新失败收口计划

## 目标

- 修复刷新 Token 失败时等待队列请求可能一直 pending 的正确性问题。
- 保持现有登录失效提示、跳转登录和请求重试语义不变。
- 用单测覆盖刷新成功重试和刷新失败拒绝等待请求两个关键路径。

## 非目标

- 不重写请求拦截器。
- 不调整 token 存储、登录跳转、刷新接口或后端契约。
- 不新增重试次数、退避、静默降级或 mock 成功路径。

## 当前事实

- `frontend/src/composables/auth/useTokenRefresh.ts` 的 `refreshTokenAndRetry` 会把当前请求包装成 `retryRequest` 加入 `pendingRequests`。
- 刷新成功时会遍历 `pendingRequests` 并调用 `callback()`，请求可继续重试。
- 刷新失败时当前代码先执行 `pendingRequests.length = 0`，再 `pendingRequests.forEach(() => reject(...))`，因此等待队列已为空，请求 Promise 可能不会 settle。
- 当前仓库没有 `useTokenRefresh` 单测。

## 设计原则

- 队列项必须同时保存“重试动作”和“拒绝动作”，确保刷新失败时每个等待请求都能 reject。
- 清空队列只能发生在已复制当前队列快照之后，避免遍历期间被新增请求干扰。
- 错误继续暴露给调用方，不吞异常、不伪造成功。

## 方案对比

### 方案 A：把队列项从函数改为对象

- 结构：`{ retry, reject }`。
- 成功：复制队列后逐个调用 `retry()`。
- 失败：复制队列后逐个调用 `reject(error)`。
- 优点：语义明确，能同时覆盖成功重试和失败拒绝。
- 缺点：改动比单独调换清空顺序略多。

### 方案 B：仅调整清空队列顺序

- 失败时先 `forEach(reject)` 再清空队列。
- 优点：改动最小。
- 缺点：当前队列只保存 retry callback，没有保存每个请求自己的 reject，仍无法正确拒绝所有等待请求。

## 推荐方案

采用方案 A。

淘汰方案 B 的原因：它无法从根因上表达“队列里每个请求都有自己的 reject”，容易继续留下悬挂 Promise。

## 执行计划

- [x] 新增 `frontend/src/composables/auth/__tests__/useTokenRefresh.test.ts`，先覆盖刷新失败时等待请求必须 reject。
- [x] 确认新测试在现有代码下失败。
- [x] 将 `pendingRequests` 队列项改为 `{ retry, reject }`，刷新成功/失败都基于队列快照处理。
- [x] 增加刷新成功重试测试，确保成功路径未被破坏。
- [x] 运行最小充分验证并记录结果。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| Token 刷新队列 | `pnpm --dir frontend run test:unit -- useTokenRefresh` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 前端构建 | `pnpm --dir frontend run build` |
| 文档计划 | `python3 scripts/validate_docs.py . --profile generic` |

## 进度记录

- 2026-05-16：确认 P0/P1 已合并，P2 选定为 Token 刷新失败请求悬挂问题。
- 2026-05-16：新增 `useTokenRefresh` 单测；RED 阶段失败为 `pending`，证明刷新失败时等待请求未 reject。
- 2026-05-16：队列项改为 `{ retry, reject }` 并基于快照处理；`pnpm --dir frontend run test:unit -- useTokenRefresh` 通过，33 个测试文件、97 条测试全绿。
- 2026-05-16：`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke`、`python3 scripts/validate_docs.py . --profile generic` 通过。
- 2026-05-16：按复杂度约束拆分 `useTokenRefresh` 队列 helper；`pnpm --dir frontend run test:unit -- useTokenRefresh` 仍通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只修复刷新 Token 失败时等待请求可能 pending 的问题，未改登录跳转、请求拦截器或后端契约。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径，刷新失败继续显式 reject 给调用方。
- 测试与验证：通过；`useTokenRefresh` 单测先红后绿，完整前端质量门禁、生产构建、登录 smoke 和文档校验均通过。
- 复杂度检查：通过；`useTokenRefresh` 已拆分队列 helper，文件 134 行，单函数保持在 50 行以内。
- Document-refresh: not-needed。原因：未改变 API、数据库、用户文档或架构契约，只新增本轮执行计划和验证记录。
- 剩余风险：本轮未改变刷新期间新请求入队后的并发策略，只修复已进入队列请求的失败结算问题。
- 潜在技术债：`httpRequest` 仍沿用既有 `any` 形态，后续可随前端 API 类型治理统一收紧。
- 结论：通过。
