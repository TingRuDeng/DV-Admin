---
ai_summary:
  purpose: "跟踪当前仍有效的前端优化事项和已完成治理基线。"
  read_when:
    - "规划前端治理或重构范围时"
    - "判断旧前端优化方案是否仍有效时"
  source_of_truth:
    - "docs/ADR-0001-FRONTEND-MODERNIZATION.md"
    - "docs/ARCHITECTURE.md"
    - "frontend/src/styles"
    - "frontend/src/components"
    - "frontend/src/views"
    - "frontend/src/router/index.ts"
    - "frontend/src/store/modules/tags-view-store.ts"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "pnpm --dir frontend run quality"
    - "pnpm --dir frontend run build"
  stale_when:
    - "前端治理基线变化"
    - "系统页面迁移状态、Pro 组件边界或缓存策略变化"
    - "ADR-0001 的实施阶段、停止条件或验收预算变化"
---

# DV-Admin 前端优化待办

> 本文档是当前仍有效的前端治理 backlog，不替代架构事实。

## Purpose

记录当前仍有效的前端后续优化事项，并明确旧方案中已经失效的部分。

## Source of truth

- `docs/ADR-0001-FRONTEND-MODERNIZATION.md`
- `docs/ARCHITECTURE.md`
- `frontend/src/styles`
- `frontend/src/components`
- `frontend/src/views`
- `frontend/src/router/index.ts`
- `frontend/src/store/modules/tags-view-store.ts`

## Key facts

- 本文档是跟踪入口，不是架构权威。
- 旧前端优化方案已被本文档和 `docs/ARCHITECTURE.md` 吸收；旧执行计划不再保留为现行参考。
- 已完成治理基线不应重复规划为新增项。
- 本文档是 ADR-0001 实施阶段、状态和验收证据的唯一跟踪入口，不另建重复 roadmap。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- full: `pnpm --dir frontend run quality`
- full: `pnpm --dir frontend run build`

## Stale when

- 前端样式治理、Pro 组件、RouteMeta 或 KeepAlive 策略变化。
- 旧 backlog 条目完成或失效。
- ADR-0001 的阶段顺序、验收标准、性能预算或停止条件变化。

---

## 文档定位

- 本文档是当前前端优化 backlog 的跟踪入口
- 旧前端优化方案不再作为现行实施依据；仍有效的事实已合并到当前权威文档和本 backlog
- 当前现状、既有规范与已落地能力，仍以 `docs/ARCHITECTURE.md`、`frontend/src/styles/README.md` 及实际代码为准
- 前端现代化决策以 `docs/ADR-0001-FRONTEND-MODERNIZATION.md` 为准；本文件只维护阶段状态、验收证据和继续/停止结论

---

## ADR-0001 前端现代化实施路线

> 当前状态：架构决策已接受并进入串行实施。以下七个阶段必须使用独立分支和独立 PR；前一阶段完成全部验收并合并后，才能开始下一阶段。

| 阶段 | 状态 | 独立交付目标 |
|------|------|--------------|
| 1. 建立基线 | 已完成（2026-09-01） | 固化构建、产物、性能 smoke 和关键页面行为基线 |
| 2. Vite 7 + `rolldown-vite` | 已完成（2026-09-01） | 只隔离验证 Rolldown 与现有插件、配置的兼容性 |
| 3. 升级 Vite 8 | 已完成（2026-09-01） | 迁移当前项目实际命中的废弃配置，保持插件能力 |
| 4. 升级 Vue Router 5 | 未开始 | 保持动态菜单与手写路由体系，不引入文件路由 |
| 5. 壳层 PoC | 未开始 | 只改造 Layout、Menu、TagsView、AppMain、主题和页面框架 |
| 6. 代表页验证 | 未开始 | 验证用户管理、通知公告、个人中心三个代表页 |
| 7. 扩大或停止评审 | 未开始 | 依据完整验收证据决定扩大壳层迁移或停止 |

### 阶段 1：建立可比较基线

**范围**

