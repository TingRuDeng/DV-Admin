# Frontend Style Governance Refactor Implementation Plan

> ⚠️ **已归档**
>
> 本文档已于 2026-05-06 归档，内容可能已过时。
> 当前权威文档请参考 `/AGENTS.md`、`/docs/README.md`、`/docs/ARCHITECTURE.md`。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the frontend style system into clear layers, add reusable page-shell components, and migrate `dashboard`, `system/user`, and `system/role` to the new structure without changing business behavior.

**Architecture:** Split `frontend/src/styles` into `tokens`, `theme`, `foundation`, `skins`, and `pages`, then route shared page structure through three thin shell components: `PageShell`, `FilterPanel`, and `DataPanel`. Keep non-migrated pages working through a temporary compatibility shim in `_minimal-saas.scss`, while migrated pages stop depending on `glass-panel` and `minimal-*` classes.

**Tech Stack:** Vue 3, Vite, TypeScript, Sass, Vitest, Element Plus, UnoCSS

---

### Task 1: Split The Style Entry Into Layered Directories

**Files:**
- Create: `frontend/src/styles/tokens/_color.scss`
- Create: `frontend/src/styles/tokens/_spacing.scss`
- Create: `frontend/src/styles/tokens/_radius.scss`
- Create: `frontend/src/styles/tokens/_shadow.scss`
- Create: `frontend/src/styles/tokens/_motion.scss`
- Create: `frontend/src/styles/tokens/_z-index.scss`
- Create: `frontend/src/styles/tokens/index.scss`
- Create: `frontend/src/styles/theme/_light.scss`
- Create: `frontend/src/styles/theme/_dark.scss`
- Create: `frontend/src/styles/theme/_element-plus.scss`
- Create: `frontend/src/styles/theme/index.scss`
- Create: `frontend/src/styles/foundation/_base.scss`
- Create: `frontend/src/styles/foundation/_layout.scss`
- Create: `frontend/src/styles/foundation/index.scss`
- Create: `frontend/src/styles/pages/index.scss`
- Modify: `frontend/src/styles/index.scss`
- Test: `frontend/src/utils/__tests__/style-governance.test.ts`

- [ ] **Step 1: Write the failing style-governance test**

```ts
// frontend/src/utils/__tests__/style-governance.test.ts
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { compile } from "sass";
import { describe, expect, it } from "vitest";

describe("style governance entrypoint", () => {
  it("compiles layered styles and exposes the shared page-shell hooks", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).toContain(".ff-page-shell");
    expect(css).toContain("--ff-color-bg-page");
    expect(css).toContain("linear-gradient(135deg");
  });

  it("keeps _minimal-saas.scss as a compatibility shim instead of the primary rule dump", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).toContain("Temporary compatibility layer");
    expect(source).not.toContain(".minimal-btn {");
  });
});
```

- [ ] **Step 2: Run the targeted test and confirm it fails**

Run: `pnpm --dir frontend vitest run src/utils/__tests__/style-governance.test.ts`

Expected: FAIL because `src/styles/index.scss` does not compile the new `ff-*` shell hooks yet, and `_minimal-saas.scss` is still the main rule dump.

- [ ] **Step 3: Create the layered Sass structure and rewrite the style entrypoint**

