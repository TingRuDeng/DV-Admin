# P9 全局路由类型边界收口计划

## 目的

收口全局 API 响应、标签页 query 和路由标题翻译工具中的 `any` 类型边界，避免公共类型继续向页面和工具函数扩散不透明数据。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核全局路由和 API 类型契约的 AI 代理

## 一分钟摘要

- 当前 `ApiResponse<T = any>`、`TagView.query?: any` 和 `translateRouteTitle(title: any)` 仍使用 `any`。
- 本轮将默认 API payload 收口为 `unknown`，将标签页 query 对齐为 `vue-router` 的 `LocationQuery`。
- 路由标题翻译工具接受可选字符串，保持现有国际化 key 拼接逻辑不变。
- 请求拦截器只补类型适配，不改业务响应解包行为、标签页状态流、菜单或面包屑渲染。

## ai_summary

```yaml
purpose: "收口全局路由和 API 工具类型中的 any 边界。"
read_when:
  - "修改 frontend/src/types/global.d.ts 或 frontend/src/utils/i18n.ts 前"
  - "排查 TagView query、ApiResponse 默认 payload 或路由标题翻译类型问题时"
source_of_truth:
  - "frontend/src/types/global.d.ts"
  - "frontend/src/utils/i18n.ts"
  - "frontend/src/utils/request.ts"
  - "frontend/src/types/__tests__/global-route-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- global-route-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "全局 API 响应、标签页模型或路由标题翻译契约变化"
```

## 权威边界

本计划只描述 P9 小切片。请求泛型治理以 `tasks/product-hardening-p5-api-request-types.md` 为准；标签页缓存键治理以对应 RouteMeta / KeepAlive 文档和测试为准。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因公共类型 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验和 diff 检查。

## 执行清单

- [x] 新增全局路由/API 类型治理测试，并确认当前代码会失败
- [x] 将 `ApiResponse` 默认 payload、`TagView.query` 和 `translateRouteTitle` 参数改为显式类型
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮收口 `ApiResponse` 默认 payload、`TagView.query` 和路由标题翻译参数类型；请求拦截器只补 Axios 类型适配，未改变业务响应解包行为。

安全检查：通过。未新增外部输入、网络端点、鉴权逻辑或密钥；敏感信息扫描未命中新增内容。

测试与验证：通过。已完成红绿测试、目标类型治理测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。`handleBusinessResponse` 为 24 行小函数，未新增复杂嵌套、魔法数字或多参数接口。

Document-refresh: needed
原因：P9 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未做浏览器端真实登录和标签页交互回归；本轮行为保持原响应解包与标签页 query 传递方式，主要由类型检查、单测和构建覆盖。

潜在技术债：`request.ts` 仍需要一次类型适配来对齐 Axios 拦截器定义与项目业务 data 解包模式，后续若重构请求实例可进一步消除该适配。

结论：通过。
