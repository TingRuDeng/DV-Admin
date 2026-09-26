# Frontend Style Layers

The frontend style system is organized in this order:

`tokens -> theme -> foundation -> skins -> pages`

## Layer responsibilities

- `tokens`: shared design values such as color, spacing, radius, shadow, motion, and z-index
- `theme`: light/dark mode and Element Plus variable bridges
- `foundation`: reset, base document styles, and page-shell layout rules
- `skins`: reusable panel, form, table, dialog, drawer, tag, button, toolbar, menu, tree, and chrome appearances
- `pages`: page-only exceptions for route views that have already been migrated

## Liquid Chrome visual system

The visual decision record is [ADR-0002](../../../docs/ADR-0002-LIQUID-CHROME-VISUAL-SYSTEM.md).

- Iridescent stops `--ff-iri-a/b/c` and `--ff-on-iri` are written at runtime by `generateIridescentStops` / `applyIridescence` in `src/utils/theme.ts`, derived from the current preset color. The values in `tokens/_color.scss` are only the default-preset fallback.
- Glass surfaces use the `ff-glass` mixin from `foundation/_glass.scss`. The blur lives on `::before` and the host gets `isolation: isolate`, so the host never becomes the containing block of `position: fixed` descendants.
- `backdrop-filter` may appear only in `foundation/_glass.scss` and `skins/_popper.scss`. Custom cursors (`cursor: url(`) and WebGL canvases are not allowed.
- Files that call the mixin must `@use "../foundation/glass" as *;` explicitly; style tests compile without the Vite `additionalData` injection.
- Gradient text uses `color: transparent` with `background-clip: text`. Do not rely on `-webkit-text-fill-color`, because the dark shim resets it to `currentColor`.
- Page styles that must reach Element Plus internals are global files under `pages/`, rooted at the page class (for example `.ff-login-page`), and must not use `:deep(`.
- The navbar menu search pill lives in `skins/_chrome.scss`. `.menu-search` keeps a fixed 168px slot in the flow and `.menu-search__field` is absolutely positioned, so it grows leftward to 260px on focus without reflowing the header. Its teleported `.menu-search__panel` joins the popper glass list in `skins/_popper.scss` and the dark popper fallback in `theme/_dark.scss`; other custom teleported popups should do the same instead of writing their own `backdrop-filter`.

## Page composition rule

New admin pages should compose:

- `PageShell`
- `FilterPanel`
- `DataPanel`

Use UnoCSS mainly for layout and small local utilities. Keep shared visual styling inside `skins/*`.

## Compatibility rule

`_minimal-saas.scss` is now a compatibility layer for non-migrated pages. Do not add new `glass-panel` or `minimal-*` usages in new code.

Treat `_minimal-saas.scss` as a frozen legacy shim. The only allowed responsibilities are:

- text-fill fallback for dark layout containers
- brand gradient preservation for logo/title text
- utility-class dark fallbacks under `.app-container`

Legacy `minimal-*` and `glass-panel` aliases are no longer part of the active stylesheet graph.

## Override rule

Keep `:deep()` and `!important` inside shared skin overrides unless a page-specific exception is unavoidable.
