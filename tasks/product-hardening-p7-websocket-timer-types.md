# P7 WebSocket 定时器类型收口计划

## 目的

在不改变 WebSocket 连接、重连和订阅行为的前提下，收口组合式函数中的定时器句柄类型，减少 `any` 在实时连接路径中的扩散。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核 WebSocket 组合式函数类型边界的 AI 代理

## 一分钟摘要

- 当前 `useStomp`、`useOnlineCount`、`useDictSync` 仍以 `any` 保存定时器句柄。
- 本轮只将定时器句柄改为 `ReturnType<typeof setTimeout> | undefined`。
- 新增守卫测试，防止这些定时器字段重新退回 `any`。
- 不改 WebSocket 行为、不改重连策略、不改订阅主题。

## ai_summary

```yaml
purpose: "收口 WebSocket 组合式函数中的定时器句柄 any 类型。"
read_when:
  - "修改 useStomp、useOnlineCount 或 useDictSync 的定时器逻辑前"
  - "排查 WebSocket 类型治理或产品化治理后续项时"
source_of_truth:
  - "frontend/src/composables/websocket/useStomp.ts"
  - "frontend/src/composables/websocket/useOnlineCount.ts"
  - "frontend/src/composables/websocket/useDictSync.ts"
  - "frontend/src/composables/websocket/__tests__/websocket-timer-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- websocket-timer-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "WebSocket 组合式函数改用其他定时器或调度机制"
```

## 权威边界

本计划只描述 P7 小切片。WebSocket 日志治理以 `tasks/product-hardening-p1-websocket-logging.md` 为准；Token 刷新与 API 请求治理不属于本轮范围。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因定时器 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验和 diff 检查。

## 执行清单

- [x] 新增 WebSocket 定时器类型治理测试，并确认当前代码会失败
- [x] 将 WebSocket 组合式函数定时器句柄改为显式类型
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮只收口 WebSocket 组合式函数中的定时器句柄类型，未改变连接、重连、订阅主题或日志行为。

安全检查：通过。未新增外部输入处理、网络端点、鉴权逻辑或密钥；敏感词扫描未命中新增内容。

测试与验证：通过。已完成红绿测试、目标类型治理测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。仅替换局部变量类型和清空值，未新增复杂分支、嵌套或长函数。

Document-refresh: needed
原因：P7 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未进行真实 WebSocket 服务联调；本轮没有改变运行时控制流，风险主要由类型检查和构建覆盖。

潜在技术债：WebSocket 模块仍有实例注册和消息载荷类型边界可继续收口，但不属于本轮小切片。

结论：通过。
