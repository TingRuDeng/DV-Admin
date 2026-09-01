---
ai_summary:
  purpose: "记录 DV-Admin 前端现代化的已接受架构决策、兼容边界和停止条件。"
  read_when:
    - "规划 Vite、Vue Router 或前端壳层升级时"
    - "评估是否扩大前端重构范围时"
  source_of_truth:
    - "docs/ADR-0001-FRONTEND-MODERNIZATION.md"
    - "docs/ARCHITECTURE.md"
    - "docs/FRONTEND_OPTIMIZATION_BACKLOG.md"
    - "frontend/package.json"
    - "frontend/vite.config.ts"
    - "frontend/src/router/index.ts"
    - "frontend/src/store/modules/permission-store.ts"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/validate_api_contracts.py ."
    - "pnpm --dir frontend run quality"
  stale_when:
    - "前端框架、构建工具或路由主版本发生变化"
    - "动态路由、布局壳层、RouteMeta、KeepAlive 或 Pro 组件边界变化"
    - "实施阶段、停止条件或回滚策略调整"
---

# ADR-0001：前端现代化采用渐进式工具链升级与壳层 PoC

- **状态：** Accepted
- **决策日期：** 2026-09-01
- **实施状态：** 分阶段实施中；阶段状态只在跟踪入口维护
- **跟踪入口：** [FRONTEND_OPTIMIZATION_BACKLOG.md](./FRONTEND_OPTIMIZATION_BACKLOG.md)

## Purpose

确定 DV-Admin 前端现代化的目标架构、实施顺序、兼容边界和停止条件，在保留现有业务能力的前提下验证新工具链与管理后台壳层。

## Source of truth

- `docs/ADR-0001-FRONTEND-MODERNIZATION.md`
- `docs/ARCHITECTURE.md`
- `docs/FRONTEND_OPTIMIZATION_BACKLOG.md`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/src/router/index.ts`
- `frontend/src/store/modules/permission-store.ts`

## Key facts

- 当前实现是 Vue 3、TypeScript、Element Plus、Pinia、Vite 8 和 Vue Router 4；Vite 7 + `rolldown-vite` 与 Vite 8 两个工具链阶段已完成。
- 本 ADR 接受的是演进目标与约束；Vite 8 已落地，但 Vue Router 5 和新壳层尚未实施。
- 现有后端动态菜单、手写路由、RouteMeta、KeepAlive/cacheKey、字典、WebSocket、JWT 刷新和 Pro 组件协议属于业务核心，必须保留。
- `frontend/package.json`、`frontend/pnpm-lock.yaml` 与 `frontend/vite.config.ts` 当前未使用 `unplugin-vue-router`，本次不引入文件路由。
- 具体阶段、状态和验收证据只在 `docs/FRONTEND_OPTIMIZATION_BACKLOG.md` 跟踪，不另建重复 roadmap。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 scripts/validate_api_contracts.py .`
- full: `pnpm --dir frontend run quality`
- full: `pnpm --dir frontend run build`

## Stale when

- Vite、Vue Router、Vue、Element Plus 或 Pinia 主版本变化。
- 动态菜单字段、组件路径、共享 API 契约或路由生成机制变化。
- Layout、Menu、TagsView、AppMain、主题系统或三种布局模式的职责边界变化。
- backlog 阶段、性能预算、停止条件或回滚策略调整。

---

## 背景

当前前端已经具备稳定的 Vue 3 业务层、双后端共享契约、动态路由、三种布局模式、标签页缓存、字典同步、WebSocket 和 Pro 组件体系。主要演进诉求是改善构建工具链、工程组织和管理后台壳层体验，而不是重新定义业务协议。

Vite 8 已稳定发布，并将生产构建、依赖优化和 JavaScript 转换统一到 Rolldown/Oxc 体系。Vite 官方对较复杂项目建议先在 Vite 7 上使用 `rolldown-vite` 隔离打包器差异，再升级 Vite 8。Vue Router 5 是过渡版本；对于未使用 `unplugin-vue-router` 的 Vue Router 4 项目，官方说明无需业务路由改写。

## 已考虑方案

| 方案 | 结论 | 主要取舍 |
|------|------|----------|
| 保留 Vue 3 业务核心，分阶段升级工具链并验证壳层 PoC | **采用** | 变更可隔离、可回滚，能够用现有双后端门禁验证；代价是迁移周期更长 |
| 切换 React/Next | 不采用 | 会重写组件、状态、路由和权限体系，收益不足以覆盖业务回归风险 |
| 切换 Nuxt | 不采用 | 当前是前后端分离管理后台，不需要为 SSR 或全栈约定重塑路由与部署模型 |
| 整体覆盖为 Pure Admin 或 Vben 脚手架 | 不采用 | 会把参考项目的业务假设、目录和权限模型带入现有系统，难以保持双后端契约 |
| 冻结现有工具链和壳层 | 不采用 | 无法验证 Rolldown/Vite 8 的构建收益，也不能解决壳层体验与工程组织的演进诉求 |

## 决策

### 1. 保留业务核心

继续使用 Vue 3、TypeScript、Element Plus 和 Pinia，并保留以下既有能力及其对外语义：