```scss
// frontend/src/styles/tokens/_color.scss
:root {
  --ff-color-bg-page: #f1f5f9;
  --ff-color-bg-panel: rgba(255, 255, 255, 0.72);
  --ff-color-bg-panel-strong: rgba(255, 255, 255, 0.9);
  --ff-color-border-soft: rgba(148, 163, 184, 0.18);
  --ff-color-text-primary: #334155;
  --ff-color-text-secondary: #64748b;
}

html.dark {
  --ff-color-bg-page: #0f172a;
  --ff-color-bg-panel: rgba(15, 23, 42, 0.74);
  --ff-color-bg-panel-strong: rgba(15, 23, 42, 0.92);
  --ff-color-border-soft: rgba(255, 255, 255, 0.1);
  --ff-color-text-primary: #e2e8f0;
  --ff-color-text-secondary: #cbd5e1;
}

// frontend/src/styles/tokens/_spacing.scss
:root {
  --ff-page-gap: 1rem;
  --ff-panel-padding: 1.25rem;
  --ff-panel-padding-lg: 1.5rem;
  --ff-toolbar-gap: 0.75rem;
}

// frontend/src/styles/tokens/_radius.scss
:root {
  --ff-radius-panel: 1rem;
  --ff-radius-control: 0.75rem;
  --ff-radius-chip: 999px;
}

// frontend/src/styles/tokens/_shadow.scss
:root {
  --ff-shadow-panel: 0 18px 40px -22px rgba(15, 23, 42, 0.24);
  --ff-shadow-control: 0 0 0 1px rgba(148, 163, 184, 0.18) inset;
}

// frontend/src/styles/tokens/_motion.scss
:root {
  --ff-duration-fast: 0.2s;
  --ff-duration-base: 0.3s;
}

// frontend/src/styles/tokens/_z-index.scss
:root {
  --ff-z-toolbar: 2;
  --ff-z-panel: 1;
}

// frontend/src/styles/tokens/index.scss
@forward "color";
@forward "spacing";
@forward "radius";
@forward "shadow";
@forward "motion";
@forward "z-index";

// frontend/src/styles/theme/_light.scss
html:not(.dark) {
  color-scheme: light;
}

// frontend/src/styles/theme/_dark.scss
html.dark {
  color-scheme: dark;
}

// frontend/src/styles/theme/_element-plus.scss
:root {
  --el-bg-color-page: var(--ff-color-bg-page);
  --el-bg-color-overlay: var(--ff-color-bg-panel-strong);
  --el-text-color-primary: var(--ff-color-text-primary);
  --el-text-color-regular: var(--ff-color-text-secondary);
  --el-border-color: var(--ff-color-border-soft);
}

// frontend/src/styles/theme/index.scss
@use "../tokens";
@use "light";
@use "dark";
@use "element-plus";

// frontend/src/styles/foundation/_base.scss
html,
body,
#app {
  min-height: 100%;
}

body {
  color: var(--ff-color-text-primary);
  background: linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%);
}

html.dark body {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

// frontend/src/styles/foundation/_layout.scss
.ff-page-shell {
  display: flex;
  flex-direction: column;
  gap: var(--ff-page-gap);
  min-height: 100%;
  padding: 1rem;
}

@media (min-width: 768px) {
  .ff-page-shell {
    padding: 1.5rem;
  }
}

// frontend/src/styles/foundation/index.scss
@use "../tokens";
@use "../reset";
@use "base";
@use "layout";

// frontend/src/styles/pages/index.scss
// Page-specific imports are added as pages migrate.

// frontend/src/styles/index.scss
@use "./tokens";
@use "./theme";
@use "./foundation";
@use "./skins";
@use "./pages";
@use "./element-plus";
@use "./element-plus-custom";
@use "./vxe-table";
@import url("./vxe-table.css");
```

- [ ] **Step 4: Run the style-governance test and make sure it passes**

Run: `pnpm --dir frontend vitest run src/utils/__tests__/style-governance.test.ts`

Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit the layered style entrypoint**

```bash
git add \
  frontend/src/styles/tokens \
  frontend/src/styles/theme \
  frontend/src/styles/foundation \
  frontend/src/styles/pages/index.scss \
  frontend/src/styles/index.scss \
  frontend/src/utils/__tests__/style-governance.test.ts
git commit -m "refactor(frontend): split frontend style layers"
```

### Task 2: Add Shared Skin Modules And A Compatibility Shim

**Files:**
- Create: `frontend/src/styles/skins/_panel.scss`
- Create: `frontend/src/styles/skins/_toolbar.scss`
- Create: `frontend/src/styles/skins/_form.scss`
- Create: `frontend/src/styles/skins/_table.scss`
- Create: `frontend/src/styles/skins/_dialog.scss`
- Create: `frontend/src/styles/skins/_drawer.scss`
- Create: `frontend/src/styles/skins/_tag.scss`
- Create: `frontend/src/styles/skins/_button.scss`
- Create: `frontend/src/styles/skins/index.scss`
- Modify: `frontend/src/styles/_minimal-saas.scss`
- Test: `frontend/src/utils/__tests__/theme-styles.test.ts`

- [ ] **Step 1: Extend the existing Sass test coverage to lock in the new shared skins**

