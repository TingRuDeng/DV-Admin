# Stomp 连接计时器抽取

## 目标

- [x] 串行：确认 `stomp-connection-manager.ts` 当前行数和计时器职责。
- [x] 串行：将重连计时器和连接超时计时器管理抽到专用 helper。
- [x] 串行：补充治理测试，防止连接管理器回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/composables/websocket/stomp-connection-manager.ts`
- 新增：`frontend/src/composables/websocket/stomp-connection-timers.ts`
- 修改：`frontend/src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts`
- 不涉及：STOMP 客户端创建、订阅注册表、重连策略计算、认证错误处理、公开 API

## 职责边界

- `stomp-connection-manager.ts`：继续负责连接状态、STOMP 事件、重连决策和公开 API。
- `stomp-connection-timers.ts`：只负责计时器句柄保存、启动、清理和重置，不持有连接业务状态。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/composables/websocket/__tests__/stomp-connection-manager.test.ts src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- `cd frontend && ./node_modules/.bin/vitest run src/composables/websocket/__tests__/stomp-connection-manager.test.ts src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts`：通过，2 个测试文件、8 个用例。
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`：通过。
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `cd frontend && ./node_modules/.bin/vitest run`：通过，85 个测试文件、235 个用例。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `git diff --check`：通过。
- `wc -l frontend/src/composables/websocket/stomp-connection-manager.ts frontend/src/composables/websocket/stomp-connection-timers.ts`：`stomp-connection-manager.ts` 290 行，`stomp-connection-timers.ts` 39 行。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只抽取重连计时器和连接超时计时器管理，没有改变 STOMP 客户端创建、订阅注册表、重连策略计算、认证错误处理或公开 API。
- 安全检查：通过；未新增外部输入处理、secret、mock、fallback 或静默降级。
- 复杂度检查：通过；`stomp-connection-manager.ts` 从 299 行降至 290 行，新增 helper 为 39 行，均低于 300 行硬约束。
- Document-refresh: not-needed。原因：本轮不改变用户功能、API、数据库模型或架构事实。
- 剩余风险：未启动真实 WebSocket 服务做运行时联调；当前由 fake timer 单测覆盖连接超时、异常关闭重连和手动断开不重连行为。
- 潜在技术债：连接管理器仍同时承担状态、事件绑定和客户端生命周期编排，后续如继续治理，可单独拆事件绑定或客户端生命周期 helper。
