# DV-Admin 沉浸式首屏与壳层视觉重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with verification checkpoints.

**Goal:** 在不改变后端 API 和业务数据流的前提下，将登录页、登录后壳层与首页仪表盘统一为暗色画布 + 荧光珊瑚色视觉，并把这些范围内的图标收敛到 Lucide。

**Architecture:** 新增 `AppIcon` 作为 Lucide 语义图标适配层，壳层和登录页通过它使用图标；仪表盘拆成 Hero、指标卡和快捷入口三个展示组件，页面只读取 Pinia 用户/权限数据并派生视图模型。全局 token 负责背景、边框、排版和动效，亮色主题复用同一套色相关系。

**Tech Stack:** Vue 3 `<script setup lang="ts">`, Pinia, Element Plus, SCSS tokens, `lucide-vue-next`, Vitest, vue-tsc, Vite.

## Global Constraints

- API 路径、请求参数、响应格式和后端实现不变。
- 登录页、壳层和首页图标统一来自 `lucide-vue-next`，界面禁止表情符号。
- 页面只呈现帮助当前任务、理解当前数据或决定下一步操作的信息。
- 所有动效在 `prefers-reduced-motion: reduce` 下禁用或降级。
- 保留当前工作区无关文件 `.pnpm-store/`，不覆盖来源不明的配置。

---

