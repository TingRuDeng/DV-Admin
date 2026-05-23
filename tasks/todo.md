# project-context-bootstrap 上下文文档升级

- [x] 确认当前仓库已有旧文档体系，采用升级模式而不是重建模式
- [x] 核对项目技术栈，确认当前仓库不是 Android 项目，使用 generic profile
- [x] 升级核心上下文文档入口和 AI 短上下文地图
- [x] 升级上下文包校验脚本
- [x] 运行校验并修复失败项
- [x] 完成交付前审查

## Review 小结

终态：finished。已按升级模式保留旧文档主体，补齐上下文包契约；`python3 scripts/validate_docs.py . --profile generic` 与 `python3 -m py_compile scripts/validate_docs.py` 均通过。

---

# P3 前端直接 console 收口

- [x] 新增全量直接 `console.*` 治理测试，并先确认当前代码会失败
- [x] 为剩余 SFC/组件引入 `createLogger` 并替换直接 `console.warn/error`
- [x] 运行目标测试，确认治理测试由红转绿
- [x] 运行前端质量、构建、smoke 和文档校验
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P3 已将生产前端源码剩余直接 `console.*` 收口到 `createLogger`，并新增 `direct-console-governance` 守卫测试；前端质量、生产构建、登录 smoke、文档校验和 diff 检查均通过。

---

# P4 Token 刷新类型收口

- [x] 新增 `useTokenRefresh` 类型治理测试，并确认当前代码会失败
- [x] 将 `httpRequest` 注入点改为最小函数接口，返回值使用 `unknown`
- [x] 保持已有 Token 刷新行为测试通过
- [x] 运行前端类型检查、目标单测和文档校验
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P4 已将 `useTokenRefresh.ts` 的 P2 遗留 `any` 类型边界收口为最小函数接口和 `unknown`，并新增类型治理守卫测试；目标测试、原行为测试、前端质量聚合、文档校验和 diff 检查均通过。

---

# P5 API 请求泛型收口

- [x] 新增 API 请求泛型治理测试，并确认当前代码会失败
- [x] 将 `frontend/src/api` 的 `request<any, T>` 改为 `request<unknown, T>`
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P5 已将 API 层 `request<any, T>` 收口为 `request<unknown, T>`，并新增 API 请求泛型治理守卫测试；目标测试、前端类型检查、前端质量聚合、文档校验和 diff 检查均通过。

---

# P6 Storage 类型边界收口

- [x] 新增 `storage.ts` 类型治理测试，并确认当前代码会失败
- [x] 将 `Storage.set` 和 `Storage.sessionSet` 的 `value` 参数改为 `unknown`
- [x] 保持现有存储行为测试通过
- [x] 运行前端类型检查、前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P6 已将 `Storage.set/sessionSet` 写入参数从 `any` 收口为 `unknown`，并新增 Storage 类型治理守卫测试；目标测试、原有存储行为测试、前端类型检查、前端质量聚合、文档校验和 diff 检查均通过。

---

# P7 WebSocket 定时器类型收口

- [x] 新增 WebSocket 定时器类型治理测试，并确认当前代码会失败
- [x] 将 WebSocket 组合式函数定时器句柄改为显式类型
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P7 已将 WebSocket 组合式函数中的定时器句柄从 `any` 收口为 `ReturnType<typeof setTimeout> | undefined`，并新增定时器类型治理守卫测试；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# P8 WebSocket 实例注册表类型收口

- [x] 新增 WebSocket 实例注册表类型治理测试，并确认当前代码会失败
- [x] 为 WebSocket 注册表定义最小实例接口
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P8 已将 WebSocket 插件实例注册表从 `Map<string, any>` 收口为最小生命周期接口，并新增实例注册表类型治理守卫测试；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# P9 全局路由类型边界收口

- [x] 新增全局路由/API 类型治理测试，并确认当前代码会失败
- [x] 将 `ApiResponse` 默认 payload、`TagView.query` 和 `translateRouteTitle` 参数改为显式类型
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P9 已将 `ApiResponse` 默认 payload 收口为 `unknown`，将 `TagView.query` 对齐为 `LocationQuery`，并将 `translateRouteTitle` 参数改为可选字符串；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# P10 API 扩展字段类型收口

- [x] 新增 API 扩展字段类型治理测试，并确认当前代码会失败
- [x] 将目标 API 类型的扩展字段索引签名改为 `unknown`
- [x] 运行目标测试和前端类型检查
- [x] 运行前端质量、文档校验和 diff 检查
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P10 已将字典项和测试模块 API 类型中的扩展字段索引签名从 `any` 收口为 `unknown`，并新增 API 扩展字段类型治理守卫测试；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# P11 标签页返回值类型收口

