# P1 运行时错误日志治理计划

## 目标

- 将前端关键运行时路径中的直接 `console.error` 收口到统一 `createLogger`。
- 避免认证、请求拦截、路由守卫和用户状态模块继续各自散落错误输出。
- 保持错误暴露，不引入静默回退、mock、伪成功或吞异常。

## 非目标

- 不调整登录、刷新 token、路由守卫、请求拦截器的业务流程。
- 不改 API 契约、错误码规范或后端响应格式。
- 不一次性清理所有组件和 demo 页的 `console`，避免扩大影响面。

## 当前事实

- `frontend/src/utils/logger.ts` 已提供统一日志出口。
- `frontend/src/utils/request.ts` 仍有请求/响应拦截器直接 `console.error`。
- `frontend/src/utils/auth.ts` 仍有登录重定向失败直接 `console.error`。
- `frontend/src/plugins/permission.ts` 的路由守卫异常存在两次重复 `console.error`。
- `frontend/src/composables/auth/useTokenRefresh.ts` 仍在 token 刷新与重试失败时直接 `console.error`。
- `frontend/src/store/modules/user-store.ts` 仍在 refresh token 失败时直接 `console.error`。
- 组件层、历史 `CURD` 兼容层和 demo 页仍有若干直接 `console`，但不属于本轮关键运行时治理范围。

## 设计原则

- 日志治理只改变输出出口，不改变控制流。
- `warn/error` 保持可见，避免真实故障被调试开关吞掉。
- 关键路径先收口：请求、认证、权限、用户状态优先于普通组件。
- 用守卫测试防止关键路径回归，而不是靠人工搜索。

## 方案对比

### 方案 A：只收口关键运行时路径

- 范围：`request.ts`、`auth.ts`、`permission.ts`、`useTokenRefresh.ts`、`user-store.ts`。
- 优点：影响面小，覆盖成熟产品发布最关键的故障链路。
- 缺点：普通组件、demo 页和历史兼容层仍会保留少量直接 `console`。

### 方案 B：全量禁止 `frontend/src` 直接 `console`

- 范围：所有前端源码。
- 优点：治理彻底。
- 缺点：会牵动上传、复制、菜单样式、历史 CURD、demo 页面等非关键路径，容易把日志治理变成大范围行为重构。

## 推荐方案

采用方案 A。

淘汰方案 B 的原因：本轮目标是成熟产品关键路径治理，不应把历史兼容层和 demo 页一起纳入，否则验证成本与回归风险不成比例。

## 执行计划

- [x] 新增关键运行时日志守卫测试，先证明当前直接 `console.error` 会被测试拦住。
- [x] 在 `frontend/src/utils/request.ts` 引入 `createLogger("request")`，替换拦截器直接 `console.error`。
- [x] 在 `frontend/src/utils/auth.ts` 引入 `createLogger("auth")`，替换登录重定向错误输出。
- [x] 在 `frontend/src/plugins/permission.ts` 引入 `createLogger("permission")`，去掉重复错误输出并保留一次明确错误日志。
- [x] 在 `frontend/src/composables/auth/useTokenRefresh.ts` 引入 `createLogger("useTokenRefresh")`，替换重试和刷新失败日志。
- [x] 在 `frontend/src/store/modules/user-store.ts` 引入 `createLogger("userStore")`，替换 refresh token 失败日志。
- [x] 运行最小充分验证并记录结果。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| 关键路径 console 守卫 | `pnpm --dir frontend run test:unit -- runtime-error-logging` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 前端构建 | `pnpm --dir frontend run build` |
| 文档计划 | `python3 scripts/validate_docs.py . --profile generic` |

## HARD-GATE

用户确认前不进行业务代码修改。

## 进度记录

- 2026-05-16：#47 已合并，确认前端 backlog 三块主线已完成；本轮拟推进关键运行时错误日志治理。
- 2026-05-16：新增 `runtime-error-logging-governance` 守卫测试；`pnpm --dir frontend run test:unit -- runtime-error-logging` 按预期失败，列出 5 个关键运行时文件仍绕过统一 logger。
- 2026-05-16：关键运行时文件已改为统一 logger；`pnpm --dir frontend run test:unit -- runtime-error-logging` 通过，32 个测试文件、95 条测试全绿。
- 2026-05-16：`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke`、`python3 scripts/validate_docs.py . --profile generic` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收口 `request`、`auth`、`permission`、`useTokenRefresh`、`user-store` 关键运行时路径，没有扩大到组件、demo 页或历史 CURD。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径，错误仍通过 logger 的 `error` 级别暴露。
- 测试与验证：通过；守卫测试先红后绿，完整前端质量门禁、生产构建、登录 smoke 和文档校验均通过。
- 复杂度检查：新增守卫测试 27 行；被改运行时文件均小于 300 行，本轮没有新增长函数或深层嵌套。
- Document-refresh: not-needed。原因：未改变 API、数据库、用户文档或架构契约，只新增本轮执行计划和验证记录。
- 剩余风险：本轮未覆盖组件层、demo 页和历史 CURD 兼容层的直接 `console`，这些不在关键运行时链路范围内。
- 潜在技术债：token 刷新失败分支现有队列 reject 时序可读性较差，但本轮按日志治理边界未改控制流。
- 结论：通过。