- 在同一台机器、同一 Node/pnpm 版本和干净依赖状态下连续运行三次生产构建。
- 记录生产构建时间三次运行的中位数、`dist/js` 总大小及其三次运行中位数。
- 记录现有性能 smoke、可访问性 smoke 和双后端真实 Playwright smoke 结果。
- 固化登录、动态菜单、left/top/mix 布局、TagsView、KeepAlive/cacheKey、用户管理、通知公告和个人中心的行为基线。

**完成标准**

- PR 描述包含机器与工具链版本、三次原始测量值、中位数和产物统计口径。
- 所有现行门禁通过；未修改依赖、构建配置或业务实现。
- 本节状态和基线摘要随该阶段 PR 更新。

**基线记录（2026-09-01）**

- 基准提交：`94df8e8826eecaad2f28f5df53e25bb1de98f544`；环境为 macOS 15.7.7 arm64、Node 24.20.0、pnpm 11.21.0，`pnpm install --frozen-lockfile` 确认依赖已是锁文件对应状态。
- 构建时间口径：在同一工作区串行执行三次 `/usr/bin/time -p pnpm run build`，记录命令端到端 `real` 时间，包含 `vue-tsc --noEmit` 与 Vite 生产构建。三次结果为 17.56s、17.53s、17.39s，中位数为 **17.53s**。
- JavaScript 产物口径：每次构建结束后汇总 `dist/js/**/*.js` 的未压缩文件字节数。三次结果均为 2,704,559 bytes（215 个文件，约 2.58 MiB），中位数为 **2,704,559 bytes**。
- 前端质量基线：`pnpm run quality` 通过；其中 Vitest 为 94 个测试文件、276 项测试全部通过。`pnpm run audit:prod` 通过，生产依赖审计为 critical 0、high 0、moderate 1、low 0。
- 浏览器基线：Mock Playwright smoke 14/14 通过；其中性能 smoke 满足登录页加载少于 8,000ms、关键资源数少于 180 的现有预算，可访问性 smoke 验证登录页标题、`main` landmark、可命名账号/密码控件和登录按钮。
- 双后端基线：Django 真实浏览器 smoke 1/1 通过（9.86s），FastAPI 真实浏览器 smoke 1/1 通过（10.82s）；共享流程覆盖登录、个人资料更新、头像上传、通知详情和已读状态。
- 关键行为基线：登录、动态菜单、用户管理和通知公告由 Mock E2E 覆盖；动态路由规范化另由 `permission-store` 单元测试覆盖；left/top/mix 三种布局、AppMain 与 TagsView 使用一次性 Playwright 探针验证真实渲染（1/1 通过，探针未进入提交）；mix 菜单状态、TagsView 增删、KeepAlive/cacheKey 由现有单元测试覆盖；个人中心由两套真实后端 smoke 覆盖。
- 本阶段只更新本 backlog 的状态和验收证据，未修改依赖、构建配置、业务实现或 API 契约；未触发硬停止条件。阶段 2 尚未开始。

### 阶段 2：在 Vite 7 上验证 `rolldown-vite`

**范围**

- 保持 Vite 7 语义，只将 Vite 实现切换为 `rolldown-vite`。
- 逐项验证自动导入、Element Plus resolver、UnoCSS、Mock、依赖预构建、Terser 和静态资源命名。
- 对比阶段 1 的构建时间、总 JavaScript 产物和关键页面行为。

**完成标准**

- 不删除或禁用现有插件来换取构建通过。
- 类型检查、单元测试、构建、Mock E2E、可访问性/性能 smoke 和两套真实后端 Playwright smoke 全部通过。
- 记录 Rolldown 兼容问题、必要配置调整和回滚证据。

**阶段记录（2026-09-01）**