- [x] 新增标签页类型治理测试，并确认当前代码会失败
- [x] 为标签页关闭结果定义显式返回值类型
- [x] 移除 TagsView 回调结果和旧滚轮事件访问中的 `any`
- [x] 运行目标测试、前端类型检查、质量聚合、文档校验、diff 检查和生产构建
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P11 已将 `TagsView` 与 `tags-view-store` 的标签关闭返回值类型收口为显式结构，并用旧版滚轮事件最小类型替代 `as any`；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# P12 设置面板类型边界收口

- [x] 新增设置类型治理测试，并确认当前代码会失败
- [x] 为设置仓库映射和侧边栏配色定义显式类型
- [x] 移除 Settings 面板和 settings-store 中的 `any`
- [x] 运行目标测试、前端类型检查、质量聚合、文档校验、diff 检查和生产构建
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P12 已将 `settings-store` 的设置项映射收口为按 key 关联的显式类型，并将设置面板侧边栏配色事件收口到 `AppSettings["sidebarColorScheme"]`；红绿测试、前端类型检查、前端质量聚合、文档校验、diff 检查和生产构建均通过。

---

# 前端超大组件拆分 P1：部门表单抽屉

- [x] P1 串行：分析部门管理页内联表单抽屉与既有拆分组件模式
- [x] P1 串行：抽出 `frontend/src/views/system/dept/components/DeptFormDrawer.vue`
- [x] P1 串行：让 `frontend/src/views/system/dept/index.vue` 只保留页面编排、查询和表格动作
- [x] P2 串行：运行目标测试、前端类型检查和质量门禁
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将部门管理页内联表单抽屉抽为 `DeptFormDrawer.vue`，页面本体从 301 行降到 270 行并继续保留查询、表格动作和提交编排；新增拆分守卫测试覆盖父页面不再内联 `ProFormDrawer`。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# P0-P3 产品化治理全量收口

- [x] 建立隔离分支并写入全量收口计划
- [x] P0：补齐共享 API 契约测试和 CI 入口
- [x] P1：补 store/router 直接测试并抽出 WebSocket 连接管理器
- [x] P1：收紧 Django Ruff 与 FastAPI mypy 门禁
- [x] P2：补 Django request id、健康检查、前端可访问性和性能 smoke
- [x] P3：补 API 契约校验、双后端策略文档和技术债清理
- [x] 运行完整验证矩阵
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P0-P3 全量收口完成；文档/API 契约校验、前端 quality/build/e2e smoke、Django ruff/pytest、FastAPI make quality/mypy app 和 diff 检查均通过。

---

# 项目深度审查 P0/P1 修复

- [x] P0 串行：补 FastAPI 文件接口鉴权、上传大小和类型边界测试
- [x] P0 串行：实现 FastAPI 文件接口鉴权、大小和类型边界
- [x] P1 串行：补 FastAPI 敏感请求日志排除路径测试
- [x] P1 串行：修正 FastAPI 敏感请求日志排除路径
- [x] P1 串行：补共享路由契约测试覆盖用户重置密码、角色菜单、头像路径
- [x] P1 串行：对齐 Django/FastAPI/前端/文档共享路由契约
- [x] P1 并行可验证：补前端权限空状态、refresh token 请求体、通知默认值测试
- [x] P1 串行：实现前端权限空状态、refresh token 请求体、通知默认值修复
- [x] P2 串行：拆分前端只读质量门禁并同步 CI/文档
- [x] P2 串行：更新治理文档中过期门禁和 Playwright 陷阱描述
- [x] P3 串行：运行最小充分验证并执行 review-gate

## Review 小结

终态：finished。已完成项目深度审查 P0/P1 修复与 P2 门禁收口：FastAPI 文件上传/删除鉴权、上传大小和类型校验、敏感请求日志排除、共享路由契约、前端 refresh token 请求体、权限空状态和通知默认值均有测试覆盖；前端质量门禁改为只读检查并同步文档。验证通过：前端 quality/build、Django ruff/pytest、FastAPI make quality、共享路由契约测试、文档校验、API 契约校验和 diff 检查。

---

# 项目深度审查剩余后端修复

- [x] P1 串行：修正 Django 重置密码测试，覆盖真实 `PUT /password/reset/` 成功语义
- [x] P1 串行：收口 FastAPI 日志/通知服务 naive datetime warning
- [x] P2 串行：修正 Redis cache 错误分支测试中的 unawaited coroutine warning
- [x] P2 串行：隔离请求日志中间件实例级排除路径配置
- [x] P3 串行：运行 Django/FastAPI 最小充分验证与 review-gate

