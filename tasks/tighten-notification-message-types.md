# Notification 订阅消息类型治理

## 目标

- [x] 串行：确认 `Notification` 订阅消息来源和现有通知数据类型。
- [x] 串行：移除订阅回调 `message: any`，并在消息边界做显式解析与校验。
- [x] 串行：补充治理测试，防止订阅消息类型回退。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/Notification/index.vue`
- 修改：`frontend/src/api/system/notice-api.ts`
- 新增：`frontend/src/components/__tests__/notification-message-type-governance.spec.ts`
- 不涉及：WebSocket 连接管理器、通知 API 路径、通知详情弹窗、后端 API

## 决策

- 使用 `@stomp/stompjs` 的 `IMessage` 作为订阅消息类型。
- `JSON.parse` 结果按 `unknown` 处理，先校验为对象，再提取通知消息字段。
- 通知发布时间允许 `string | Date`，原因是接口和 WebSocket JSON 实际到前端时会以字符串表示时间。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/notification-message-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