- 后端动态菜单与当前手写路由体系
- RouteMeta、路由权限、KeepAlive、cacheKey 与 TagsView 行为
- left、top、mix 三种布局模式
- JWT 双 token 刷新、Pinia store、字典缓存和 WebSocket/STOMP
- `ProSearch`、`ProTable`、`ProFormDrawer` 等 Pro 组件协议
- Django/FastAPI 共享 API、字段与组件路径契约

不切换 React、Next 或 Nuxt，不整体覆盖现有脚手架。

### 2. 外部项目仅作参考

- [Pure Admin](https://github.com/pure-admin/vue-pure-admin) 仅作为 Element Plus 管理后台壳层 PoC 的布局、菜单、标签页和主题交互参考。
- [Vben Admin](https://github.com/vbenjs/vue-vben-admin) 仅作为工程组织、交互细节和可维护性参考。
- 不复制两者的业务架构、权限模型、路由生成协议或数据访问层，也不把它们声明为项目依赖。

### 3. Vite 按两步迁移

1. 保持 Vite 7 主版本，先切换到 `rolldown-vite`，集中验证 Rolldown 对现有插件和构建配置的兼容性。
2. 第一阶段完全通过后，再在独立 PR 升级 Vite 8，并只迁移当前项目实际命中的废弃配置。

验证范围必须包括自动导入、Element Plus resolver、UnoCSS、Mock、依赖预构建、Terser 和静态资源命名。不得通过删除现有插件换取构建通过。该路径遵循 [Vite 8 公告](https://vite.dev/blog/announcing-vite8) 与 [Vite 7→8 迁移指南](https://vite.dev/guide/migration)。

### 4. Vue Router 5 独立升级

Vue Router 5 在 Vite 8 稳定后单独升级，继续使用后端动态菜单和当前手写路由体系，不引入文件路由。当前仓库未使用 `unplugin-vue-router`，因此按照 [Vue Router 5 迁移指南](https://router.vuejs.org/guide/migration/v4-to-v5)，不规划业务路由重写。

### 5. 壳层 PoC 限定范围

壳层 PoC 只允许改造 Layout、Menu、TagsView、AppMain、主题和页面框架。先验证用户管理、通知公告、个人中心三个代表页，再依据验收结果决定扩大或停止；不得默认进入全量重构。

## 正面后果

- 打包器、Vite 主版本、路由主版本和壳层变化被拆成可定位的独立变量。
- 现有双后端 Playwright smoke、Mock E2E、类型检查和构建门禁可继续作为回归证据。
- 新壳层可以复用成熟项目的交互经验，同时保留 DV-Admin 已治理的业务契约。
- 每个阶段都能通过单一 PR 回滚，不引入数据库迁移或后端发布耦合。

## 负面后果与成本

- 迁移需要多个串行 PR，短期会同时维护当前实现与目标方向的文档认知。
- `rolldown-vite` 和 Vite 8 的插件兼容性必须逐项验证，不能只以构建成功判断完成。
- 壳层 PoC 需要覆盖三种布局、缓存和可访问性，工作量高于直接替换模板。
- Pure Admin 与 Vben 的后续变化不会自动同步到本项目，参考内容必须由本项目验收标准裁决。

## 兼容边界

以下任一变化都不属于本 ADR 已授权的现代化实现范围：

- 修改 Django/FastAPI 菜单字段、前端组件路径或共享 API 契约。
- 重写 JWT 刷新、Pinia store、字典、WebSocket 或 ProTable/ProForm 协议。
- 以文件路由替换当前后端动态菜单和手写路由生成流程。
- 取消 RouteMeta、KeepAlive/cacheKey 或 left/top/mix 三种布局模式。
- 删除现有插件、测试或行为门禁以规避兼容问题。

如确有必要突破这些边界，必须先提出新的架构决策并重新评审，不能在实施 PR 中顺带扩大范围。

## 回滚策略

- 每个阶段使用独立分支和独立 PR；前一阶段完全通过后才能开始下一阶段。
- `rolldown-vite` 阶段失败时恢复 Vite 7 原依赖与锁文件，不夹带 Vite 8 变更。
- Vite 8 阶段失败时回退该阶段依赖和实际配置迁移，保留已验证的 Vite 7 + Rolldown 结论。
- Vue Router 5 阶段失败时只回退路由依赖与该阶段必要调整。
- 壳层或代表页阶段失败时回退对应壳层 PR，业务页面、store、API 和后端不随之重写。
- 任一回滚后重新运行受影响门禁，不能仅凭 Git revert 成功声明恢复。

## 硬停止条件

出现以下任一条件时，当前阶段停止并重新评审，不自动进入下一阶段：

- 需要修改 Django/FastAPI 菜单字段、组件路径或共享 API 契约。
- 需要重写 JWT 刷新、Pinia store、字典、WebSocket 或 ProTable/ProForm 协议。
- 动态路由、RouteMeta、KeepAlive/cacheKey 或三种布局模式出现回归。
- 任一后端真实 Playwright smoke 失败。
- 现有可访问性或性能预算失败。
- 构建时间或总 JavaScript 产物三次运行中位数相对基线回退超过 10%。

## 实施与验收

七个串行阶段、状态、分支/PR 边界和阶段验收项统一记录在 [FRONTEND_OPTIMIZATION_BACKLOG.md](./FRONTEND_OPTIMIZATION_BACKLOG.md)。本 ADR 只定义决策和不可突破的边界，不复制实施状态。
