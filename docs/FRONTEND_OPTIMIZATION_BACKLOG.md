# DV-Admin 前端优化待办

> 本文档用于记录**当前仍有效**的前端后续优化事项。它基于仓库现状重新整理，替代仓库根目录 `后续优化/` 下旧方案文档中的可执行部分。

---

## 文档定位

- 本文档是当前前端优化 backlog 的跟踪入口
- `后续优化/` 目录下的旧文档保留为**历史参考**，不再作为现行实施依据
- 当前现状、既有规范与已落地能力，仍以 `docs/ARCHITECTURE.md`、`frontend/src/styles/README.md` 及实际代码为准

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
- [x] 再迁移 `system/config`（`system/role`、`system/menu`、`system/dict` 已完成）

**评估结论（2026-04）**

- `components/CURD` 继续作为历史页面兼容层保留，不作为新一轮 Pro 抽象基座
- 新增或重构页面统一使用 `ProSearch` / `ProTable` / `ProFormDrawer`，不再新增 `CURD` 调用点

**收口结果（2026-04-14）**

- 系统管理域列表页已统一为 `ProTable(request)` 驱动
- 页面层表单弹层统一为 `ProFormDrawer`
- 页面层详情/非表单弹层统一为 `ProDialog` / `ProDrawer`
- 已新增测试守卫，禁止在 `src/views` 回归到原生 `el-dialog` / `el-drawer`

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
- `frontend/src/views/system/config/index.vue`

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