```ts
// append to frontend/src/utils/__tests__/theme-styles.test.ts
it("styles shared shell panels and tables through ff semantic hooks", () => {
  const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
  const css = compile(indexScssPath).css;

  injectStyle(css);
  document.body.innerHTML = `
    <section class="ff-page-shell">
      <section class="ff-filter-panel"></section>
      <section class="ff-data-panel">
        <div class="ff-data-panel__body">
          <table class="ff-table"></table>
        </div>
      </section>
    </section>
  `;

  const filterPanel = document.querySelector(".ff-filter-panel") as HTMLElement;
  const dataPanel = document.querySelector(".ff-data-panel") as HTMLElement;

  expect(getComputedStyle(filterPanel).borderRadius).toBe("16px");
  expect(getComputedStyle(dataPanel).backgroundColor).not.toBe("");
});
```

- [ ] **Step 2: Run the Sass tests and confirm the new case fails**

Run: `pnpm --dir frontend vitest run src/utils/__tests__/theme-styles.test.ts`

Expected: FAIL because `.ff-filter-panel` and `.ff-data-panel` do not have shared skin rules yet.

- [ ] **Step 3: Create the skin modules and turn `_minimal-saas.scss` into a compatibility file**

```scss
// frontend/src/styles/skins/_panel.scss
.ff-filter-panel,
.ff-data-panel,
.ff-side-panel {
  background: var(--ff-color-bg-panel);
  border: 1px solid var(--ff-color-border-soft);
  border-radius: var(--ff-radius-panel);
  box-shadow: var(--ff-shadow-panel);
  backdrop-filter: blur(18px);
}

.ff-filter-panel {
  padding: var(--ff-panel-padding-lg);
}

.ff-data-panel {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  padding: var(--ff-panel-padding-lg);
}

.ff-data-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.ff-data-panel__body {
  flex: 1;
  min-height: 0;
}

// frontend/src/styles/skins/_toolbar.scss
.ff-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--ff-toolbar-gap);
}

.ff-toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

// frontend/src/styles/skins/_form.scss
.ff-form .el-form-item {
  margin-bottom: 0;
}

.ff-form .el-input__wrapper,
.ff-form .el-select__wrapper,
.ff-form .el-textarea__inner {
  border-radius: var(--ff-radius-control);
  box-shadow: var(--ff-shadow-control);
}

// frontend/src/styles/skins/_table.scss
.ff-table {
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.32);
}

.ff-table-wrap {
  overflow: hidden;
  border: 1px solid var(--ff-color-border-soft);
  border-radius: calc(var(--ff-radius-panel) - 2px);
  background: rgba(255, 255, 255, 0.2);
}

html.dark .ff-table-wrap {
  background: rgba(15, 23, 42, 0.28);
}

// frontend/src/styles/skins/_dialog.scss
.ff-dialog .el-dialog {
  border-radius: var(--ff-radius-panel);
}

// frontend/src/styles/skins/_drawer.scss
.ff-drawer {
  --el-drawer-padding-primary: 1.25rem;
}

// frontend/src/styles/skins/_tag.scss
.ff-status-tag {
  padding-inline: 0.75rem;
  border: none;
  border-radius: var(--ff-radius-chip);
}

// frontend/src/styles/skins/_button.scss
.ff-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.ff-button-primary {
  border-radius: var(--ff-radius-control);
}

.ff-button-secondary,
.ff-button-danger {
  border-radius: var(--ff-radius-control);
}

// frontend/src/styles/skins/index.scss
@use "panel";
@use "toolbar";
@use "form";
@use "table";
@use "dialog";
@use "drawer";
@use "tag";
@use "button";

// frontend/src/styles/_minimal-saas.scss
// Temporary compatibility layer for non-migrated pages.
.glass-panel {
  background: var(--ff-color-bg-panel);
  border: 1px solid var(--ff-color-border-soft);
  border-radius: var(--ff-radius-panel);
  box-shadow: var(--ff-shadow-panel);
  backdrop-filter: blur(18px);
}

.minimal-form {
  .el-form-item {
    margin-bottom: 0;
  }
}

.minimal-table {
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.32);
}

.minimal-dialog .el-dialog {
  border-radius: var(--ff-radius-panel);
}

.minimal-tag {
  padding-inline: 0.75rem;
  border: none;
  border-radius: var(--ff-radius-chip);
}
```

- [ ] **Step 4: Run the Sass tests again**

Run: `pnpm --dir frontend vitest run src/utils/__tests__/theme-styles.test.ts`

Expected: PASS with the new `ff-*` skin assertions succeeding alongside the existing dark-mode checks.

