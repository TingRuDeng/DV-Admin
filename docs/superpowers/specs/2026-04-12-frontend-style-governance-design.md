# Frontend Style Governance Refactor Design

Date: 2026-04-12
Scope: `frontend/`
Target pages: `dashboard`, `system/user`, `system/role`
Refactor level: medium

## 1. Context

The current frontend style system has drifted from layered governance into incremental visual patching. The main problems are:

- `src/styles/index.scss` mixes design-system imports, component-library overrides, page styles, theme background rules, and shared business blocks.
- `src/styles/_minimal-saas.scss` has become a catch-all file for multiple concerns including panel, form, button, table, dialog, tag, and navbar appearance.
- Business pages directly depend on visual-result classes such as `glass-panel`, `minimal-btn`, `minimal-input`, and `minimal-table`.
- Many Vue SFCs use `scoped` styles plus `:deep()` overrides to patch Element Plus behavior locally.
- The current style structure makes it hard to decide whether a change belongs in theme variables, shared component skinning, or a page-specific override.

This has made style changes fragile. Adjusting a shared visual pattern now risks unexpected regressions across unrelated pages.

## 2. Goals

- Rebuild a clear style governance hierarchy without redesigning the UI language.
- Preserve current visual direction and business behavior as much as possible.
- Create a maintainable path for future pages to follow a consistent structure.
- Migrate three representative pages as reference implementations:
  - `frontend/src/views/dashboard/index.vue`
  - `frontend/src/views/system/user/index.vue`
  - `frontend/src/views/system/role/index.vue`
- Allow limited addition of foundational page-shell components and moderate DOM cleanup where it improves style ownership.

## 3. Non-Goals

- No full-site UI redesign.
- No wholesale migration of every page in the admin.
- No business logic rewrites for CURD flows.
- No attempt to remove all UnoCSS usage.
- No attempt to eliminate every historical `:deep()` or `!important` in one pass.

## 4. Design Principles

- Styles must be layered by responsibility.
- Page templates should express structure and semantics, not assemble visual polish ad hoc.
- Component-library overrides must live in dedicated skin/theme layers, not scattered across page SFCs.
- Shared patterns should be named semantically and reused intentionally.
- Page-level style files may only handle local exceptions, not define new cross-page design rules.

## 5. Proposed Style Architecture

The refactor introduces five layers with one-way dependency from low-level tokens upward:

1. `tokens`
   Stores primitive design values only: color, spacing, radius, shadow, motion, z-index, layout constants.
   No direct component styling.

2. `theme`
   Maps tokens into light/dark theme variables and Element Plus variable bridges.
   Responsible for theme state and CSS variable outputs, not page styling.

3. `foundation`
   Defines reset, typography defaults, root layout surfaces, app container conventions, and base responsive skeleton.

4. `skins`
   Defines reusable visual skins for shared UI structures such as panel, toolbar, form, table, dialog, drawer, button, and tag.
   This is the primary home for Element Plus appearance overrides that are intended to be shared.

5. `pages`
   Contains page-specific exceptions for migrated sample pages.
   No new cross-page visual rules may be added here.

## 6. Target Directory Structure

```text
frontend/src/styles/
  index.scss
  tokens/
    _color.scss
    _spacing.scss
    _radius.scss
    _shadow.scss
    _motion.scss
    _z-index.scss
    index.scss
  theme/
    _light.scss
    _dark.scss
    _element-plus.scss
    index.scss
  foundation/
    _reset.scss
    _base.scss
    _layout.scss
    index.scss
  skins/
    _panel.scss
    _toolbar.scss
    _form.scss
    _table.scss
    _dialog.scss
    _drawer.scss
    _tag.scss
    _button.scss
    index.scss
  pages/
    _dashboard.scss
    _system-user.scss
    _system-role.scss
    index.scss
```

## 7. Entry File Responsibilities

`frontend/src/styles/index.scss` should become a thin orchestrator only:

- import tokens
- import theme
- import foundation
- import skins
- import selected page styles
- import required third-party style files that still need explicit inclusion

It should no longer contain large blocks of page behavior, theme compensation rules, or mixed shared/business styling.

## 8. Foundational Page Components

To reduce visual-class sprawl in page templates, introduce a small set of structural components:

- `PageShell`
  - Standard page outer wrapper
  - Owns page padding, vertical spacing, and responsive stacking rules

- `FilterPanel`
  - Standard wrapper for search/filter sections
  - Accepts content via slots
  - Owns panel spacing and high-level layout conventions for inline filter forms

- `DataPanel`
  - Standard wrapper for title, actions, content body, and pagination area
  - Supports table containers and section actions without embedding business logic

These components are intentionally thin. They provide semantic structure and stable style hooks, not business behavior.

## 9. Naming Strategy

The current visual-result classes should be treated as transitional and gradually retired:

- keep `app-container` as a compatibility layer during migration
- phase out direct dependence on:
  - `glass-panel`
  - `minimal-form`
  - `minimal-input`
  - `minimal-btn`
  - `minimal-btn-plain`
  - `minimal-btn-danger`
  - `minimal-table`
  - `minimal-dialog`
  - `minimal-tag`

