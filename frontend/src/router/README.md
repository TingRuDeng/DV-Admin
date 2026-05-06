# Router 模块说明

## 目的

说明前端路由层的关键契约，重点是 `RouteMeta` 规范化与 KeepAlive/cacheKey 行为，避免页面级改动破坏全局缓存和菜单语义。

## 适合读者

- 修改路由、菜单、标签页缓存行为的前端开发者
- 执行页面收口或路由迁移任务的 AI 代理

## 一分钟摘要

- 后端菜单 `meta` 进入 store 前会做 `normalizeMeta` 清洗。
- 页面缓存键优先 `meta.cacheKey`，再退化到路由名或 `fullPath`。
- 默认不按 query 维度分裂缓存，除非显式声明 `cacheByQuery` 或 `cacheQueryKeys`。

```yaml
ai_summary:
  authority: "前端路由元信息与缓存键约定（模块级）"
  scope: "RouteMeta 字段、动态路由规范化、标签缓存键规则"
  read_when:
    - "修改路由 meta 字段时"
    - "排查 keepAlive / tagsView 缓存异常时"
  verify_with:
    - "frontend/src/utils/route-meta.ts"
    - "frontend/src/utils/view-cache.ts"
    - "frontend/src/store/modules/permission-store.ts"
    - "frontend/src/store/modules/tags-view-store.ts"
  stale_when:
    - "RouteMeta 字段变更"
    - "缓存键算法变更"
```

## 权威边界

- 本文件只覆盖路由层本地契约，不替代全局架构文档。
- 全局规则以 `AGENTS.md` 和 `docs/ARCHITECTURE.md` 为准。

## 如何验证

- 运行单测：`pnpm --dir frontend test:unit -- route-meta`、`pnpm --dir frontend test:unit -- view-cache`
- 检查代码：`frontend/src/utils/route-meta.ts`、`frontend/src/utils/view-cache.ts`、`frontend/src/layouts/components/AppMain/index.vue`
