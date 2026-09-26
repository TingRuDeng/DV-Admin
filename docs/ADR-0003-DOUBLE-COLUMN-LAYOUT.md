---
ai_summary:
  purpose: "记录在 left/top/mix 之外新增双列布局的决策、复用边界、移动端退化规则和兼容约束。"
  read_when:
    - "修改布局模式、LayoutMode 枚举或设置面板的布局选项时"
    - "修改 mix 布局的一级菜单同步逻辑时"
  source_of_truth:
    - "docs/ADR-0003-DOUBLE-COLUMN-LAYOUT.md"
    - "frontend/src/enums/settings/layout-enum.ts"
    - "frontend/src/composables/layout/useLayout.ts"
    - "frontend/src/layouts/index.vue"
    - "frontend/src/layouts/modes/double/index.vue"
    - "frontend/src/layouts/components/Menu/useTopMenuNavigation.ts"
    - "frontend/src/layouts/components/Menu/DoubleRailMenu.vue"
    - "frontend/e2e/shell-layout.spec.ts"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "pnpm --dir frontend run quality"
    - "pnpm --dir frontend exec playwright test e2e/shell-layout.spec.ts --workers=1"
  stale_when:
    - "布局模式的取值、移动端退化规则或一级菜单同步逻辑变化"
    - "双列布局的尺寸、glass 写法或第二列显示条件变化"
---

# ADR-0003：新增双列布局

- **状态：** Accepted
- **决策日期：** 2026-09-26
- **前置决策：** [ADR-0001](./ADR-0001-FRONTEND-MODERNIZATION.md)（保留 left/top/mix，新增布局需要新 ADR）、[ADR-0002](./ADR-0002-LIQUID-CHROME-VISUAL-SYSTEM.md)（视觉与交互约束）

## Purpose

在不改后端菜单字段、组件路径、共享 API 和 Pro 组件协议的前提下，参照 vue-vben-admin 的 sidebar-mixed-nav 新增第四种布局"双列"：左侧一列一级菜单图标，右侧一列当前一级菜单的子菜单。

## Source of truth

- `docs/ADR-0003-DOUBLE-COLUMN-LAYOUT.md`
- `frontend/src/enums/settings/layout-enum.ts`
- `frontend/src/composables/layout/useLayout.ts`
- `frontend/src/layouts/index.vue`
- `frontend/src/layouts/modes/double/index.vue`
- `frontend/src/layouts/components/Menu/useTopMenuNavigation.ts`
- `frontend/src/layouts/components/Menu/DoubleRailMenu.vue`
- `frontend/e2e/shell-layout.spec.ts`

## Key facts

- `LayoutMode` 新增 `double`，left/top/mix 三种布局和它们的行为不变；`AppSettings.layout`、`RouteMeta.layout` 的类型同步扩展，store 字段名和持久化键不变。
- 双列布局在移动端（<992px）直接退化为左侧布局，`useLayout().currentLayout` 与布局根节点 class 都按退化后的值计算，复用左侧布局已验收的抽屉导航。
- 一级菜单的生成、激活同步和"跳到第一个叶子页面"抽成 `useTopMenuNavigation`，mix 顶部菜单和双列图标栏共用；第二列复用 mix 左栏的 `useMixLayoutState`。
- 第二列只在当前一级菜单有两个及以上可见子菜单（或 `alwaysShow`）时显示；顶栏的折叠按钮收起第二列，沿用 `appStore.sidebar.opened` 的语义。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- full: `pnpm --dir frontend run quality`
- full: `pnpm --dir frontend exec playwright test e2e/shell-layout.spec.ts --workers=1`

## Stale when

- 布局取值、移动端退化规则或一级菜单同步逻辑变化。
- 双列布局的尺寸、玻璃写法或第二列显示条件变化。

---

## 背景

对标 vue-vben-admin 时，双列布局是差距最明显、辨识度最高的一项。ADR-0001 把 left/top/mix 列为必须保留的布局，并要求突破布局边界前先有新的决策记录；本 ADR 只新增一个可选布局，不修改、不删除现有三种。

## 决策

- **结构：** 左侧 80px 图标栏（一级菜单图标在上、名称在下），右侧 200px 子菜单列，二者都是悬浮玻璃面板，玻璃画在内层元素的 `::before` 上（ADR-0002 的写法约束）。主内容按"图标栏 + 可见的第二列"留出左边距。
- **交互：** 点击一级菜单切换第二列并跳到它的第一个可访问页面；只有一个可见子菜单的一级菜单直接跳转，不展开第二列；从页签或地址栏进入页面时，一级菜单与第二列自动跟随。只有 hover 变色和既有的宽度过渡，没有新增动效。
- **移动端：** 退化为左侧布局，不单独实现第三套抽屉。
- **复用：** mix 顶部菜单改为使用 `useTopMenuNavigation`，一级菜单现在由 `permissionStore.routes` 响应式计算，并且跳转时跳过隐藏子路由。

## 正面后果

- 用户可以在设置里选择与 vben 同类的双列导航，一级菜单多时切换更快。
- mix 与双列共用一级菜单逻辑，后续修改只有一处。

## 负面后果与成本

- 多一种布局需要随壳层改动一起验证；`shell-layout.spec.ts` 新增了双列用例。
- 双列布局在移动端表现为左侧布局，用户在手机上看到的布局名与设置不同。

## 兼容边界

- 不改后端菜单字段、组件路径、共享 API、Pro 组件协议和 RouteMeta 其他字段。
- 不改变 left/top/mix 的结构和 `useMixLayoutState` 的对外行为。
