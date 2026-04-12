# Frontend Style Layers

The frontend style system is organized in this order:

`tokens -> theme -> foundation -> skins -> pages`

## Layer responsibilities

- `tokens`: shared design values such as color, spacing, radius, shadow, motion, and z-index
- `theme`: light/dark mode and Element Plus variable bridges
- `foundation`: reset, base document styles, and page-shell layout rules
- `skins`: reusable panel, form, table, dialog, drawer, tag, button, and toolbar appearances
- `pages`: page-only exceptions for route views that have already been migrated

## Page composition rule

New admin pages should compose:

- `PageShell`
- `FilterPanel`
- `DataPanel`

Use UnoCSS mainly for layout and small local utilities. Keep shared visual styling inside `skins/*`.

## Compatibility rule

`_minimal-saas.scss` is now a compatibility layer for non-migrated pages. Do not add new `glass-panel` or `minimal-*` usages in new code.

## Override rule

Keep `:deep()` and `!important` inside shared skin overrides unless a page-specific exception is unavoidable.
