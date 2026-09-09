# DV-Admin 沉浸式首屏与壳层视觉重构设计

## 目标

在不改变 Django/FastAPI API 契约和业务数据流的前提下，重构登录页、登录后全局壳层和首页仪表盘。视觉方向采用“暗色画布 + 荧光珊瑚色”，所有新增和重构后的图标统一使用 Lucide，界面删除表情符号与装饰性空白文案。

## 视觉系统

- 页面以深墨蓝黑为底，叠加低对比网格、边缘光晕和细分隔线。
- 主色使用荧光珊瑚橙，辅助色使用冰蓝，正文使用高对比冷白；亮色主题保持同一色相关系。
- 动效只包含入场错峰、悬浮位移和点击回弹，并在 `prefers-reduced-motion` 下关闭。
- `lucide-vue-next` 作为壳层、登录页和首页的图标来源，移除这些范围内的 `i-svg:*`、手绘 SVG 和表情符号。

## 组件边界

- `frontend/src/views/dashboard/index.vue` 只负责读取用户和权限数据、组装页面。
- `frontend/src/views/dashboard/components/DashboardHero.vue` 负责欢迎信息、当前时间和视觉背景。
- `frontend/src/views/dashboard/components/DashboardMetricCard.vue` 负责单个真实指标。
- `frontend/src/views/dashboard/components/DashboardQuickActions.vue` 负责可访问路由快捷入口，并通过事件触发跳转。
- `frontend/src/components/AppIcon/index.vue` 负责 Lucide 图标名到组件的映射，供 Logo、菜单、登录表单和壳层操作复用。
- `AppLogo`、`NavBar`、`MenuItemContent` 使用 `AppIcon`；业务内页继续使用现有 API 和数据流。

## 信息与交互

- 登录页使用“左侧品牌画布 + 右侧聚焦表单”，仅保留登录所需字段和必要反馈。
- 首页展示用户身份、权限范围和可访问模块，移除文档/视频外链、Github 角标和无操作价值的装饰区域。
- 快捷入口从真实可访问路由生成；无入口时使用简洁空状态。
- 导航和登录操作保留键盘焦点、可读 `aria-label` 和 reduced-motion 降级。

## 数据流

用户信息来自现有 `useUserStore`，可访问菜单来自现有 `useLayoutMenu`/权限路由，页面只做派生计算。子组件通过 props 接收数据，通过 emits 请求跳转；不新增全局状态或后端接口。

## 验证

实现完成后执行 dashboard/style governance 单测、`type-check`、`lint:check` 和生产构建。验证结果分别报告，未执行或受环境阻断的检查单独列出。