- 基准与环境：从阶段 1 合并提交 `5eef322a23c17e5c2061e721d9ca0b86354fa3d9` 创建独立分支；继续使用 macOS 15.7.7 arm64、Node 24.20.0 和 pnpm 11.21.0，`pnpm install --frozen-lockfile` 通过。
- 依赖切换：将顶层 Vite 精确锁定为 `npm:rolldown-vite@7.1.9`，与阶段 1 的 Vite 7.1.9 版本语义一致，避免在验证打包器时夹带 Vite 小版本升级；未删除、禁用或替换其他插件。
- 必要兼容调整：Rolldown 的 `PreRenderedAsset` 通过 `names` 提供资源名，原配置只读取 `name`，首次构建在 CSS 资源命名阶段失败；`assetFileNames` 现按 `names[0] -> name -> 空值` 兼容读取，并为无名资源保留 `assets` 兜底目录。该调整兼容原 Rollup 形态，不改变业务静态资源路径协议。
- 插件与构建验证：类型检查和生产构建证明自动导入、Vue 插件与 Element Plus resolver 可用；构建产物包含 Element Plus 与 UnoCSS 规则；Mock Playwright 14/14 通过并证明 Mock 插件可用；开发预构建生成 99 个 optimized 依赖和 29 个共享 chunk；Terser 输出未发现直接 `console.log/warn/error/info` 调用或 `debugger;`；产物仍按 `js/css/img/fonts` 目录和哈希文件名输出，`mockServiceWorker.js` 继续按 public 文件原样复制。
- 兼容观察：Rolldown 内置的 Lightning CSS 会对全局 Sass 中 15 个既有 `:deep()` 选择器发出告警；直接编译现有 Sass 也会保留同样 15 个选择器，因此这不是本阶段新增的选择器变化。现有页面、布局、可访问性、性能和双后端 smoke 均通过，本阶段不夹带无关样式重构。
- 构建对比：与阶段 1 相同口径串行运行三次 `/usr/bin/time -p pnpm run build`，结果为 13.29s、12.63s、13.13s，中位数为 **13.13s**，相对 17.53s 基线改善约 **25.1%**。
- JavaScript 产物：三次均为 2,732,296 bytes（223 个文件，约 2.61 MiB），中位数为 **2,732,296 bytes**；相对阶段 1 增加 27,737 bytes，约 **1.03%**，未触发 10% 停止条件。
- 行为与门禁：`pnpm run quality` 通过（94 个测试文件、276 项测试）；生产依赖审计 critical/high 均为 0；Mock smoke 14/14、left/top/mix + AppMain + TagsView 一次性浏览器探针 1/1、Django 真实 smoke 1/1、FastAPI 真实 smoke 1/1 均通过。动态路由、RouteMeta、KeepAlive/cacheKey 和三种布局未发现回归。
- 回滚证据：本阶段只修改 Vite 别名、锁文件、资源命名兼容配置和权威文档；完整回退该阶段提交即可恢复阶段 1 的 Vite 7/Rollup 状态，不涉及 Django/FastAPI、共享 API、菜单字段、组件路径、JWT、Pinia、字典、WebSocket 或 Pro 组件协议。
- 结论：未触发 ADR-0001 硬停止条件；阶段 2 验收通过。阶段 3 仍须在本 PR 合并后从最新 `master` 创建独立分支，不自动夹带到本阶段。

### 阶段 3：独立升级 Vite 8

**范围**

- 从已通过的 Vite 7 + Rolldown 基线升级 Vite 8。
- 只迁移当前配置实际命中的废弃项，并验证 Rolldown/Oxc、依赖优化、Terser 和 CSS/静态资源输出。
- 继续保留自动导入、Element Plus resolver、UnoCSS、Mock 和现有插件能力。

**完成标准**

- 不以删除现有插件或缩减测试范围作为迁移手段。
- 完成阶段 2 的全部门禁和阶段 1 的性能/产物对比。
- 文档中的“当前技术栈”只有在该 PR 合并后才更新为 Vite 8。

**阶段记录（2026-09-01）**