## Review 小结

终态：finished。已完成剩余高价值后端修复：Django 重置密码测试不再允许旧路由 404 混过；FastAPI 日志和通知时间写入统一为 UTC aware；Redis cache 错误分支测试不再产生未等待 coroutine；请求日志中间件自定义排除路径不再污染其他实例。验证通过：Django ruff/pytest、FastAPI make quality、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：用户表单抽屉

- [x] P1 串行：新增用户页拆分守卫测试，先确认当前代码仍内联 `ProFormDrawer`
- [x] P1 串行：抽出 `frontend/src/views/system/user/components/UserFormDrawer.vue`
- [x] P1 串行：让 `frontend/src/views/system/user/index.vue` 只保留页面编排、查询、表格动作和导入入口
- [x] P2 串行：运行目标测试、前端类型检查和质量门禁
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将用户管理页的表单抽屉抽为 `UserFormDrawer.vue`，页面本体降到 300 行以内并继续保留查询、表格动作和导入入口；新增拆分守卫测试先红后绿。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：角色表单与权限抽屉

- [x] P1 串行：新增角色页拆分守卫测试，先确认当前代码仍内联 `ProFormDrawer` 和 `ProDrawer`
- [x] P1 串行：抽出 `frontend/src/views/system/role/components/RoleFormDrawer.vue`
- [x] P1 串行：抽出 `frontend/src/views/system/role/components/RolePermissionDrawer.vue`
- [x] P1 串行：让 `frontend/src/views/system/role/index.vue` 只保留页面编排、查询、表格动作和删除入口
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将角色管理页的角色表单和权限分配抽屉分别抽为 `RoleFormDrawer.vue` 与 `RolePermissionDrawer.vue`，页面本体降到 207 行并保留查询、表格动作和删除编排；新增拆分守卫测试先红后绿。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：通知表单与详情弹窗

- [x] P1 串行：新增通知页拆分守卫测试，先确认当前代码仍内联 `ProFormDrawer`
- [x] P1 串行：抽出 `frontend/src/views/system/notice/components/NoticeFormDrawer.vue`
- [x] P1 串行：抽出 `frontend/src/views/system/notice/components/NoticeDetailDialog.vue`
- [x] P1 串行：同步通知默认值和富文本安全守卫测试到新组件边界
- [x] P1 串行：让 `frontend/src/views/system/notice/index.vue` 只保留查询、表格动作、发布/撤回/删除编排
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将通知管理页的通知表单和详情弹窗分别抽为 `NoticeFormDrawer.vue` 与 `NoticeDetailDialog.vue`，页面本体降到 291 行并继续保留查询、表格动作、发布/撤回/删除编排；同步默认值和富文本安全守卫测试到新组件边界。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：菜单表单抽屉

- [x] P1 串行：新增菜单页拆分守卫测试，先确认当前代码仍内联 `ProFormDrawer`
- [x] P1 串行：抽出 `frontend/src/views/system/menu/components/MenuFormDrawer.vue`
- [x] P1 串行：抽出 `frontend/src/views/system/menu/components/MenuRouteFields.vue`
- [x] P1 串行：抽出 `frontend/src/views/system/menu/components/MenuRouteParamsEditor.vue`
- [x] P1 串行：让 `frontend/src/views/system/menu/index.vue` 只保留查询、表格动作、删除和刷新编排
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将菜单管理页的菜单表单抽屉、路由字段和路由参数编辑器分别抽为 `MenuFormDrawer.vue`、`MenuRouteFields.vue` 与 `MenuRouteParamsEditor.vue`，页面本体降到 214 行并保留查询、表格动作、删除和刷新编排；新增拆分守卫测试先红后绿。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：字典表单抽屉

- [x] P1 串行：新增字典页和字典项页拆分守卫测试，确认父页面不再内联 `ProFormDrawer`
- [x] P1 串行：抽出 `frontend/src/views/system/dict/components/DictFormDrawer.vue`
- [x] P1 串行：抽出 `frontend/src/views/system/dict/components/DictItemFormDrawer.vue`
- [x] P1 串行：让 `frontend/src/views/system/dict/index.vue` 和 `frontend/src/views/system/dict/dict-item.vue` 只保留查询、表格动作、删除和跳转编排
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将字典管理页和字典项管理页的表单抽屉分别抽为 `DictFormDrawer.vue` 与 `DictItemFormDrawer.vue`，页面本体降到 207 行和 197 行；字典项新增入口在抽屉组件边界将数字字典 ID 显式转为表单契约需要的字符串。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：设置面板区块