- [ ] **Step 5: Commit the shared skins and compatibility shim**

```bash
git add \
  frontend/src/styles/skins \
  frontend/src/styles/_minimal-saas.scss \
  frontend/src/utils/__tests__/theme-styles.test.ts
git commit -m "refactor(frontend): add shared page skins"
```

### Task 3: Add Reusable Page-Shell Components

**Files:**
- Create: `frontend/src/components/PageShell/index.vue`
- Create: `frontend/src/components/FilterPanel/index.vue`
- Create: `frontend/src/components/DataPanel/index.vue`
- Create: `frontend/src/components/__tests__/page-shell.spec.ts`

- [ ] **Step 1: Write the failing component tests**

```ts
// frontend/src/components/__tests__/page-shell.spec.ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PageShell from "@/components/PageShell/index.vue";
import FilterPanel from "@/components/FilterPanel/index.vue";
import DataPanel from "@/components/DataPanel/index.vue";

describe("page shell components", () => {
  it("renders PageShell with the shared wrapper class", () => {
    const wrapper = mount(PageShell, {
      slots: { default: "<div class='inner'>content</div>" },
    });

    expect(wrapper.classes()).toContain("ff-page-shell");
    expect(wrapper.find(".inner").exists()).toBe(true);
  });

  it("renders FilterPanel as a semantic shell", () => {
    const wrapper = mount(FilterPanel, {
      slots: { default: "<form class='filter-body'></form>" },
    });

    expect(wrapper.classes()).toContain("ff-filter-panel");
    expect(wrapper.find(".filter-body").exists()).toBe(true);
  });

  it("renders DataPanel title, actions, body, and footer slots", () => {
    const wrapper = mount(DataPanel, {
      props: { title: "用户数据" },
      slots: {
        actions: "<button class='action'>新增</button>",
        default: "<div class='table-body'></div>",
        footer: "<div class='pager'></div>",
      },
    });

    expect(wrapper.find(".ff-data-panel__title").text()).toContain("用户数据");
    expect(wrapper.find(".action").exists()).toBe(true);
    expect(wrapper.find(".table-body").exists()).toBe(true);
    expect(wrapper.find(".pager").exists()).toBe(true);
  });
});
```

- [ ] **Step 2: Run the component test and verify it fails**

Run: `pnpm --dir frontend vitest run src/components/__tests__/page-shell.spec.ts`

Expected: FAIL because the page-shell components do not exist yet.

- [ ] **Step 3: Implement the three shell components**

```vue
<!-- frontend/src/components/PageShell/index.vue -->
<template>
  <section class="ff-page-shell" :class="{ 'ff-page-shell--fill': fill }">
    <slot />
  </section>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ fill?: boolean }>(), {
  fill: true,
});
</script>

<!-- frontend/src/components/FilterPanel/index.vue -->
<template>
  <section class="ff-filter-panel">
    <slot />
  </section>
</template>

<!-- frontend/src/components/DataPanel/index.vue -->
<template>
  <section class="ff-data-panel">
    <header class="ff-data-panel__header">
      <div class="ff-data-panel__title">
        <slot name="title">
          <span>{{ title }}</span>
        </slot>
      </div>
      <div v-if="$slots.actions" class="ff-data-panel__actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="ff-data-panel__body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="ff-data-panel__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>
```

- [ ] **Step 4: Run the component test and make sure it passes**

Run: `pnpm --dir frontend vitest run src/components/__tests__/page-shell.spec.ts`

Expected: PASS with `3 passed`.

- [ ] **Step 5: Commit the shell components**

```bash
git add \
  frontend/src/components/PageShell/index.vue \
  frontend/src/components/FilterPanel/index.vue \
  frontend/src/components/DataPanel/index.vue \
  frontend/src/components/__tests__/page-shell.spec.ts
git commit -m "feat(frontend): add shared page shell components"
```

### Task 4: Migrate The Dashboard Page To The Shared Shells

**Files:**
- Create: `frontend/src/views/__tests__/dashboard-style-migration.spec.ts`
- Create: `frontend/src/styles/pages/_dashboard.scss`
- Modify: `frontend/src/styles/pages/index.scss`
- Modify: `frontend/src/views/dashboard/index.vue`

- [ ] **Step 1: Write the failing dashboard migration test**

