# Stomp 连接状态 helper 抽取

## 目标

- [x] 串行：确认 `stomp-connection-manager.ts` 当前连接状态职责和行数边界。
- [x] 串行：抽取连接状态与重连次数更新 helper。
- [x] 串行：补充治理测试，防止 `stomp-connection-manager.ts` 回到 300 行及以上。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/composables/websocket/stomp-connection-manager.ts`
- 新增：`frontend/src/composables/websocket/stomp-connection-state.ts`
- 修改：`frontend/src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts`
- 不涉及：STOMP 客户端创建、订阅注册表、重连策略计算、认证错误处理、公开 manager API

## 模块边界

- `stomp-connection-manager.ts`：继续负责客户端生命周期、连接、断开、重连调度和订阅转发。
- `stomp-connection-state.ts`：只负责 `isConnected`、`reconnectCount` 的读写和外部变更回调。

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

- 通过：`cd frontend && ./node_modules/.bin/vitest run src/composables/websocket/__tests__/stomp-connection-manager.test.ts src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts`，2 个测试文件、9 个用例通过。
- 通过：`cd frontend && ./node_modules/.bin/vue-tsc --noEmit`。
- 通过：`cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`。
- 通过：`cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`。
- 通过：`cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`。
- 通过：`cd frontend && ./node_modules/.bin/vitest run`，85 个测试文件、240 个用例通过。
- 通过：`python3 scripts/validate_docs.py . --profile generic`。
- 通过：`git diff --check`。
- 行数：`frontend/src/composables/websocket/stomp-connection-manager.ts` 为 282 行，低于 300 行硬限制。

## Review Gate

- 终态：finished
- Spec 符合度：符合，仅抽取连接状态与重连次数读写 helper。
- 安全检查：未新增外部输入、网络请求、认证逻辑、存储逻辑或 secret。
- 测试与验证：目标测试、全量前端单测、类型检查、静态检查、格式检查、样式检查、文档校验和 diff 空白检查均通过。
- 复杂度检查：`stomp-connection-manager.ts` 从 290 行降至 282 行，新增 `stomp-connection-state.ts` 为 38 行，并扩展治理测试覆盖新 helper。
- 文档刷新判断：Document-refresh: not-needed
- 原因：本轮不改变 API、数据库模型、架构流程或运行契约。
- 剩余风险：未做真实 WebSocket 服务联调；本轮为内部状态读写等价抽取，目标测试覆盖连接、断开、订阅和异常重连。
- 潜在技术债：manager 仍承载客户端生命周期和重连调度，后续可继续按动作边界拆分。
- 结论：通过。