- 基准与环境：阶段 3 最终基于 `master` 提交 `9c2e111e3b23585f074772fb335ba16f62a48100`，继续使用 macOS 15.7.7 arm64、Node 24.20.0 和 pnpm 11.21.0；`pnpm install --frozen-lockfile` 通过。
- 依赖升级：顶层 Vite 从 `npm:rolldown-vite@7.1.9` 升级并精确锁定为 Vite 8.2.2；同步升级 `@vitejs/plugin-vue` 6.0.8、UnoCSS 66.8.1，并将直接使用的 `@iconify/utils` 对齐到 UnoCSS 图标预设依赖的 3.1.4。未删除、禁用或替换现有插件。
- 必要配置迁移：将 Vite 8 已废弃的 `build.rollupOptions` 改为 `build.rolldownOptions`，保留阶段 2 已验证的 `assetFileNames` 兼容读取、Terser 压缩和静态资源目录/哈希命名语义；没有通过移除配置或插件换取构建通过。
- 插件与构建验证：类型检查和生产构建证明 Vue 自动导入、Element Plus resolver、UnoCSS 与现有插件可用；Mock Playwright 14/14 通过；开发预构建生成 99 个 optimized 依赖和 10 个共享 chunk；生产产物为 212 个 JS、57 个 CSS、3 个图片和 1 个字体文件，`mockServiceWorker.js` 继续原样复制；Terser 输出未发现直接 `console.log/warn/error/info` 调用或 `debugger;`。
- 兼容观察：阶段 2 记录的 15 个全局 Sass `:deep()` Lightning CSS 告警仍存在，未出现新的选择器变化。Vite 8 还提示未来 `configLoader: native` 默认值将不支持 `__dirname` 和无 import attributes 的 JSON 导入；当前默认配置加载器、开发服务器和生产构建均通过，该未来主版本迁移提示不在本阶段“只迁移实际废弃项”的范围内。Vitest 4.0.18 的 mocker peer 尚未声明 Vite 8，因此测试链隔离保留传递 Vite 7.1.9；本阶段不夹带 Vitest/MSW 测试工具链迁移，顶层应用开发与生产构建链仍为 Vite 8，现有 276 项单元测试全部通过。
- 构建对比：按阶段 1 相同口径串行运行三次 `/usr/bin/time -p pnpm run build`，结果为 12.31s、12.16s、12.05s，中位数为 **12.16s**；相对阶段 1 的 17.53s 改善约 **30.63%**，相对阶段 2 的 13.13s 改善约 **7.39%**。
- JavaScript 产物：三次均为 2,686,958 bytes（212 个文件，约 2.56 MiB），中位数为 **2,686,958 bytes**；相对阶段 1 减少 17,601 bytes（约 **0.65%**），相对阶段 2 减少 45,338 bytes（约 **1.66%**），未触发 10% 停止条件。
- 行为与门禁：`pnpm run quality` 通过（94 个测试文件、276 项测试）；生产依赖审计 critical/high 均为 0；Mock smoke 14/14、left/top/mix + AppMain + TagsView 一次性浏览器探针 1/1、Django 真实 smoke 1/1、FastAPI 真实 smoke 1/1 均通过。Django smoke 的并发测试库问题已在独立前置 PR 修复并由两套 Vite 基线复现确认，不属于 Vite 8 回归。
- 回滚证据：完整回退本阶段对 Vite、Vue 插件、UnoCSS/Iconify、锁文件、`rolldownOptions` 和权威文档的改动，即可恢复阶段 2 的 Vite 7 + Rolldown 状态；不涉及 Django/FastAPI、共享 API、菜单字段、组件路径、JWT、Pinia、字典、WebSocket 或 Pro 组件协议。
- 结论：未触发 ADR-0001 硬停止条件；阶段 3 验收通过。阶段 4 仍须在本 PR 合并后从最新 `master` 创建独立分支，不自动夹带到本阶段。

### 阶段 4：独立升级 Vue Router 5

**范围**

- 只升级 Vue Router 5，不引入文件路由或 `unplugin-vue-router`。
- 保留后端动态菜单、当前手写静态路由、RouteMeta 清洗、权限守卫、KeepAlive/cacheKey 和 TagsView 语义。

**完成标准**

- 动态路由注入、刷新恢复、403 准入、activeMenu、面包屑和缓存行为无回归。
- left/top/mix 三种布局和两套真实后端 Playwright smoke 通过。
- 文档中的“当前技术栈”只有在该 PR 合并后才更新为 Vue Router 5。

### 阶段 5：制作 Pure Admin 风格壳层 PoC

**范围**