New shared styles should move toward stable semantic hooks, for example:

- `ff-page-shell`
- `ff-filter-panel`
- `ff-data-panel`
- `ff-form`
- `ff-table`
- `ff-toolbar`

Implementation should use the `ff-` prefix for newly introduced shared semantic hooks. Shared class names must describe role, not visual effect.

## 10. Rules for `:deep()` and `!important`

The refactor establishes explicit limits:

- `:deep()` is allowed in:
  - shared skins for third-party component customization
  - rare page-specific exceptions when no better shared abstraction exists
- `:deep()` should not be added casually inside business pages for shared styling concerns
- `!important` is allowed only for:
  - unavoidable third-party override conflicts
  - theme safety overrides with no cleaner resolution
- ordinary page styling must avoid new `!important`

The implementation should reduce their usage on the migrated pages even if repository-wide totals are not normalized in one pass.

## 11. UnoCSS Usage Policy

UnoCSS remains part of the stack, but its scope should be clearer:

- good uses:
  - spacing
  - flex/grid layout
  - responsive arrangement
  - small utility expressions local to template structure
- avoid using UnoCSS as the primary mechanism for:
  - shared component skin
  - repeated business panel visuals
  - complex visual states that belong in `skins/*`

Templates should stop relying on long chains of utilities plus visual helper classes to recreate the same panel pattern repeatedly.

## 12. Migration Plan for Sample Pages

### 12.1 Dashboard

Purpose in refactor:

- validate panel shell extraction
- validate page shell structure
- remove direct dependence on ad hoc `glass-panel` composition for the page root

Expected migration:

- wrap content in `PageShell`
- replace main content container with shared semantic panel structure
- keep business content and greeting behavior unchanged
- move page-specific layout refinements into `pages/_dashboard.scss`

### 12.2 System Role

Purpose in refactor:

- validate filter section, data section, dialog skin, and drawer skin together
- confirm that medium-complexity CRUD pages can be rewritten without style sprawl

Expected migration:

- search section moves under `FilterPanel`
- list section moves under `DataPanel`
- shared form and table classes replace direct `minimal-*` class usage
- local page-only details stay in `pages/_system-role.scss`

### 12.3 System User

Purpose in refactor:

- validate the most complex target page in scope
- cover split layout, tree panel, filter panel, data panel, drawer, and table cases

Expected migration:

- outer layout becomes `PageShell`
- left department area becomes a semantic side panel
- right filter area and data area move to shared shells
- repeated visual wrappers around table and drawer are replaced with shared hooks
- page-specific tree and drawer adjustments stay isolated in `pages/_system-user.scss`

## 13. Migration Order

Recommended sequence:

1. Restructure style entrypoints and split `_minimal-saas.scss`
2. Introduce page-shell components and semantic style hooks
3. Migrate `dashboard`
4. Migrate `system/role`
5. Migrate `system/user`
6. Remove or deprecate obsolete shared visual classes used by those pages

This order reduces risk by validating the architecture on simpler pages before applying it to the most complex page in scope.

## 14. Implementation Constraints

- Do not change business behavior.
- Do not redesign the visual language unless necessary to preserve consistency during extraction.
- Keep Element Plus as the primary component system.
- Preserve compatibility for non-migrated pages wherever practical.
- Limit DOM restructuring to what is needed for semantic shells and stable style ownership.

## 15. Acceptance Criteria

The refactor is successful when all of the following are true:

- the style directory clearly separates token, theme, foundation, skin, and page layers
- `index.scss` becomes a clean entrypoint instead of a rule dump
- `_minimal-saas.scss` is removed or reduced to a temporary compatibility shim, not a primary style source
- `dashboard`, `system/user`, and `system/role` use the new page-shell structure
- the migrated pages materially reduce direct dependence on `minimal-*` and `glass-panel`
- migrated pages reduce local `:deep()` and `!important` usage where those overrides were compensating for missing shared structure
- future pages can follow a documented pattern built around page-shell components and shared skins

## 16. Validation

At minimum, implementation validation should include:

- `pnpm --dir frontend type-check`
- `pnpm --dir frontend test:run`
- `pnpm --dir frontend build`
- manual UI regression checks for:
  - `dashboard`
  - `system/user`
  - `system/role`

If targeted tests are added, they should focus on shared shell behavior and structural expectations, not brittle broad snapshots.

## 17. Risks and Mitigations

- Risk: compatibility regressions on non-migrated pages
  - Mitigation: keep compatibility shims where necessary and avoid broad global selector rewrites

- Risk: shell components become too opinionated and start owning business layout logic
  - Mitigation: keep components slot-first and structure-only

- Risk: `skins/*` becomes a new dumping ground
  - Mitigation: enforce strict boundaries between skins and page-level overrides during implementation review

- Risk: incomplete deprecation leaves both old and new conventions active for too long
  - Mitigation: document deprecated classes and stop using them in all migrated pages immediately

## 18. Recommended Next Step

After this design is approved, write an implementation plan that breaks the work into:

- style architecture restructuring
- foundation component creation
- page-by-page migration
- verification and cleanup
