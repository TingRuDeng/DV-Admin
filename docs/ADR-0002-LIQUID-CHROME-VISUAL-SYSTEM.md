---
ai_summary:
  purpose: "记录 DV-Admin 前端 Liquid Chrome 视觉系统的已接受决策、否决效果、token 分层与玻璃写法约束。"
  read_when:
    - "修改前端配色、字体、玻璃面板、动效或主题预设色时"
    - "准备给页面加新的视觉效果或新的 backdrop-filter 时"
  source_of_truth:
    - "docs/ADR-0002-LIQUID-CHROME-VISUAL-SYSTEM.md"
    - "frontend/src/styles/README.md"
    - "frontend/src/styles/tokens/_color.scss"
    - "frontend/src/styles/tokens/_glass.scss"
    - "frontend/src/styles/foundation/_glass.scss"
    - "frontend/src/utils/theme.ts"
    - "frontend/src/store/modules/settings-store.ts"
    - "frontend/src/settings.ts"
    - "frontend/src/utils/__tests__/style-governance.test.ts"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "pnpm --dir frontend exec vitest run src/utils/__tests__"
    - "pnpm --dir frontend run quality"
  stale_when:
    - "tokens、玻璃 mixin、虹彩推导或默认预设色变化"
    - "backdrop-filter 允许清单或自定义光标、WebGL 禁令变化"
    - "登录页、首页 hero 或壳层视觉结构重做"
---

# ADR-0002：前端采用 Liquid Chrome 视觉系统

- **状态：** Accepted
- **决策日期：** 2026-09-24
- **前置决策：** [ADR-0001](./ADR-0001-FRONTEND-MODERNIZATION.md)（本 ADR 只换视觉，不突破其兼容边界）

## Purpose

确定 DV-Admin 前端的视觉语言、被否决的效果、token 分层和玻璃材质写法，让后续视觉改动有统一的取舍依据，不再回到"深色画布 + 霓虹珊瑚"或引入高成本特效。

## Source of truth

- `docs/ADR-0002-LIQUID-CHROME-VISUAL-SYSTEM.md`
- `frontend/src/styles/README.md`
- `frontend/src/styles/tokens/_color.scss`、`frontend/src/styles/tokens/_glass.scss`
- `frontend/src/styles/foundation/_glass.scss`
- `frontend/src/utils/theme.ts`（`generateIridescentStops`、`applyIridescence`）
- `frontend/src/store/modules/settings-store.ts`、`frontend/src/settings.ts`
- `frontend/src/utils/__tests__/style-governance.test.ts`

## Key facts

- 视觉语言：深色底 `#06060A`、浅色底 `#EAEAEE`，面板是玻璃加细描边，展示字体为自托管 Geist 极细字重，主按钮、激活导航、徽标和当前页码使用三段虹彩渐变，开关旋钮和无图头像是金属球。深色和浅色两种模式都保留。
- 预设色驱动虹彩：设置面板和 store 字段不变，默认预设为 `#6E36D6`；`--ff-iri-a/b/c` 与 `--ff-on-iri` 由 `generateIridescentStops` 按预设色的 OKLCH 色相在运行时推导。
- 旧默认色 `#FF705C` 只在 `vea:ui:theme_color_migration` 未标记时迁移一次；之后用户主动选回珊瑚色不受影响。
- 玻璃模糊只允许出现在 `foundation/_glass.scss` 的 `ff-glass` mixin 和 `skins/_popper.scss`，由 style-governance 测试强制。
- 全站使用系统光标，`src` 下不允许 `cursor: url(` 和 WebGL canvas，同样由 style-governance 测试强制。
- 交互只有 hover 变色和进场动画；弹簧缓动 `--ff-ease-spring` 只用于开关。`prefers-reduced-motion` 下关闭进场、路由过渡和数值渐变。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `pnpm --dir frontend exec vitest run src/utils/__tests__`
- full: `pnpm --dir frontend run quality`
- full: `pnpm --dir frontend run test:e2e:smoke`

## Stale when

- tokens、玻璃 mixin、虹彩推导参数或默认预设色变化。
- style-governance 的 backdrop-filter 允许清单、光标或 WebGL 禁令调整。
- 登录页、首页 hero 或壳层的视觉结构被重新设计。
- 新 ADR 取代本视觉系统。

---

## 背景

原视觉是"深色画布 + 霓虹珊瑚"，产品方希望对标 Awwwards / FWA / CSS Design Awards 的视觉品质，并且不接受描述性的装饰文字。三个 HTML 原型（Acid Ink、Editorial Klein、Liquid Chrome）并排对比后，选定 Liquid Chrome。

改造受 ADR-0001 的兼容边界约束：不改后端菜单字段、组件路径、共享 API、store 协议，也不改 ProSearch / ProTable / ProFormDrawer 协议；页面模板只在登录页和首页 hero 调整，其他页面通过全局 skin 换装。

## 决策

### 1. 保留与否决的效果

| 效果 | 结论 | 原因 |
|------|------|------|
| 玻璃面板、虹彩主色、极细展示字、金属球控件 | 采用 | 原型的核心识别度，成本可控 |
| 静态虹彩光池（`body::before` 上的 radial-gradient） | 采用 | 给玻璃提供可折射的底色，不动画、不用 JS |
| 进场动画、路由淡入、hover 变色 | 采用 | 纯 CSS，可被 reduced-motion 关闭 |
| WebGL / canvas 液态金属背景、银色金属团 | 否决 | 持续占用 GPU，与管理后台的长时间使用场景不符 |
| 自定义光标、指针液滴、点击飞溅 | 否决 | 影响可用性与可访问性，全站保持系统光标 |
| 磁吸按钮、卡片倾斜、跟随指针高光、字母抬起 | 否决 | 管理后台以效率为先，这类效果会干扰点击目标 |
| 果冻形变的弹窗和抽屉 | 否决 | 弹层只做滑入加淡入 |