```ts
// frontend/src/views/__tests__/dashboard-style-migration.spec.ts
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("dashboard style migration", () => {
  it("uses the shared page shell instead of glass-panel markup", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/dashboard/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain('class="ff-page-shell__hero');
    expect(source).not.toContain("glass-panel");
  });
});
```

- [ ] **Step 2: Run the dashboard migration test and confirm it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/dashboard-style-migration.spec.ts`

Expected: FAIL because `dashboard/index.vue` still uses `app-container` and `glass-panel`.

- [ ] **Step 3: Migrate the dashboard template and add page-specific styling**

```vue
<!-- key structure in frontend/src/views/dashboard/index.vue -->
<template>
  <PageShell>
    <section class="ff-page-shell__hero ff-page-shell__hero--dashboard">
      <GithubCorner class="github-corner" />

      <div class="ff-dashboard__top">
        <div class="ff-dashboard__greeting">
          <img
            class="ff-dashboard__avatar"
            :src="userStore.userInfo.avatar + '?imageView2/1/w/80/h/80'"
          />
          <p class="ff-dashboard__headline">{{ greetings }}</p>
        </div>

        <div class="ff-dashboard__links">
          <!-- existing document/video links stay unchanged -->
        </div>
      </div>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import GithubCorner from "@/components/GithubCorner/index.vue";
</script>
```

```scss
// frontend/src/styles/pages/_dashboard.scss
.ff-page-shell__hero--dashboard {
  position: relative;
  padding: var(--ff-panel-padding-lg);
  background: var(--ff-color-bg-panel);
  border: 1px solid var(--ff-color-border-soft);
  border-radius: var(--ff-radius-panel);
  box-shadow: var(--ff-shadow-panel);
}

.ff-dashboard__top {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
}

.ff-dashboard__greeting {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
}

.ff-dashboard__avatar {
  width: 5rem;
  height: 5rem;
  border-radius: 999px;
}

// append to frontend/src/styles/pages/index.scss
@use "dashboard";
```

- [ ] **Step 4: Run the dashboard migration test**

Run: `pnpm --dir frontend vitest run src/views/__tests__/dashboard-style-migration.spec.ts`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the dashboard migration**

```bash
git add \
  frontend/src/views/dashboard/index.vue \
  frontend/src/styles/pages/_dashboard.scss \
  frontend/src/views/__tests__/dashboard-style-migration.spec.ts
git commit -m "refactor(frontend): migrate dashboard to page shells"
```

### Task 5: Migrate The Role Page To FilterPanel And DataPanel

**Files:**
- Create: `frontend/src/views/__tests__/role-style-migration.spec.ts`
- Create: `frontend/src/styles/pages/_system-role.scss`
- Modify: `frontend/src/styles/pages/index.scss`
- Modify: `frontend/src/views/system/role/index.vue`

- [ ] **Step 1: Write the failing role migration test**

```ts
// frontend/src/views/__tests__/role-style-migration.spec.ts
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system role style migration", () => {
  it("uses PageShell, FilterPanel, and DataPanel without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/role/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<FilterPanel");
    expect(source).toContain("<DataPanel");
    expect(source).not.toContain("minimal-btn");
    expect(source).not.toContain("glass-panel");
  });
});
```

- [ ] **Step 2: Run the role migration test and verify it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/role-style-migration.spec.ts`

Expected: FAIL because the role page still depends on `glass-panel` and `minimal-*` classes.

- [ ] **Step 3: Refactor the role page to shared shells and semantic hooks**

```vue
<!-- key structure in frontend/src/views/system/role/index.vue -->
<template>
  <PageShell>
    <FilterPanel>
      <el-form
        ref="queryFormRef"
        :model="queryParams"
        :inline="true"
        class="ff-form ff-toolbar"
        @submit.prevent
      >
        <!-- existing search fields -->
      </el-form>
    </FilterPanel>

    <DataPanel title="角色数据">
      <template #actions>
        <div class="ff-button-group">
          <el-button type="primary" icon="plus" class="ff-button-primary" @click="handleOpenDialog()">
            新增角色
          </el-button>
          <el-button
            type="danger"
            plain
            icon="delete"
            class="ff-button-danger"
            :disabled="ids.length === 0"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </template>

      <div class="ff-table-wrap">
        <el-table ref="dataTableRef" v-loading="loading" :data="roleList" class="ff-table">
          <!-- existing columns -->
        </el-table>
      </div>

      <template #footer>
        <Pagination
          v-if="total > 0"
          v-model:total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="fetchData"
        />
      </template>
    </DataPanel>

    <el-dialog v-model="dialog.visible" :title="dialog.title" class="ff-dialog" width="500px">
      <!-- existing dialog form -->
    </el-dialog>

    <el-drawer v-model="assignPermDialogVisible" :title="'【' + checkedRole.name + '】权限分配'" class="ff-drawer">
      <!-- existing drawer content -->
    </el-drawer>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import FilterPanel from "@/components/FilterPanel/index.vue";
import DataPanel from "@/components/DataPanel/index.vue";
</script>
```