- 仅改造 Layout、Menu、TagsView、AppMain、主题和页面框架。
- Pure Admin 只作为 Element Plus 壳层交互参考；Vben 只作为工程组织和交互参考。
- 不修改业务 API、store、动态路由协议、Pro 组件协议或后端实现。

**完成标准**

- left/top/mix 三种布局、移动端断点、主题切换、标签页和缓存行为均通过现有测试与人工验收。
- 现有可访问性与性能预算通过，构建/产物未触发 10% 停止条件。
- PoC 可由单一 PR 完整回滚，不遗留新旧壳层混合协议。

### 阶段 6：验证三个代表页

**代表页**

- 用户管理：验证 ProTable、筛选、分页、抽屉表单和权限按钮。
- 通知公告：验证列表、详情、状态、富文本和动态菜单入口。
- 个人中心：验证资料、头像、密码、静态资源 URL 和响应式页面框架。

**完成标准**

- 三页在 Django 与 FastAPI 下的共享行为一致。
- 两套真实后端 Playwright smoke、相关 Mock E2E、单元测试、可访问性和性能 smoke 全部通过。
- 只适配页面框架和壳层接缝，不重写 ProTable/ProForm 或数据协议。

### 阶段 7：扩大或停止评审

**决策输入**

- 阶段 1-6 的测试、构建、性能、产物、可访问性和人工验收证据。
- 三个代表页的改造成本、复用程度、回归数量和回滚复杂度。
- 所有硬停止条件是否曾触发，以及触发后的处置结论。

**输出**

- 仅允许形成“按明确页面批次扩大壳层迁移”或“停止并保留现状”之一。
- 扩大迁移必须另行给出页面批次和验收范围，不得把本阶段视为全量重构的默认授权。

### 全阶段硬停止条件

出现以下任一情况时，停止当前阶段并重新评审，不自动进入下一阶段：

- 需要修改 Django/FastAPI 菜单字段、组件路径或共享 API 契约。
- 需要重写 JWT 刷新、Pinia store、字典、WebSocket 或 ProTable/ProForm 协议。
- 动态路由、RouteMeta、KeepAlive/cacheKey 或三种布局模式出现回归。
- 任一后端真实 Playwright smoke 失败。
- 现有可访问性或性能预算失败。
- 构建时间或总 JavaScript 产物三次运行中位数相对阶段 1 基线回退超过 10%。

---

## 已完成基线

以下能力已在仓库中落地，不应再重复作为“新增项”规划：

- 页面样式治理已切换为 `tokens -> theme -> foundation -> skins -> pages`
- 路由页已优先组合 `PageShell`、`FilterPanel`、`DataPanel`
- `frontend/src/plugins/permission.ts` 已承担登录鉴权、拉取用户信息、动态路由注入与异常兜底
- 菜单高亮已支持 `meta.activeMenu`
- 系统管理域已有多页完成新页面骨架迁移
- `components/CURD` 已提供一批可复用雏形组件，但尚未演进为统一 Pro 层
- 页面层弹层已完成抽象收敛：`frontend/src/views` 不再直接使用 `el-dialog` / `el-drawer`
- `tags-view-store`、`TableSelect`、WebSocket STOMP manager 和主题样式测试已完成 P1-P4 收口
- `components/CURD` 兼容层已完成复核：兼容层外无业务调用点，旧全局组件声明已移除，新增调用由测试守卫阻断
- 近期前端大文件治理已继续收口：`FileUpload.vue`、`NavbarActions.vue` 和 TagsView 缓存 store 的纯逻辑已拆入 helper，并补充对应单元测试

---

## 2026-06-27 前端治理收口摘要

- `frontend/src/components/Upload/FileUpload.vue` 已把文件展示映射、上传批次完成判断、成功响应收集、失败文件清理和删除路径解析抽入 `fileUploadHelpers.ts`。
- `frontend/src/layouts/components/NavBar/components/NavbarActions.vue` 已把导航栏右侧动作区主题文字 class 判定抽入 `navbarActionsHelpers.ts`。
- `frontend/src/store/modules/tags-view-store.ts` 已把缓存新增、删除、保留、更新迁移和快照构造抽入 `tags-view-cache-helpers.ts`。
- 上述治理均保留原组件对外行为，仅新增纯逻辑测试覆盖核心分支；相关组件和 store 均低于 300 行。
- 单文件 300 行保留为风险提示，不再作为独立拆分目标；后续优先处理契约缺口、能力漂移、安全配置、死代码、文档事实冲突和测试盲区。
- 9-25 行兼容 shim 或再导出入口暂作为观察项保留；除非出现明确退场窗口，不再继续为了行数拆分。

