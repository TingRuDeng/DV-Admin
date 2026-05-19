# P11 标签页返回值类型收口计划

## 目的

收口标签页关闭和批量关闭链路中的返回值类型，避免 `TagsView` 与 `tags-view-store` 继续通过 `any` 传递已访问标签列表和缓存标签列表。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核 RouteMeta、KeepAlive/cacheKey 和标签页缓存链路的 AI 代理

## 一分钟摘要

- 当前 `tags-view-store.ts` 的 `delView` 回调结果仍显式标成 `any`。
- 当前 `TagsView/index.vue` 的关闭标签、关闭左右侧、关闭全部回调结果仍显式标成 `any`。
- 当前横向滚轮兼容逻辑通过 `(event as any).wheelDelta` 访问旧浏览器字段。
- 本轮只补明确返回值类型和最小事件类型，不改变标签关闭、路由跳转或缓存失效行为。

## ai_summary

```yaml
purpose: "收口 TagsView 与 tags-view-store 标签关闭返回值 any 边界。"
read_when:
  - "修改 frontend/src/store/modules/tags-view-store.ts 前"
  - "修改 frontend/src/layouts/components/TagsView/index.vue 前"
  - "排查 KeepAlive/cacheKey 或标签页关闭跳转行为时"
source_of_truth:
  - "frontend/src/store/modules/tags-view-store.ts"
  - "frontend/src/layouts/components/TagsView/index.vue"
  - "frontend/src/layouts/components/__tests__/tags-view-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- tags-view-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "标签页关闭返回结构、KeepAlive 缓存键或路由跳转策略变化"
```

## 权威边界

本计划只描述 P11 小切片。全局 `TagView` 结构以 `frontend/src/types/global.d.ts` 为准；缓存键生成规则以 `frontend/src/utils/view-cache.ts` 为准；ProTable/ProForm 抽象不属于本轮范围。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因标签页类型边界 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验、diff 检查和生产构建。

## 执行清单

- [x] 新增标签页类型治理测试，并确认当前代码会失败
- [x] 为标签页关闭结果定义显式返回值类型
- [x] 移除 TagsView 回调结果和旧滚轮事件访问中的 `any`
- [x] 运行目标测试、前端类型检查、质量聚合、文档校验、diff 检查和生产构建
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮只收口标签页关闭返回值和旧滚轮事件访问的类型边界，未改变标签关闭、路由跳转、KeepAlive 缓存键或缓存失效逻辑。

安全检查：通过。未新增外部输入、网络端点、鉴权逻辑或密钥；新增和修改文件未命中敏感凭据关键字扫描。

测试与验证：通过。已完成红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。新增 `TagsViewChangeResult` 类型和一个守卫测试；未新增运行时分支，未扩大组件职责。

Document-refresh: needed
原因：P11 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未做浏览器交互回归；本轮不改运行时行为，标签关闭链路由类型检查、单测和构建覆盖。

潜在技术债：`delLeftViews` / `delRightViews` 在找不到目标标签时仍沿用既有不 resolve 行为，本轮为避免行为变更未处理。

结论：通过。