```scss
// frontend/src/styles/pages/_system-role.scss
.ff-role-page .ff-data-panel__body {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.ff-role-page .ff-status-cell {
  display: inline-flex;
  align-items: center;
}

// append to frontend/src/styles/pages/index.scss
@use "system-role";
```

- [ ] **Step 4: Run the role migration test**

Run: `pnpm --dir frontend vitest run src/views/__tests__/role-style-migration.spec.ts`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the role page migration**

```bash
git add \
  frontend/src/views/system/role/index.vue \
  frontend/src/styles/pages/_system-role.scss \
  frontend/src/views/__tests__/role-style-migration.spec.ts
git commit -m "refactor(frontend): migrate role page to shared shells"
```

### Task 6: Migrate The User Page To Shared Shells

**Files:**
- Create: `frontend/src/views/__tests__/user-style-migration.spec.ts`
- Create: `frontend/src/styles/pages/_system-user.scss`
- Modify: `frontend/src/styles/pages/index.scss`
- Modify: `frontend/src/views/system/user/index.vue`

- [ ] **Step 1: Write the failing user migration test**

```ts
// frontend/src/views/__tests__/user-style-migration.spec.ts
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system user style migration", () => {
  it("uses the shared page shells and no longer depends on glass-panel or minimal-* hooks", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/user/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<FilterPanel");
    expect(source).toContain("<DataPanel");
    expect(source).toContain('class="ff-side-panel');
    expect(source).not.toContain("glass-panel");
    expect(source).not.toContain("minimal-");
  });
});
```

- [ ] **Step 2: Run the user migration test and verify it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/user-style-migration.spec.ts`

Expected: FAIL because the user page still uses `glass-panel`, `minimal-input`, `minimal-btn`, `minimal-table`, and `glass-drawer`.

- [ ] **Step 3: Refactor the user page to the shared shells**

```vue
<!-- key structure in frontend/src/views/system/user/index.vue -->
<template>
  <PageShell class="ff-user-page">
    <div class="ff-user-page__grid">
      <aside class="ff-side-panel">
        <DeptTree
          v-model="queryParams.deptId"
          class="ff-user-page__dept-tree"
          @node-click="handleQuery"
        />
      </aside>

      <section class="ff-user-page__main">
        <FilterPanel>
          <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="ff-form ff-toolbar">
            <!-- existing search fields -->
          </el-form>
        </FilterPanel>

        <DataPanel title="用户数据">
          <template #actions>
            <div class="ff-button-group">
              <el-button
                v-hasPerm="['system:users:add']"
                type="primary"
                icon="plus"
                class="ff-button-primary"
                @click="handleOpenDialog()"
              >
                新增用户
              </el-button>
              <el-button
                v-hasPerm="['system:users:delete']"
                type="danger"
                plain
                icon="delete"
                class="ff-button-danger"
                :disabled="selectIds.length === 0"
                @click="handleDelete()"
              >
                批量删除
              </el-button>
            </div>
          </template>

          <div class="ff-table-wrap">
            <el-table v-loading="loading" :data="pageData" class="ff-table">
              <!-- existing columns -->
            </el-table>
          </div>

          <template #footer>
            <Pagination
              v-if="total > 0"
              v-model:total="total"
              v-model:page="queryParams.pageNum"
              v-model:limit="queryParams.pageSize"
              @pagination="fetchData"
            />
          </template>
        </DataPanel>
      </section>
    </div>

    <el-drawer
      v-model="dialog.visible"
      :title="dialog.title"
      append-to-body
      class="ff-drawer"
      :size="drawerSize"
      @close="handleCloseDialog"
    >
      <!-- existing form content -->
    </el-drawer>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import FilterPanel from "@/components/FilterPanel/index.vue";