- [x] P1 串行：补充设置面板拆分守卫测试，确保 `index.vue` 只做抽屉编排
- [x] P1 串行：抽出 `ThemeSection.vue`、`InterfaceSection.vue`、`LayoutSection.vue` 和 `SettingsActions.vue`
- [x] P1 串行：将设置面板共享类型收口到 `frontend/src/layouts/components/Settings/types.ts`
- [x] P1 串行：迁移原有区块样式到对应子组件，保留父组件抽屉壳样式
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将设置面板从单文件 593 行拆为父级抽屉编排和 4 个职责明确的子组件，父组件降到 157 行；重置后通过子组件公开的 `syncLocalState` 同步本地主题/侧边栏选择状态。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：TagsView 标签页组件

- [x] P1 串行：补充 TagsView 拆分守卫测试，确保 `index.vue` 只做标签页编排
- [x] P1 串行：抽出 `TagItem.vue`，封装单个标签渲染、翻译和事件出口
- [x] P1 串行：抽出 `TagsContextMenu.vue`，封装右键菜单 UI 和菜单事件出口
- [x] P1 串行：抽出 `useAffixTags.ts` 和 `useTagsContextMenu.ts`，收口固定标签提取和右键菜单状态管理
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将 TagsView 从 549 行拆为父级路由/store 编排、标签项、右键菜单和两个组合式函数，父组件降到 293 行；标签关闭、刷新、左右/其他/全部关闭和滚轮横向滚动逻辑保持原行为。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：菜单搜索组件

- [x] P1 串行：补充 MenuSearch 拆分守卫测试，确保 `index.vue` 只做弹窗和搜索编排
- [x] P1 串行：抽出 `MenuSearchHistory.vue`，封装搜索历史列表和清理事件出口
- [x] P1 串行：抽出 `MenuSearchResultList.vue`，封装搜索结果列表、图标和选中态
- [x] P1 串行：抽出 `MenuSearchFooter.vue`，封装底部快捷键提示和样式
- [x] P1 串行：抽出 `menu-search-routes.ts` 和 `useMenuSearchHistory.ts`，收口路由扁平化和历史存储逻辑
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将 MenuSearch 从 526 行拆为父级弹窗/搜索编排、搜索历史、结果列表、底部快捷键提示、路由扁平化工具和历史存储组合式函数，父组件降到 195 行；Ctrl+K、上下键选择、搜索历史、外链打开和路由跳转行为保持原逻辑。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：文本滚动组件

- [x] P1 串行：补充 TextScroll 拆分守卫测试，确保 `index.vue` 只保留渲染和关闭入口
- [x] P1 串行：抽出 `frontend/src/components/TextScroll/types.ts`，收口组件 props 类型
- [x] P1 串行：抽出 `frontend/src/components/TextScroll/useTextScroll.ts`，收口 hover、滚动时长、打字机和 HTML 净化逻辑
- [x] P1 串行：让 `frontend/src/components/TextScroll/index.vue` 保留模板、样式和关闭按钮事件
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将 TextScroll 从 415 行拆为渲染组件、props 类型和滚动/打字机组合式函数，父组件降到 270 行；保留原有滚动、悬停暂停、HTML 净化、打字机和关闭按钮行为。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。

---

# 前端超大组件拆分 P1：个人中心页面

- [x] P1 串行：更新 profile 拆分守卫测试，确保 `index.vue` 只做页面和 API 编排
- [x] P1 串行：抽出 `ProfileSidebar.vue`，封装头像、昵称、角色和文件选择入口
- [x] P1 串行：抽出 `ProfileInfoPanel.vue` 和 `ProfileSecurityPanel.vue`，封装账号信息和安全设置展示
- [x] P1 串行：抽出 `ProfileEditDialog.vue` 和 `types.ts`，封装账号资料和密码表单弹窗
- [x] P1 串行：删除已注释的手机/邮箱绑定旧代码和无效 timer/ref
- [x] P2 串行：运行目标测试、前端类型检查、质量门禁和生产构建
- [x] P3 串行：运行文档/API 契约校验、diff 检查和 review-gate

## Review 小结

终态：finished。已将个人中心页面从 421 行拆为父级页面编排、头像侧栏、账号信息、安全设置和账号/密码弹窗组件，父组件降到 147 行；删除已注释的手机/邮箱绑定旧代码和无效 timer/ref。验证通过：目标测试、前端 type-check、前端 quality、前端 build、文档校验、API 契约校验和 diff 检查。