### Task 1: Add the Lucide icon adapter and dependency

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/pnpm-lock.yaml`
- Create: `frontend/src/components/AppIcon/index.vue`
- Create: `frontend/src/components/AppIcon/icon-map.ts`
- Test: `frontend/src/components/__tests__/app-icon.spec.ts`

**Interfaces:**
- `AppIcon` props: `{ name: string; size?: number | string; strokeWidth?: number; label?: string }`.
- `icon-map.ts` exports `resolveAppIcon(name: string): Component` and a typed fallback.

- [ ] **Step 1: Add the dependency**

Run from `frontend/`:

```bash
pnpm add lucide-vue-next
```

- [ ] **Step 2: Write the adapter test**

```ts
it("resolves known names and falls back for unknown names", () => {
  expect(resolveAppIcon("search")).toBe(Search)
  expect(resolveAppIcon("unknown")).toBe(CircleHelp)
})
```

- [ ] **Step 3: Implement the map and wrapper**

Map semantic names used by the shell and login (`command`, `search`, `maximize`, `minimize`, `sliders-horizontal`, `languages`, `bell`, `settings`, `user-round`, `lock-keyhole`, `loader-circle`, `arrow-right`, `circle-help`, `layout-dashboard`, `users-round`, `shield-check`, `panel-left-close`, `panel-left-open`) to Lucide components. Render `aria-hidden` unless `label` is supplied.

- [ ] **Step 4: Run the focused test**

Run: `pnpm vitest run src/components/__tests__/app-icon.spec.ts`
Expected: PASS.

### Task 2: Rebuild shared tokens and shell icon surfaces

**Files:**
- Modify: `frontend/src/styles/tokens/_color.scss`
- Modify: `frontend/src/styles/tokens/_shadow.scss`
- Modify: `frontend/src/styles/skins/_chrome.scss`
- Modify: `frontend/src/styles/skins/_menu.scss`
- Modify: `frontend/src/styles/foundation/_layout.scss`
- Modify: `frontend/src/layouts/components/AppLogo/index.vue`
- Modify: `frontend/src/layouts/components/Menu/components/MenuItemContent.vue`
- Modify: `frontend/src/layouts/components/NavBar/index.vue`
- Modify: `frontend/src/layouts/components/NavBar/components/NavbarActions.vue`
- Modify: `frontend/src/components/MenuSearch/index.vue`
- Modify: `frontend/src/components/Fullscreen/index.vue`
- Modify: `frontend/src/components/SizeSelect/index.vue`
- Modify: `frontend/src/components/LangSelect/index.vue`
- Modify: `frontend/src/components/Notification/index.vue`
- Modify: `frontend/src/components/DarkModeSwitch/index.vue`

**Interfaces:**
- Existing route metadata and Pinia stores remain unchanged.
- Existing menu and navbar events continue to call current handlers.

- [ ] **Step 1: Replace shell icon markup**

Use `<AppIcon>` for logo, menu fallback, search, fullscreen, layout size, language, bell, theme and settings. Keep existing labels and handlers; only icon rendering changes.

- [ ] **Step 2: Apply the visual token layer**

Set dark-first shell variables, bright-theme overrides, grid background, coral active state, translucent navbar and tighter focus rings. Keep existing layout dimensions and responsive breakpoints.

- [ ] **Step 3: Add reduced-motion rules**

Wrap shell hover transforms and background motion in a media query that disables transitions and transforms for reduced-motion users.

- [ ] **Step 4: Run shell governance checks**

Run: `pnpm vitest run src/layouts/components/__tests__ src/views/__tests__/dashboard-style-migration.spec.ts`
Expected: PASS; no route or event behavior changes.

### Task 3: Rebuild the dashboard as focused, data-backed composition

**Files:**
- Modify: `frontend/src/views/dashboard/index.vue`
- Create: `frontend/src/views/dashboard/components/DashboardHero.vue`
- Create: `frontend/src/views/dashboard/components/DashboardMetricCard.vue`
- Create: `frontend/src/views/dashboard/components/DashboardQuickActions.vue`
- Modify: `frontend/src/styles/pages/_dashboard.scss`
- Modify: `frontend/src/views/__tests__/dashboard-style-migration.spec.ts`

**Interfaces:**
- `DashboardHero` props: `{ name: string; avatar?: string; currentTime: string }`.
- `DashboardMetricCard` props: `{ label: string; value: string | number; icon: string; accent: "coral" | "blue" | "neutral" }`.
- `DashboardQuickActions` props: `{ items: Array<{ title: string; path: string; icon?: string }> }`; emits `navigate(path: string)`.

- [ ] **Step 1: Add focused component tests**

Cover: metric values render, quick action emits its route, empty actions render a concise empty state, and dashboard source contains no emoji or GithubCorner.

- [ ] **Step 2: Implement the components**

Use actual `useUserStore` info, permission route count, role count and permission count. Flatten only visible route entries for shortcuts. Use `router.push` in the page event handler.

- [ ] **Step 3: Implement the visual composition**

Create a split hero with a time marker, identity block, metric rail and route shortcuts. Use CSS grid, pseudo-element grid lines, subtle pointer hover variables and staggered entry animation; remove external document/video links.

- [ ] **Step 4: Run dashboard tests**

Run: `pnpm vitest run src/views/__tests__/dashboard-style-migration.spec.ts src/views/dashboard`
Expected: PASS.

### Task 4: Rebuild the login entrance with Lucide and no decorative copy

**Files:**
- Modify: `frontend/src/views/login/index.vue`
- Modify: `frontend/src/views/login/components/Login.vue`
- Modify: `frontend/src/views/login/components/Register.vue`
- Modify: `frontend/src/views/login/components/ResetPwd.vue`
- Modify: `frontend/src/styles/pages/_login.scss`

**Interfaces:**
- Existing login/register/reset form `v-model`, validation rules and submit functions remain unchanged.
- Existing theme and language controls remain available.

- [ ] **Step 1: Replace form and action icons**

Use `AppIcon`/Lucide for user, lock, captcha, loading, theme and language affordances. Preserve `aria-label`s and keyboard submit behavior.

- [ ] **Step 2: Implement the split entrance layout**

Make the left canvas visual-only with concise product identity, and the right panel the only interactive form surface. Keep existing async component switching and footer behavior.

- [ ] **Step 3: Add responsive and reduced-motion states**

Collapse to a single form column below tablet width and disable canvas movement under reduced motion.

- [ ] **Step 4: Run login focused checks**

Run: `pnpm vitest run src/views/login src/views/__tests__`
Expected: PASS.

### Task 5: Validate, self-review and report

**Files:**
- Modify if needed: `docs/DOC_SYNC_CHECKLIST.md` or `docs/ARCHITECTURE.md` only if the final implementation changes documented architecture.

- [ ] **Step 1: Run type checking**

Run: `pnpm type-check`
Expected: exit code 0.

- [ ] **Step 2: Run lint checks**

Run: `pnpm lint:check`
Expected: exit code 0.

- [ ] **Step 3: Run the production build**

Run: `pnpm build`
Expected: exit code 0 and generated dist assets.

- [ ] **Step 4: Review the diff and worktree**

Run: `git diff --stat && git diff --check && git status --short --branch`.
Confirm only the planned files and the pre-existing `.pnpm-store/` are present; report the `.git` write restriction separately.
