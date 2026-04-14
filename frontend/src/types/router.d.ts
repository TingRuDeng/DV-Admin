import "vue-router";

declare module "vue-router" {
  type RouteLayout = "left" | "top" | "mix";

  // https://router.vuejs.org/zh/guide/advanced/meta.html#typescript
  // 可以通过扩展 RouteMeta 接口来输入 meta 字段
  interface RouteMeta {
    /**
     * 菜单名称
     * @example 'Dashboard'
     */
    title?: string;

    /**
     * 菜单图标
     * @example 'el-icon-edit'
     */
    icon?: string;

    /**
     * 是否隐藏菜单
     * true 隐藏, false 显示
     * @default false
     */
    hidden?: boolean;

    /**
     * 始终显示父级菜单，即使只有一个子菜单
     * true 显示父级菜单, false 隐藏父级菜单，显示唯一子节点
     * @default false
     */
    alwaysShow?: boolean;

    /**
     * 是否固定在页签上
     * true 固定, false 不固定
     * @default false
     */
    affix?: boolean;

    /**
     * 是否缓存页面
     * true 缓存, false 不缓存
     * @default false
     */
    keepAlive?: boolean;

    /**
     * 是否在面包屑导航中隐藏
     * true 隐藏, false 显示
     * @default false
     */
    breadcrumb?: boolean;

    /**
     * 指定当前路由激活的菜单项
     * 典型场景为详情页、隐藏页、高级编辑页
     */
    activeMenu?: string;

    /**
     * 稳定的页面缓存键
     */
    cacheKey?: string;

    /**
     * 是否按 query 维度区分缓存实例
     * @default false
     */
    cacheByQuery?: boolean;

    /**
     * 仅按指定 query 键区分缓存实例（优先于 cacheByQuery）
     * @example ['tab', 'mode']
     */
    cacheQueryKeys?: string[];

    /**
     * 路由级权限标识（页面访问语义）
     * 按钮级权限请使用 v-hasPerm
     */
    perms?: string[];

    /**
     * 路由级角色标识（页面访问语义）
     * 角色按钮控制请使用 v-hasRole
     */
    roles?: string[];

    /**
     * 路由级布局覆盖
     */
    layout?: RouteLayout;

    /**
     * 附加路由参数
     */
    params?: Record<string, unknown>;
  }
}