### 2. token 分层

沿用 `tokens -> theme -> foundation -> skins -> pages`，并沿用 `--ff-*` 命名：

- `tokens/_color.scss`：画布、正文四级（primary / regular / secondary / dim）、线条、hover / press、`--ff-iri*` 兜底值和 `--ff-orb` 金属球。旧的 `--ff-accent*`、`--ff-shell-*` 名称保留并改为引用新值，避免全仓改名。
- `tokens/_glass.scss`：`--ff-glass`、`--ff-glass-strong`、`--ff-glass-tint`、`--ff-glass-edge`、`--ff-glass-hi`、`--ff-glass-fx(-thick)`、`--ff-glass-fallback` 和光池色 `--ff-glow-*`，深浅两组值。
- `tokens/_typography.scss`：Geist 与 Geist Mono 的 Latin 子集 woff2 放在 `src/assets/fonts/` 并附 OFL 许可；中文回落到系统字体。
- `tokens/_motion.scss`：`--ff-ease-out`、`--ff-ease-standard`、`--ff-ease-spring` 和三档时长。
- `theme/_element-plus.scss`：`:root` 与 `html.dark` 各写一份 Element Plus 变量桥接，覆盖 EP 自带的 dark css-vars。
- `variables.scss` 只放 Sass 变量（它会被注入到所有 SCSS），不写会产生 CSS 输出的规则。

### 3. 预设色推导规则

`generateIridescentStops(primary, theme)` 以预设色的 OKLCH 色相 h 为中心取三个色标：

- 深色模式：色相偏移 −32° / +10° / +115°，高明度低彩度的粉彩，`--ff-on-iri` 为 `#0b0b10`。
- 浅色模式：色相偏移 −25° / 0° / +105°，中明度高彩度的饱和色，`--ff-on-iri` 为白色。
- 超出 sRGB 色域时保持明度和色相、二分降彩度；与 on-iri 文字对比度低于 4.5:1 时按 0.01 步长调整明度直到达标。
- settings-store 在已有的 `watch([theme, themeColor])` 里紧跟 `applyTheme` 调用 `applyIridescence`，store 字段和 action 不变。
- "经典蓝"侧栏在 `html.sidebar-color-blue` 下改为蓝调玻璃加白字，仍只在浅色模式出现。

### 4. 玻璃写法约束

- 统一用 `@include ff-glass($variant, $position, $inset)`。模糊画在 `::before` 上，宿主设 `isolation: isolate`。原因是 `backdrop-filter`、`filter`、`transform` 放在宿主上会让它成为 `position: fixed` 后代的包含块（mix 布局移动端侧栏会被带偏）。
- 壳层宿主（侧栏、顶栏、面板）不加 `filter` 或 `transform`；进场动画用 `backwards` 填充，结束后不残留 transform。动画进行中玻璃模糊暂时缺席是可接受的代价。
- 表格固定列、粘性表头、tags 栏、`.el-menu--popup` 保留元素自身的近不透明底色，防止滚动内容透出。
- 使用 mixin 的文件必须显式 `@use "../foundation/glass" as *;`，因为样式测试用的 `sass.compile` 不带 additionalData。
- 不新增 `.glass-panel` 类名。
- 渐变文字用 `color: transparent` 加 `background-clip: text`，不用 `-webkit-text-fill-color`：`_minimal-saas.scss` 的深色兜底会把 `.ff-page-shell` 内的 text-fill 强制回填为 `currentColor`。

### 5. 性能边界

- 同屏常驻的 backdrop-filter 只有侧栏、顶栏和页面面板这几层，外加按需出现的弹层；首页快捷入口这类重复方块只用半透明底，不逐个模糊。
- 光池是静态渐变，不动画、不跟随指针；页面不引入 canvas、WebGL 或新的运行时动画依赖，`animate.css` 已移除。
- 构建总 JS 与构建时间的三次中位数不得比改造前回退超过 10%，沿用 ADR-0001 的硬停止条件。

## 正面后果

- 视觉由少量 token 和一个 mixin 驱动，换预设色时整套虹彩自动协调且保证对比度。
- 高风险写法（宿主 backdrop-filter、自定义光标、WebGL）被测试拦截，不会随页面改动回流。
- 业务页面零模板改动即可换装，ADR-0001 的协议边界保持不变。

## 负面后果与成本

- 玻璃依赖 `backdrop-filter`，不支持的浏览器回落为不透明 tint，观感较平。
- 进场动画进行中玻璃模糊暂时缺席。
- 旧的 `--ff-accent*`、`--ff-shell-*` 名称继续作为别名存在，三套 token 的收敛仍记录在 [TECH_DEBT.md](./TECH_DEBT.md)。
- 注册与重置密码表单在当前路由下不可达，保持原样未重做。

## 兼容边界

以下变化不属于本 ADR 授权的范围，需要新的决策：

- 修改后端菜单字段、组件路径、共享 API、store 字段或 Pro 组件协议。
- 在 mixin 和 popper skin 以外新增 `backdrop-filter`，或引入 canvas / WebGL / 自定义光标。
- 为视觉效果逐页批量改写业务页模板。
