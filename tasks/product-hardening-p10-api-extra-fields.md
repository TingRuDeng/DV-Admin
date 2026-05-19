# P10 API 扩展字段类型收口计划

## 目的

将测试模块和字典项 API 类型里的扩展字段索引签名从 `any` 收口为 `unknown`，避免未知接口字段继续绕过类型边界。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核 API 类型定义和请求驱动抽象边界的 AI 代理

## 一分钟摘要

- 当前 `dict-items-api.ts`、`project-api.ts`、`cases-api.ts` 仍用 `[key: string]: any` 表达后端扩展字段。
- 本轮只把这些扩展字段收口为 `[key: string]: unknown`。
- 新增守卫测试，防止 API 扩展字段类型回退到 `any`。
- 不改 API 路径、请求参数、响应结构或页面调用方式。

## ai_summary

```yaml
purpose: "收口 API 类型定义中的扩展字段 any 边界。"
read_when:
  - "修改 frontend/src/api/system/dict-items-api.ts 前"
  - "修改 frontend/src/api/test/project-api.ts 或 frontend/src/api/test/cases-api.ts 前"
  - "排查 API 类型治理或请求驱动抽象后续项时"
source_of_truth:
  - "frontend/src/api/system/dict-items-api.ts"
  - "frontend/src/api/test/project-api.ts"
  - "frontend/src/api/test/cases-api.ts"
  - "frontend/src/api/__tests__/api-extra-fields-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- api-extra-fields-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "测试模块 API 或字典项 API 的扩展字段契约变化"
```

## 权威边界

本计划只描述 P10 小切片。全局 API 响应默认类型治理以 `tasks/product-hardening-p9-global-route-types.md` 为准；ProTable 请求抽象不属于本轮范围。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因 API 扩展字段 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验、diff 检查和生产构建。

## 执行清单

- [x] 新增 API 扩展字段类型治理测试，并确认当前代码会失败
- [x] 将目标 API 类型的扩展字段索引签名改为 `unknown`
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮只收口目标 API 类型的扩展字段索引签名，未改变 API 路径、请求参数、响应结构或页面调用方式。

安全检查：通过。未新增外部输入、网络端点、鉴权逻辑或密钥；敏感信息扫描未命中新增内容。

测试与验证：通过。已完成红绿测试、目标类型治理测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。只替换类型索引签名和新增守卫测试，未新增运行时分支、嵌套或复杂函数。

Document-refresh: needed
原因：P10 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未做测试模块页面的浏览器交互回归；本轮不改运行时逻辑，风险主要由类型检查、单测和构建覆盖。

潜在技术债：其他组件和 CURD 抽象中仍存在历史 `any`，需要按更小范围继续分批收口。

结论：通过。