import DataPanel from "@/components/DataPanel/index.vue";
</script>
```

```scss
// frontend/src/styles/pages/_system-user.scss
.ff-user-page__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--ff-page-gap);
  min-height: 0;
}

@media (min-width: 1024px) {
  .ff-user-page__grid {
    grid-template-columns: 280px minmax(0, 1fr);
  }
}

.ff-user-page__main {
  display: flex;
  flex-direction: column;
  gap: var(--ff-page-gap);
  min-height: 0;
}

.ff-user-page__dept-tree {
  min-height: 100%;
}

// append to frontend/src/styles/pages/index.scss
@use "system-user";
```

- [ ] **Step 4: Run the user migration test**

Run: `pnpm --dir frontend vitest run src/views/__tests__/user-style-migration.spec.ts`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the user page migration**

```bash
git add \
  frontend/src/views/system/user/index.vue \
  frontend/src/styles/pages/_system-user.scss \
  frontend/src/views/__tests__/user-style-migration.spec.ts
git commit -m "refactor(frontend): migrate user page to shared shells"
```

### Task 7: Document The New Conventions And Run Full Verification

**Files:**
- Create: `frontend/src/styles/README.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Add a lightweight documentation check by asserting the new README exists and names the shell pattern**

```ts
// append to frontend/src/utils/__tests__/style-governance.test.ts
it("documents the new style layers and page shell usage", () => {
  const source = readFileSync(resolve(process.cwd(), "src/styles/README.md"), "utf8");

  expect(source).toContain("tokens -> theme -> foundation -> skins -> pages");
  expect(source).toContain("PageShell");
  expect(source).toContain("FilterPanel");
  expect(source).toContain("DataPanel");
});
```

- [ ] **Step 2: Run the targeted test and confirm it fails before the docs are written**

Run: `pnpm --dir frontend vitest run src/utils/__tests__/style-governance.test.ts`

Expected: FAIL because `frontend/src/styles/README.md` does not exist yet.

- [ ] **Step 3: Write the local frontend style guide and architecture note**

```md
<!-- frontend/src/styles/README.md -->
# Frontend Style Layers

Layer order:

1. `tokens`
2. `theme`
3. `foundation`
4. `skins`
5. `pages`

Use `PageShell`, `FilterPanel`, and `DataPanel` for new admin pages.
Do not add new `glass-panel` or `minimal-*` usage.
Keep `:deep()` and `!important` inside shared skin overrides unless a page-specific exception is unavoidable.
```

```md
<!-- append a short section to docs/ARCHITECTURE.md -->
## Frontend Style Governance

The frontend uses layered Sass entrypoints under `frontend/src/styles`:
`tokens -> theme -> foundation -> skins -> pages`.

New admin pages should compose `PageShell`, `FilterPanel`, and `DataPanel` instead of rebuilding panel/form/table styling inside each page SFC.
```

- [ ] **Step 4: Run the full verification suite**

Run: `pnpm --dir frontend type-check`
Expected: PASS

Run: `pnpm --dir frontend test:run`
Expected: PASS

Run: `pnpm --dir frontend build`
Expected: PASS

Run: `git diff --check`
Expected: PASS with no whitespace errors

- [ ] **Step 5: Commit the documentation and verified refactor**

```bash
git add \
  frontend/src/styles/README.md \
  docs/ARCHITECTURE.md \
  frontend/src/utils/__tests__/style-governance.test.ts
git commit -m "docs(frontend): document style governance layers"
```

## Self-Review

### Spec Coverage

- Style layering in the approved spec is implemented by Tasks 1 and 2.
- Page-shell components from the approved spec are implemented by Task 3.
- Sample page migration for `dashboard`, `system/role`, and `system/user` is covered by Tasks 4, 5, and 6.
- Documentation for future page authors is covered by Task 7.
- Validation requirements from the approved spec are covered by Task 7.

### Placeholder Scan

- No `TODO`, `TBD`, or deferred implementation markers remain.
- Every task lists exact files, commands, and commit messages.
- Every code-writing step includes concrete snippets for the files being introduced or changed.

### Type And Naming Consistency

- Shared shell naming is consistently `PageShell`, `FilterPanel`, `DataPanel`.
- Shared semantic classes consistently use the `ff-` prefix.
- Sass layering names match the approved spec: `tokens`, `theme`, `foundation`, `skins`, `pages`.