## 2026-05-23 前端治理收口摘要

- `frontend/src/store/modules/tags-view-store.ts` 已修复关闭左右标签时目标不存在导致 Promise 不 resolve 的边界，并用 store 单测覆盖。
- `frontend/src/components/TableSelect/` 已拆出类型、搜索表单、数据表和底部动作组件，并补充类型治理和黑盒行为测试。
- `frontend/src/composables/websocket/stomp-connection-manager.ts` 已拆出纯逻辑 helper、类型、client factory 和订阅注册表，连接管理行为由 fake client 单测覆盖。
- 原 `theme-styles` 大测试已按职责拆分为暗色工具、表单 chrome、弹层样式和共享测试工具。
- `components/CURD` 暂作为历史兼容层冻结保留；新页面和重构页面继续使用 `ProSearch` / `ProTable` / `ProFormDrawer`。

---

## 当前优先级

### P0: RouteMeta 规范化

**目标**

建立统一的前端路由元信息契约，避免静态路由、动态路由、菜单高亮、面包屑、缓存和权限语义分散。

**待办**

- [x] 在前端补充统一的 `RouteMeta` 类型定义
- [x] 为动态路由转换增加 `normalizeMeta`，统一清洗后端返回的 `meta`
- [x] 对齐静态路由与动态路由的字段语义，避免两套约定并存
- [x] 明确 `activeMenu` 的使用规则，优先覆盖详情页、隐藏页、编辑页
- [x] 明确 `perms` / `roles` 在前端的职责边界
- [x] 将后端菜单字段到前端 meta 的映射规则写入文档

**涉及代码**

- `frontend/src/router/index.ts`
- `frontend/src/store/modules/permission-store.ts`
- `frontend/src/layouts/components/Menu/BasicMenu.vue`
- `frontend/src/components/Breadcrumb/index.vue`
- `frontend/src/layouts/components/TagsView/index.vue`

**完成标准**

- 静态路由和动态路由都遵守同一套 meta 字段定义
- `activeMenu`、`breadcrumb`、`keepAlive`、`affix`、`layout` 等字段含义明确
- 后端返回字段缺失时，前端有稳定默认值

---

### P1: KeepAlive / cacheKey 契约统一

**目标**

将当前基于 `fullPath` 的缓存策略收敛为可控的稳定 key，避免 query、分页或筛选条件导致缓存实例膨胀。

**待办**

- [x] 为路由引入统一 `cacheKey` 约定
- [x] 将 `AppMain` 的缓存组件命名逻辑从 `fullPath` 调整为优先 `meta.cacheKey`，其次 `route.name`
- [x] 将 `tags-view-store` 的 `cachedViews` 从 `fullPath` 迁移为稳定缓存 key
- [x] 为“列表页默认缓存、详情页默认不缓存”建立统一约定
- [x] 为少数确实依赖 query 维度缓存的页面保留显式例外策略
- [x] 梳理刷新、关闭左右、关闭其他、重定向刷新在新策略下的行为

**涉及代码**

- `frontend/src/layouts/components/AppMain/index.vue`
- `frontend/src/store/modules/tags-view-store.ts`
- `frontend/src/layouts/components/TagsView/index.vue`
- `frontend/src/router/index.ts`

**完成标准**

- 常见列表页不会因为 query 变化创建多份缓存实例
- 详情页、编辑页和多步骤页的缓存行为可预测
- 刷新标签页与关闭标签页行为和缓存 key 策略一致

---

### P2: ProTable / ProForm 抽象

**目标**

在不推翻现有页面骨架的前提下，从系统管理页中提炼统一的 Pro 级列表和表单能力，减少重复的查询、分页、弹窗和提交逻辑。

