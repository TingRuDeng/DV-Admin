# P8 WebSocket 实例注册表类型收口计划

## 目的

在不改变 WebSocket 初始化、注册和清理行为的前提下，收口全局 WebSocket 实例注册表的 `any` 类型边界，避免实时连接路径继续扩散不透明实例。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核 WebSocket 插件实例生命周期的 AI 代理

## 一分钟摘要

- 当前 `plugins/websocket.ts` 使用 `Map<string, any>` 管理 WebSocket 实例，注册函数参数也是 `any`。
- 本轮定义最小实例接口，只表达清理阶段真实依赖的 `disconnect` / `closeWebSocket` 能力。
- 新增守卫测试，防止注册表类型重新退回 `any`。
- 不改初始化时机、不改注册 key、不改清理顺序。

## ai_summary

```yaml
purpose: "收口 WebSocket 插件实例注册表的 any 类型边界。"
read_when:
  - "修改 frontend/src/plugins/websocket.ts 的实例注册、获取或清理逻辑前"
  - "排查 WebSocket 类型治理或产品化治理后续项时"
source_of_truth:
  - "frontend/src/plugins/websocket.ts"
  - "frontend/src/plugins/__tests__/websocket-registry-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- websocket-registry-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "WebSocket 实例注册表改为其他生命周期管理方式"
```

## 权威边界

本计划只描述 P8 小切片。WebSocket 定时器类型治理以 `tasks/product-hardening-p7-websocket-timer-types.md` 为准；连接、重连和订阅行为不属于本轮范围。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因注册表 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验和 diff 检查。

## 执行清单

- [x] 新增 WebSocket 实例注册表类型治理测试，并确认当前代码会失败
- [x] 为 WebSocket 注册表定义最小实例接口
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮只收口 WebSocket 插件实例注册表类型，未改变初始化时机、注册 key、清理顺序或连接行为。

安全检查：通过。未新增外部输入、网络端点、鉴权逻辑或密钥；敏感词扫描未命中新增内容。

测试与验证：通过。已完成红绿测试、目标类型治理测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。新增一个最小生命周期接口，函数长度、嵌套深度和参数数量未增加。

Document-refresh: needed
原因：P8 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未进行真实 WebSocket 服务联调；本轮只替换类型边界和无效空值判断，不改变运行时控制流。

潜在技术债：WebSocket 消息载荷解析仍有可进一步收口的类型边界，但不属于本轮小切片。

结论：通过。
