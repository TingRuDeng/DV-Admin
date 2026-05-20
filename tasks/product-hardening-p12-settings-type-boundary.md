# P12 设置面板类型边界收口计划

## 目的

收口设置面板与设置仓库中的 `any` 类型边界，让布局、主题和侧边栏配色设置继续由明确枚举和状态类型约束。

## 适合读者

- 继续推进产品化治理的前端维护者
- 审核布局、主题和侧边栏配色配置链路的 AI 代理

## 一分钟摘要

- 当前 `settings-store.ts` 的通用设置更新通过 `Ref<any>` 写入，绕过了设置项类型约束。
- 当前 `Settings/index.vue` 的侧边栏配色变更参数仍使用 `any`。
- 本轮只收口设置项和侧边栏配色类型，不改变抽屉展示、主题切换、布局切换或本地存储行为。

## ai_summary

```yaml
purpose: "收口 Settings 面板和 settings-store 中的 any 类型边界。"
read_when:
  - "修改 frontend/src/store/modules/settings-store.ts 前"
  - "修改 frontend/src/layouts/components/Settings/index.vue 前"
  - "排查布局、主题或侧边栏配色设置链路时"
source_of_truth:
  - "frontend/src/store/modules/settings-store.ts"
  - "frontend/src/layouts/components/Settings/index.vue"
  - "frontend/src/layouts/components/__tests__/settings-type-governance.spec.ts"
verify_with:
  - "pnpm --dir frontend run test:unit -- settings-type-governance"
  - "pnpm --dir frontend run type-check"
stale_when:
  - "设置项结构、侧边栏配色枚举或设置抽屉交互变化"
```

## 权威边界

本计划只描述 P12 小切片。全局设置结构以 `frontend/src/types/global.d.ts` 和 `frontend/src/settings.ts` 为准；布局枚举以 `frontend/src/enums/settings/layout-enum.ts` 为准；主题与侧边栏配色枚举以 `frontend/src/enums/settings/theme-enum.ts` 为准。

## 如何验证

- 先运行新增守卫测试，确认现有代码会因设置类型边界 `any` 失败。
- 修改实现后重新运行目标测试和前端类型检查。
- 交付前运行前端质量聚合、文档校验、diff 检查和生产构建。

## 执行清单

- [x] 新增设置类型治理测试，并确认当前代码会失败
- [x] 为设置仓库映射和侧边栏配色定义显式类型
- [x] 移除 Settings 面板和 settings-store 中的 `any`
- [x] 运行目标测试、前端类型检查、质量聚合、文档校验、diff 检查和生产构建
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。

Spec 符合度：通过。本轮只收口设置仓库映射和设置面板侧边栏配色事件的类型边界，未改变抽屉展示、主题切换、布局切换或本地存储键。

安全检查：通过。未新增网络端点、鉴权逻辑或密钥；侧边栏配色事件入口对非预期值显式抛错，不做静默降级。

测试与验证：通过。已完成红绿测试、目标类型治理测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建。

复杂度检查：通过。只新增设置映射类型、侧边栏配色类型守卫和一个静态治理测试；未扩大组件职责。

Document-refresh: needed
原因：P12 执行计划和总待办需要记录本轮治理边界、验证命令与完成状态。

剩余风险：未做浏览器交互回归；本轮不改 UI 交互路径，风险主要由类型检查、单测和构建覆盖。

潜在技术债：设置仓库的通用 `updateSetting` 当前没有调用点，后续可在确认无外部依赖后评估是否删除。

结论：通过。