**待办**

- [x] 评估现有 `components/CURD` 是否作为演进基础，或仅保留兼容层
- [x] 定义 `ProSearch` / `ProTable` / `ProFormDrawer` / `ProFormModal` 的最小职责边界
- [x] 先做最小可用版本，不一次性引入过多高级能力
- [x] 以 `system/user` 作为样板页完成第一轮抽象
- [x] 再迁移 `system/role`、`system/menu`、`system/dict`

**评估结论（2026-04）**

- `components/CURD` 继续作为历史页面兼容层保留，不作为新一轮 Pro 抽象基座
- 新增或重构页面统一使用 `ProSearch` / `ProTable` / `ProFormDrawer`，不再新增 `CURD` 调用点

**复核结论（2026-05-23）**

- 兼容层外已无业务调用点，系统管理页已迁移到 Pro 组件体系
- `components/CURD` 暂继续保留为历史兼容层，避免一次性删除旧抽象带来不可见回归
- `src/types/components.d.ts` 已移除 CURD 全局组件声明，避免 IDE 和模板类型继续暗示可直接使用 `<CURD>` / `<PageContent>` / `<PageSearch>` / `<PageModal>`
- 后续只有出现真实调用点、迁移遗漏或明确退场窗口时，才继续拆分或删除 `frontend/src/components/CURD/`

**收口结果（2026-04-14）**

- 系统管理域列表页已统一为 `ProTable(request)` 驱动
- 页面层表单弹层统一为 `ProFormDrawer`
- 页面层详情/非表单弹层统一为 `ProDialog` / `ProDrawer`
- 已新增测试守卫，禁止在 `src/views` 回归到原生 `el-dialog` / `el-drawer`
- 已新增测试守卫，禁止在 `src/views` 回归到 `components/CURD` 页面组件，并约束视图层 `ProTable` 保持 `request` 驱动
- 公共组件与 `CURD` 兼容层弹层均已收口到 `ProDialog` / `ProDrawer`，原生弹层仅保留在 Pro 包装层内部实现
- 已新增全局守卫，约束 `src/**/*.vue` 的原生弹层仅可出现在 `ProDialog` / `ProDrawer` / `ProFormDrawer` 内部
- 已在构建层、Lint 层与测试层同时约束：`CURD` 目录不参与组件自动注册，且禁止在兼容层外新增 `components/CURD` 引用

**建议的 MVP 范围**

- `ProSearch`
  - 查询项配置
  - 重置
  - 回车搜索
  - 折叠高级筛选
- `ProTable`
  - 统一工具栏
  - 请求驱动分页
  - 加载态 / 空态
  - 批量操作区
  - 列显隐和刷新
- `ProFormDrawer` / `ProFormModal`
  - 标题区
  - 加载态 / 提交态
  - 表单回填
  - 关闭重置
  - 提交生命周期封装

**涉及代码**

- `frontend/src/components/CURD/`
- `frontend/src/views/system/user/index.vue`
- `frontend/src/views/system/role/index.vue`
- `frontend/src/views/system/menu/index.vue`
- `frontend/src/views/system/dict/index.vue`

**完成标准**

- 新页面不再重复手写查询、分页和弹窗表单的通用流程
- `system/user` 至少完成一轮可复用抽象验证
- 老页面可渐进迁移，不要求一次性全量替换

---

## 建议实施顺序

1. 先完成 `RouteMeta` 规范化，统一基础契约
2. 再完成 `KeepAlive / cacheKey` 改造，稳定标签页与缓存行为
3. 最后在稳定路由与缓存契约上推进 `ProTable / ProForm` 抽象

---

## 明确不再继续推进的旧方案项

以下内容已被后续实现吸收，或不再作为当前阶段的直接待办：

- “新增 `PageWrapper` 作为统一页面容器”
- “补一个 `router/guard.ts` 才有全局守卫”
- “建立样式分层结构作为未来方案”
- “把用户页作为第一张页面样板再决定是否迁移”

这些判断对应的底层目标并非全部失效，但其原始表述已与当前仓库现状不一致。
