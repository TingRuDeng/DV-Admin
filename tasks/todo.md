# 当前任务状态

> 本文件只记录当前活跃任务和已完成任务摘要。已完成的详细执行计划不再长期保留，必要时从 Git 历史或对应 PR 查看。

## 活跃任务

- [ ] 待选择：下一轮长期可持续性治理目标。

## 最近完成

- [x] User 状态标签组件抽取已通过 PR #293 合并：用户启用状态标签文案、类型和样式类映射已抽入 `UserStatusTag.vue`，`user/index.vue` 从 290 行降至 285 行，User 页面治理测试新增状态组件守卫和行数守卫；本轮不改变用户查询参数、表格请求、重置密码、删除用户、导入弹窗、表单抽屉或后端 API，合并提交为 `732d84a`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Notice 状态标签组件抽取已通过 PR #291 合并：通知目标类型和发布状态标签文案、类型和样式类映射已抽入 `NoticeStatusTag.vue`，`notice/index.vue` 从 291 行降至 254 行，Notice 页面治理测试新增状态组件守卫和行数守卫；本轮不改变通知查询参数、表格请求、发布/撤回/删除动作、表单抽屉、详情弹窗或后端 API，合并提交为 `a5d488c`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] TagsView 路由标签同步抽取已通过 PR #289 合并：固定标签初始化、当前路由标签添加和当前标签 fullPath/query 更新已抽入 `useTagsRouteSync.ts`，`TagsView/index.vue` 从 293 行降至 216 行，TagsView 类型治理测试新增 composable 扫描和行数守卫；本轮不改变标签项 UI、右键菜单 UI、TagsView store API、缓存键规则或后端 API，合并提交为 `95d3922`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Login 死模板清理已通过 PR #287 合并：删除已注释的记住我/注册/第三方登录模板、注释导入和未使用样式，`Login.vue` 从 294 行降至 229 行，登录表单规则治理测试新增行数守卫；本轮不改变登录提交、验证码刷新、默认凭据、路由跳转、注册/重置密码组件或后端 API，合并提交为 `a355f08`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Stomp 连接计时器抽取已通过 PR #285 合并：重连计时器与连接超时计时器管理已抽入 `stomp-connection-timers.ts`，`stomp-connection-manager.ts` 从 299 行降至 290 行，WebSocket 定时器治理测试已覆盖新 helper 并新增 manager 行数守卫；本轮不改变 STOMP 客户端创建、订阅注册表、重连策略计算、认证错误处理或公开 API，合并提交为 `a2ed762`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageModal 静态组件映射表抽取已通过 PR #283 合并：`componentMap` 与 `childrenMap` 已抽入 `pageModalComponentMaps.ts`，`PageModal.vue` 从 300 行降至 245 行，组件映射治理测试已覆盖新 helper 并新增 PageModal 行数守卫；本轮不改变表单模板结构、弹窗/抽屉行为、slot 协议、`defineExpose()` 公开 API 或后端 API，合并提交为 `9f895d3`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] 生产源码 any 扫描注释噪音清理已通过 PR #281 合并：删除 `dict-api.ts` 中废弃的注释接口片段，调整 `uploadError.ts` 注释文案，生产源码 `any/@ts-ignore/@ts-expect-error` 扫描已无命中；本轮不改变字典 API 类型、上传错误处理逻辑、运行时行为或后端 API，合并提交为 `138e5ac`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] demo icons 图标代码生成类型边界收紧已通过 PR #279 合并：`demo/icons.vue` 的 `generateIconCode` 与 `generateElementIconCode` 参数已从显式 `any` 收紧为 `string`，SVG 图标列表改为只读字面量数组，新增 demo icons 类型治理测试防止函数参数回退；本轮不改变图标资源加载、Element Plus 图标注册、页面布局或后端 API，合并提交为 `f1b0f3d`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Breadcrumb 路由项类型边界收紧已通过 PR #277 合并：面包屑本地路由项已用 `BreadcrumbRoute` 显式表达 `path/name/meta/redirect` 字段，dashboard fallback 移除 `as any`，`handleLink(item: any)` 收紧为明确类型并兼容 redirect 函数形式，新增 Breadcrumb 类型治理测试防止显式 any 回退；本轮不改变路由生成、权限路由、面包屑 UI 样式或后端 API，合并提交为 `ef22654`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Notification 订阅消息类型边界收紧已通过 PR #275 合并：订阅回调参数已从 `message: any` 收紧为 STOMP `IMessage`，`JSON.parse` 结果按 `unknown` 处理并在组件边界校验通知消息字段，通知发布时间类型对齐为 `string | Date`，新增 Notification 消息类型治理测试防止回退；本轮不改变 WebSocket 连接管理器、通知 API 路径、通知详情弹窗或后端 API，合并提交为 `57db919`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] WangEditor 编辑器实例与上传配置类型边界收紧已通过 PR #273 合并：编辑器实例已从隐式 `any` 收紧为 `IDomEditor`，上传图片配置改用 `IUploadConfig` 与本地 `UploadImageConfig` 明确表达 `base64LimitSize`，移除 `uploadImage` 配置 `as any` 与 `handleCreated(editor: any)`，新增 WangEditor 类型治理测试防止回退；本轮不改变上传 API、富文本内容模型、通知表单、demo 页面或后端 API，合并提交为 `2f45eda`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] IconSelect 标签页事件类型边界收紧已通过 PR #271 合并：`IconSelect` 的 `handleTabClick(tabPane: any)` 已收紧为 Element Plus `TabsPaneContext`，`activeTab` 收紧为 `TabPaneName`，标签页缺少 `name` 时显式抛错，新增 IconSelect 类型治理测试防止标签页事件类型回退；本轮不改变图标加载、搜索逻辑、图标命名规则、CURD 表单组件映射或后端 API，合并提交为 `2e4ec6e`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] AppLink 跳转目标类型边界收紧已通过 PR #269 合并：`AppLink` 新增 `AppLinkTo` 显式表达当前 `{ path, query }` 跳转对象结构，外链和内部路由 props 构建结果收紧为明确联合类型，移除 `linkProps(to: any)`，新增 AppLink 类型治理测试防止跳转目标回退到显式 `any`；本轮不改变菜单路径拼接、外链判断、`router-link` 透传语义或后端 API，合并提交为 `c648728`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Dict 字典值类型边界收紧已通过 PR #267 合并：新增 `DictValue` / `DictModelValue` 共享类型，`Dict/index.vue` 的选择值、复选值和 change 事件已移除显式 `any`，`DictLabel.vue` 的标签查询值已收紧为 `DictValue`，新增字典值类型治理测试防止 `ref<any>`、`handleChange(val: any)` 和 `value: any` 回流；本轮不改变字典接口、字典缓存、字典项数据结构、select/radio/checkbox 的 `v-model` 对外语义或后端 API，合并提交为 `b5bcd81`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] 上传组件错误回调类型边界收紧已通过 PR #265 合并：`SingleImageUpload`、`FileUpload`、`MultiImageUpload` 的上传失败回调参数已从显式 `any` 收紧为 `unknown`，新增 `uploadError` helper 在窄化后读取未知错误的 `message`，并新增上传错误类型治理测试防止 `error: any` 回流；本轮不改变上传请求、删除请求、文件列表结构、错误提示语义或后端 API，合并提交为 `19852f8`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] OperationColumn DOM 测量类型边界收紧已通过 PR #263 合并：`getOperationMaxWidth()` 已移除 `totalWidth: any` 与 `button: any`，按钮 DOM 查询收紧为 `querySelectorAll<HTMLElement>(".el-button")`，新增 OperationColumn 类型治理测试防止显式 `any` 回流；本轮不改变表格操作列渲染、插槽协议、按钮间距、最终宽度计算或后端 API，合并提交为 `efad8ed`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] InputTag 配置属性类型边界收紧已通过 PR #261 合并：`InputTag` 的 `buttonAttrs/inputAttrs/tagAttrs` 已从 `Record<string, any>` 收紧为 Element Plus `ButtonProps/InputProps/TagProps`，保留 `buttonAttrs.btnText` 自定义按钮文本能力，新增配置属性类型治理测试防止显式 `any` 回流；本轮不改变标签新增、删除、滚动容器、CURD 调用方式或后端 API，合并提交为 `82d08b2`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] 登录表单规则类型边界收紧已通过 PR #259 合并：`Login.vue` 和 `Register.vue` 的表单规则已从 `Partial<Record<string, any>>` 收紧为 Element Plus `FormRules`，确认密码 validator 改为 `unknown` 值窄化，新增登录表单规则类型治理测试防止显式 `any` 回流；本轮不改变登录、注册、验证码、路由跳转或后端认证 API，合并提交为 `f7d6c37`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] CURD 通用对象类型边界收紧已通过 PR #257 合并：`IObject` 已从 `Record<string, any>` 收紧为 `Record<string, unknown>`，表格单元格、搜索表单、筛选和表格操作读取点已改为局部窄化，新增通用对象类型治理测试防止回退；本轮不改变 CURD 渲染、请求、分页、筛选、导入导出或后端 API，合并提交为 `925a5d5`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] CURD 表格列扩展类型边界收紧已通过 PR #255 合并：`IContentConfig.cols` 的扩展索引已从 `[key: string]: any` 收紧为 `ICurdTableColumnExtraValue = unknown`，新增表格列扩展类型治理测试防止回退；本轮不改变 PageContent 渲染、分页、筛选、导入导出或后端 API，合并提交为 `3c2bd07`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] CURD 表单 API 类型边界收紧已通过 PR #253 合并：`PageModal.vue` 的 `defineSlots` 与 `setFormItemData` 已改为共享表单 API 类型，`IFormItems` 的 `options`、`initialValue`、`events` 已移除显式 `any`，新增表单 API 类型治理测试防止回退；本轮不改变弹窗、抽屉、表单初始化、校验或提交行为，合并提交为 `7050705`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] CURD 组件映射类型边界收紧已通过 PR #251 合并：`PageSearch.vue` 和 `PageModal.vue` 的动态组件映射已改为共享 `ICurdComponentMap` / `ICurdComponentMapValue` 类型，显式导入 Element Plus 组件并移除映射处的 `Map<..., any>` 与 `@ts-ignore`；新增组件映射类型治理测试防止回退，合并提交为 `67a4ac5`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] CURD 数据请求与解析类型边界收紧已通过 PR #249 合并：`IContentConfig` 新增响应泛型，数据请求、解析、导出文件响应、导入导出和表单提交 action 已从可控的 `Promise<any>` 收敛为明确响应或 `unknown`；`usePageContentData.applyPageData` 移除显式 `any`，新增类型治理测试防止数据 action 和 parser 回退，合并提交为 `ac9e5d6`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Django settings 配置构建职责拆分已通过 PR #247 合并：`backend/drf_admin/settings.py` 从 469 行降至 259 行，DRF、JWT、API 白名单、Redis 缓存、Channels 和日志配置构建已拆入 `settings_helpers.py`；环境变量名称、缓存别名、JWT 轮换策略、权限白名单、Channels Redis db 和日志文件名保持不变，新增 settings helper 单测覆盖 DRF/JWT、API 前缀、白名单、Redis/本地缓存、Channels 和日志配置，合并提交为 `9d72ed4`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 文件动作抽取已通过 PR #245 合并：`PageContent.vue` 从 345 行降至 223 行，导入导出弹窗状态、远程导出、本地导出、模板下载、单文件导入、批量 Excel 导入和公开 `exportPageData` 已拆入 `usePageContentFileActions.ts`；表格渲染、分页、筛选、表格操作、toolbar 分发、公开类型和 `defineExpose()` 保持不变，新增 composable 单测覆盖当前页导出、选中导出、远程导出、导入模板下载、单文件导入、批量导入空表、读取失败和公开后端导出，合并提交为 `87d60e5`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 表格操作状态抽取已通过 PR #243 合并：`PageContent.vue` 从 404 行降至 345 行，表格选择、批量删除 ID、删除确认、操作列分发和行内修改逻辑已拆入 `usePageContentTableActions.ts`；导入导出、分页、筛选、公开类型和 `defineExpose()` 保持不变，新增 composable 单测覆盖选择状态、批量删除、指定行删除、无删除配置、操作列透传、行内修改和未配置修改提示，合并提交为 `2c08ae4`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 远程筛选状态抽取已通过 PR #241 合并：`PageContent.vue` 从 423 行降至 404 行，筛选参数转换、`filterJoin` 拼接、`column-key` 兼容、筛选参数缓存和 `filterChange` 事件分发已拆入 `usePageContentFilters.ts`；导入导出、删除修改、数据分页、公开类型和 `defineExpose()` 保持不变，新增 composable 单测覆盖普通筛选、拼接筛选、兼容字段和增量合并，合并提交为 `9fd6c42`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 数据分页状态抽取已通过 PR #239 合并：`PageContent.vue` 从 486 行降至 423 行，`loading/pageData/pagination/lastFormData`、分页请求参数拼装、分页切换和数据响应写入已拆入 `usePageContentData.ts`；导入导出、删除修改、筛选事件、公开类型和 `defineExpose()` 保持不变，新增 composable 单测覆盖分页请求、非分页请求、parseData、页码重置和分页切换，合并提交为 `120c953`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent Excel 文件处理逻辑抽取已通过 PR #237 合并：`PageContent.vue` 从 534 行降至 486 行，Excel buffer 写入、Excel 文件读取、行解析和浏览器保存已拆入 `pageContentExcel.ts`；导入导出业务分支、提示文案、公开类型和 `defineExpose()` 保持不变，新增 helper 单测覆盖写入、解析、空表和读取失败，合并提交为 `63007a1`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 工具栏配置逻辑抽取已通过 PR #235 合并：`PageContent.vue` 从 606 行降至 534 行，默认按钮配置、权限标识组合、按钮权限判断和 toolbar/table toolbar 派生逻辑已拆入 `usePageContentToolbarConfig.ts`；顶部工具栏、表格操作列、业务动作分发、导入导出、公开类型和 `defineExpose()` 保持不变，合并提交为 `e70cec9`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 表格单元格组件拆分已通过 PR #233 合并：`PageContent.vue` 从 716 行降至 606 行，`image/list/url/switch/input/price/percent/icon/date/tool` 内置单元格渲染已拆入 `PageContentTableCell.vue`；列循环、自定义插槽、行内修改、操作按钮事件、分页、导入导出、公开类型和 `defineExpose()` 保持不变，合并提交为 `e1c7a55`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 导入弹窗组件拆分已通过 PR #231 合并：`PageContent.vue` 从 813 行降至 716 行，导入弹窗 UI、上传控件、本地表单状态、校验、关闭重置和提交事件已拆入 `PageContentImportDialog.vue`；模板下载、单文件导入、Excel 批量解析、分页刷新、导出弹窗、表格列渲染、公开类型和 `defineExpose()` 保持不变，合并提交为 `6009988`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 导出弹窗组件拆分已通过 PR #229 合并：`PageContent.vue` 从 901 行降至 813 行，导出弹窗 UI、导出表单本地状态、字段选择、数据源选择、校验和关闭重置已拆入 `PageContentExportDialog.vue`；ExcelJS 写入、远程导出、本地导出、文件保存、导入弹窗、分页、筛选、删除、表格列渲染、公开类型和 `defineExpose()` 保持不变，合并提交为 `66bf3a6`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] PageContent 工具栏组件拆分已通过 PR #227 合并：`PageContent.vue` 从 936 行降至 901 行，顶部左右工具栏和列筛选 popover 已拆入 `PageContentToolbar.vue`；数据获取、分页、筛选、导入导出、删除、编辑、表格列渲染、CURD 公开类型和兼容层弃用治理策略保持不变，合并提交为 `92f10cc`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI deps token helper 拆分已通过 PR #225 合并：`deps.py` 从 259 行降至 242 行，Authorization/Bearer token 提取、access token payload 校验和用户 ID 提取已拆入 `deps_tokens.py`；黑名单检查、用户批量撤销检查、数据库查询、request.state 写入、权限检查器和角色检查器保持不变，合并提交为 `03cedbc`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Token 黑名单记录 helper 拆分已通过 PR #223 合并：`token_blacklist.py` 从 292 行降至 272 行，Token 黑名单记录构造、用户撤销记录构造和时间比较已拆入 `token_blacklist_records.py`，内存存储兼容访问器已拆入 `token_blacklist_compat.py`；JWT 解码、Redis 连接、内存降级、认证依赖和公开服务 API 保持不变，合并提交为 `05290f4`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Django system 测试管理员用户 helper 抽取已通过 PR #221 合并：7 个 system 测试文件中的重复 `create_admin_user()` 已收敛到 `backend/drf_admin/apps/system/test_helpers.py`，共享 helper 为 60 行，相关测试文件均低于 300 行；Django 运行时代码、权限逻辑、模型、序列化器和 API 响应契约保持不变，合并提交为 `0ecc2f7`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] Django OAuth 接口测试拆分已通过 PR #219 合并：原 323 行 `tests.py` 已拆为 helper/login/refresh-token/session/home 五个职责文件，拆分后文件分别为 46、60、86、123、30 行，OAuth 运行时代码、URL、序列化器、模型和 API 响应契约保持不变；`backend/TESTING.md` 已同步为当前 pytest 测试入口，合并提交为 `b292fff`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI OAuth 接口测试拆分已通过 PR #217 合并：原 255 行 `test_oauth.py` 已拆为 login/captcha/session 三个职责测试文件，拆分后文件分别为 67、153、50 行，OAuth 运行时代码和登录、验证码、用户信息、菜单、登出接口契约保持不变，合并提交为 `faedf11`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 字典类型服务测试拆分已通过 PR #215 合并：原 251 行 `test_dict_service_dicts.py` 已拆为 query/mutation 两个职责测试文件，拆分后文件分别为 96、158 行，`dict_service` 运行时代码、字典类型 API、schema、数据库模型和前端调用保持不变，合并提交为 `e1f1575`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 字典项服务嵌套接口测试拆分已通过 PR #213 合并：原 257 行 `test_dict_service_items.py` 已拆为 query/mutation 两个职责测试文件，拆分后文件分别为 97、167 行，`dict_service` 运行时代码、字典项 API、schema、数据库模型和前端调用保持不变，合并提交为 `f651d88`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Redis 缓存测试拆分已通过 PR #211 合并：原 268 行 `test_cache_redis.py` 已拆为连接/key、读写、删除/存在性/清理 3 个职责测试文件，拆分后文件分别为 42、141、109 行，`RedisCache` 运行时代码和缓存契约保持不变，合并提交为 `470b345`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 角色服务 helper 拆分已通过 PR #209 合并：`role_service.py` 已从 270 行降至 212 行，角色输出转换、更新字段构建和菜单输出转换已拆入 `role_serializers.py`，`RoleService` 公开方法、缓存清理和 RBAC 行为保持不变，合并提交为 `0e11f09`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI OAuth 用户访问逻辑拆分已通过 PR #207 合并：`oauth.py` 已从 274 行降至 169 行，用户权限查询、菜单查询和菜单树构建 helper 已拆入 `oauth_user_access.py`，`Users` 公开方法、OAuth 菜单接口和权限校验行为保持不变，合并提交为 `e53a0fc`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 验证码服务拆分已通过 PR #205 合并：`captcha_service.py` 已从 277 行降至 158 行，`CaptchaCache`、`MemoryCaptchaCache`、`RedisCaptchaCache` 已拆入 `captcha_cache.py`，服务入口、OAuth 验证码接口和登录验证码校验行为保持不变，合并提交为 `55f9f2a`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 用户写接口 OpenAPI 文案拆分已通过 PR #203 合并：`user_routes/mutation.py` 已从 286 行降至 91 行，长 description 和 responses 已拆入 `mutation_docs.py`，路由函数、权限声明、路径和响应契约保持不变，合并提交为 `36ca4bf`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Token 黑名单内存降级存储拆分已通过 PR #201 合并：`TokenBlacklistMemoryStore` 已承接内存黑名单和用户撤销标记状态，`token_blacklist.py` 当前为 292 行，新增 helper 测试覆盖过期清理、撤销判断和清理行为，合并提交为 `3a0051d`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Django 数据导入模块拆分已通过 PR #199 合并：`import_django_data.py` 已从 292 行降至 58 行，配置、状态、fixture 读取、写入转换和关系处理已拆入专用模块；模型契约校验已同步扫描 `django_import_config.py`，合并提交为 `ecf14a9`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 通知服务拆分已通过 PR #197 合并：`notice_service.py` 已从 292 行降至 225 行，时间辅助、输出转换和已读状态 helper 已拆入 `notice_time.py`、`notice_serializers.py`、`notice_read_helpers.py`，合并提交为 `9d79041`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 日志服务拆分已通过 PR #195 合并：`log_service.py` 已从 293 行降至 205 行，时间辅助、输出转换和访问统计聚合 helper 已拆入 `log_time.py`、`log_serializers.py`、`log_stats_helpers.py`，合并提交为 `fc9a33b`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Token 黑名单服务拆分已通过 PR #193 合并：`token_blacklist.py` 已从 302 行降至 288 行，Key 生成和内存过期清理 helper 已拆入 `token_blacklist_keys.py`，合并提交为 `e770406`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 健康检查测试拆分已通过 PR #191 合并：原 315 行 `test_health.py` 已拆为 endpoints、database、redis、readiness 4 个职责测试文件，合并提交为 `9316387`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Django 数据导入测试拆分已通过 PR #190 合并：原 327 行 `test_import_django_data.py` 已拆为 mapping、models、relations、helpers 4 个职责测试文件，合并提交为 `9ebc2ff`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 请求日志中间件拆分已通过 PR #189 合并：`logging_middleware.py` 已从 329 行收缩为 9 行兼容导出入口，合并提交为 `7440e9f`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 慢查询中间件拆分已通过 PR #188 合并：`slow_query_middleware.py` 已从 350 行收缩为 17 行兼容导出入口，合并提交为 `7b84942`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 日志 API 路由拆分已通过 PR #187 合并：`logs.py` 已从 353 行收缩为 9 行兼容路由入口，合并提交为 `def5421b`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 缓存核心模块拆分已通过 PR #186 合并：`cache.py` 已从 353 行收缩为 20 行兼容导出入口，合并提交为 `f6262dcc1262b1b95a7974880b9214db9a3d402d`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 通知服务测试拆分已通过 PR #185 合并：原 356 行 `test_notice_service.py` 已拆为后台查询、详情、写操作、发布状态、我的通知列表 5 个职责测试文件和 1 个共享 fixture，合并提交为 `aaec39124663d81e58b8b7d78465d220be996561`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 日志服务测试拆分已通过 PR #184 合并：原 363 行 `test_log_service.py` 已拆为时间辅助、分页查询、访问趋势、访问统计、删除与创建 5 个职责测试文件和 1 个共享 fixture，合并提交为 `c190563ccf30a02b4e4f82be4f33c2e7f2bd7a39`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI Token 黑名单测试拆分已通过 PR #183 合并：原 384 行 `test_token_blacklist.py` 已拆为 key/redis 属性、单 token 黑名单、用户批量撤销、删除清理、内存降级 5 个测试文件和 1 个共享 fixture，合并提交为 `aff0acf0b0445761fa91e124d836ea30023b12a1`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 角色服务测试拆分已通过 PR #182 合并：原 456 行 `test_role_service.py` 已拆为查询、写操作、删除、菜单权限 4 个职责测试文件和 1 个共享 fixture，合并提交为 `656fcd30334489ddf80dcdb316b3bccd25f2034d`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 缓存测试拆分已通过 PR #181 合并：原 521 行 `test_cache.py` 已拆为内存缓存、Redis 缓存、缓存服务和缓存键模板 4 个测试文件，合并提交为 `98ecc285429c43902f62ff4a960b74a1a2b086ea`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 用户服务测试拆分已通过 PR #180 合并：原 531 行 `test_user_service.py` 已拆为查询、写操作、删除密码、导入导出 4 个测试文件和 1 个共享 fixture，合并提交为 `59311739d1002ac57fab6e7c47015d58cd285a93`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 用户服务拆分已通过 PR #179 合并：`user_service.py` 已从 598 行收缩为 16 行兼容聚合入口，合并提交为 `bb3260d487df70388cb9af90f01364dd6834632a`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI OAuth API 拆分已通过 PR #178 合并：`auth.py` 已从 750 行收缩为 37 行兼容聚合入口，合并提交为 `5bd63c0fc37f84acee7b9c6d1597e97b80151f2f`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 用户 API 拆分已通过 PR #177 合并：`users.py` 已从 720 行收缩为 31 行兼容聚合入口，合并提交为 `21b824239e3f4cff96dde3a56fea390a405cbbe4`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 用户 API 拆分本地验证完成：`users.py` 已从 720 行收缩为 31 行兼容聚合入口，查询、写操作、密码重置、导入导出端点已拆入 `user_routes/`；用户目标测试 6 passed，FastAPI `make quality` 539 passed、覆盖率 85.08%，API 契约和文档校验均通过。
- [x] FastAPI system model 拆分已通过 PR #176 合并：`system.py` 已从 339 行收缩为 20 行兼容导出入口，合并提交为 `e9c8afae56d49909d505d6d5103fed117d4977a7`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI system model 拆分本地验证完成：`system.py` 已从 339 行收缩为 20 行兼容导出入口，权限角色、部门、通知、字典和日志模型已拆入独立模块；目标模型契约测试 33 passed，FastAPI `make quality` 539 passed、覆盖率 84.98%，文档校验和 diff 检查均通过。
- [x] FastAPI system schema 拆分已通过 PR #175 合并：`system.py` 已从 545 行收缩为 85 行兼容导出入口，合并提交为 `f715ce469e57565a67491653bc27a2922e0d36f8`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI system schema 拆分：`system.py` 已从 545 行收缩为 85 行兼容导出入口，用户、角色、通知、菜单、部门、字典、日志和通用 schema 已拆入独立模块；目标测试 52 passed，FastAPI `make quality` 539 passed、覆盖率 84.92%，文档校验和 diff 检查均通过。
- [x] FastAPI 字典服务拆分已通过 PR #174 合并：`dict_service.py` 已从 474 行收缩为 15 行聚合入口，合并提交为 `a795b42b299200e12ba993b0c0d2803e52b42c33`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 字典服务拆分：`dict_service.py` 已从 474 行收缩为 15 行聚合入口，字典缓存、字典类型、嵌套字典项、扁平字典项和共享 helper 已拆入独立服务模块；目标测试 49 passed，FastAPI `make quality` 539 passed、覆盖率 84.84%，文档校验和 diff 检查均通过。
- [x] FastAPI 字典服务测试拆分状态记录：PR #173 已合并，合并提交为 `5b477b6e9fd145212cfb83483279804ae9d965cc`，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。
- [x] FastAPI 字典服务测试拆分：原 728 行 `test_dict_service.py` 已拆为 3 个职责测试文件和 1 个共享 fixture，全部低于 300 行；PR #172 已合并，远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过。

## 已完成摘要

- [x] 项目上下文文档升级：补齐 `docs/README.md`、`docs/AI_CONTEXT.md` 与 `scripts/validate_docs.py` 校验入口。
- [x] 产品化治理 P0-P3：共享 API 契约、关键前端测试、WebSocket 管理器、后端门禁、request id/health、文档/API 契约校验已落地。
- [x] 前端类型治理 P4-P12：Token 刷新、API 请求泛型、Storage、WebSocket 定时器/注册表、全局路由/API、扩展字段、TagsView、Settings 类型边界已收口。
- [x] 深度审查 P0/P1：FastAPI 文件接口鉴权和上传边界、敏感日志排除、共享路由契约、前端权限空态、refresh token 请求体和通知默认值已修复。
- [x] 前端超大组件拆分：用户、角色、通知、菜单、字典、部门、设置、TagsView、MenuSearch、TextScroll、Profile、Dashboard、字典同步 demo 等拆分已合入。
- [x] 前端共享组件与测试收口：`tags-view-store` Promise resolve 边界、`TableSelect` 类型/行为测试、WebSocket STOMP helper、主题样式测试拆分和 CURD 兼容层复核已完成。

## Review 小结

本轮任务清单收口已完成：`活跃任务` 区只保留当前状态，最近完成的字典项排序字段治理迁入 `最近完成`，历史长列表不再占用活跃区。该变更只调整执行状态记录，不修改运行时代码、契约脚本或产品文档。

本轮修复审查优先级前四项：FastAPI RBAC 权限码已对齐前端/Django 种子契约；通用文件上传已拒绝 SVG；Django 开发态媒体路由已脱离 Swagger 开关；Playwright 本地 smoke 已改为固定端口、禁止复用已有服务，并忽略本地 HTML 报告。验证已覆盖文档/API 契约、FastAPI `make quality`、Django ruff + pytest、前端 `pnpm run quality`、`pnpm run build` 和 `VITE_APP_PORT=9530 pnpm run test:e2e:smoke`。

本轮小范围治理已完成：FastAPI 测试数据库、同步 ASGI 客户端、权限种子已从 `conftest.py` 拆入专用夹具文件；Django 历史测试权限码已统一为 `system:permissions:*`；后端验证通过。

本轮进入 FastAPI 依赖锁定治理：`fastapi/uv.lock` 此前被全局 Git ignore 忽略，导致本地和 CI 依赖解析可能漂移；本轮将锁文件纳入仓库并补充验证记录。

FastAPI 依赖锁定治理已完成：`.gitignore` 已显式允许 `fastapi/uv.lock`，锁文件已纳入仓库；`uv lock --check`、`uv sync --locked --group dev`、`make quality`、文档校验、脚本编译和 diff 检查均通过。

本轮文件上传 / 删除契约治理已完成：FastAPI 上传响应新增 `path` 并按 `files/{user_id}` 隔离保存；删除接口改为只接受上传返回的相对路径，并校验目录边界与用户归属；前端文件上传和多图上传删除时改传 `path`，缺少路径时显式提示；文件接口文档、契约校验和 Playwright 报告的 Prettier ignore 治理已同步。验证通过：FastAPI `make quality`（504 passed，覆盖率 81.23%）、前端 `pnpm run quality`（64 files / 165 tests）、前端 `pnpm run build`、文档/API 契约校验和 `git diff --check`。

本轮进入双后端关键端点契约治理：新增 `scripts/api_endpoint_contracts.py` 作为关键端点契约目录，覆盖认证、用户、菜单、字典、字典项和文件接口的路径、方法、权限、分页和关键字段；Django/FastAPI 契约测试已开始共同断言该目录，`scripts/validate_api_contracts.py` 会校验证据文件中的路径、权限和调用片段，避免契约目录脱离真实代码。

双后端关键端点契约治理第一轮已完成：文档校验、API 契约校验、脚本编译、Django/FastAPI 目标契约测试、ruff 和 `git diff --check` 均通过；本轮未启动后端服务做运行时双实现对比，后续如继续推进应以该目录为输入补运行时采样契约测试。

本轮进入 Django fixture 导入 fail-fast 治理：`fastapi/app/db/import_django_data.py` 原先在 fixture 缺失、单条导入失败、FK/M2M 失败时会打印后继续，存在误报成功风险；本轮新增 fail-fast 测试并把导入流程拆成小 helper，确保关键失败抛出 `DjangoDataImportError`。

Django fixture 导入 fail-fast 治理已完成：缺少 fixture、单条导入失败、M2M 目标缺失三类失败测试已覆盖；`make quality` 通过（505 passed，覆盖率 83.41%），文档校验、API 契约校验、脚本编译和 `git diff --check` 均通过。

本轮进入运行时 API 契约抽样治理：新增 FastAPI 运行时抽样测试，复用 `scripts/api_endpoint_contracts.py` 中的关键端点目录校验认证信息、动态路由、用户/菜单/字典/字典项分页和文件上传删除闭环；同时修正 FastAPI 用户、字典和字典项分页路由，使其真实接受前端契约参数 `pageSize`。目标验证通过：`python3 scripts/validate_api_contracts.py .` 和 `uv run pytest tests/test_runtime_api_contracts.py -q`。

本轮进入 Django fixture 导入 golden 测试治理：新增小型 golden fixture，覆盖部门自关联、权限菜单自关联、字典/字典项外键、角色权限 M2M、用户部门 FK 和用户角色 M2M，确保导入链路不只 fail-fast，也能长期验证完整映射结果。

Django fixture 导入 golden 测试治理已完成：`uv run pytest tests/test_import_django_data_golden.py tests/test_import_django_data.py tests/test_import_django_data_fail_fast.py -q` 通过（22 passed），FastAPI `make quality` 通过（511 passed，覆盖率 84.06%），文档/API 契约校验、脚本编译和 `git diff --check` 均通过。

本轮动态路由组件契约治理已完成：前端动态路由解析缺失组件时改为显式抛错，不再静默落到 404；新增 `scripts/validate_route_components.py` 校验 FastAPI 测试权限种子、golden fixture 和 Django 初始化数据中默认角色可访问菜单组件必须存在于 `frontend/src/views`；CI 质量门禁已接入该校验。验证通过：前端 `pnpm run quality`（64 files / 166 tests）、前端 `pnpm run build`、FastAPI `make quality`（511 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 默认密码配置治理已完成：`Settings.default_password` 已移除代码默认弱口令，`DEFAULT_PASSWORD` 必须由环境变量或 `.env` 显式提供；`.env.example` 改为非弱占位值，用户新增/重置密码接口说明和技术债统计已同步。验证通过：`uv run pytest tests/test_config.py -q`（15 passed）、FastAPI `make quality`（512 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django 运行时 API 契约抽样治理已完成：新增 Django 关键读端点运行时抽样，复用共享端点目录校验认证信息、动态路由、用户/菜单/字典/字典项分页响应；RED 阶段暴露 `dictCode` 未真实过滤字典项，已通过 `DictItemsFilter` 显式映射到 `dict__dict_code` 修复，并把 Django 运行时测试纳入 `scripts/validate_api_contracts.py` 必备入口。验证通过：Django 目标测试（10 passed）、Django `uv run ruff check .`、Django `uv run pytest`（83 passed）、FastAPI 契约对照测试（6 passed）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮前端错误响应边界治理已完成：新增 `normalizeApiErrorEnvelope` 统一错误信封，`request.ts` 改为只消费归一化后的错误结果；FastAPI 参数校验明细 `data.errors[].message` 已优先展示，避免只显示泛化错误；前端 API 契约测试和 `scripts/validate_api_contracts.py` 已纳入该入口。验证通过：前端目标测试（11 passed）、`pnpm run quality`（64 files / 168 tests）、`pnpm run build`、Django/FastAPI 契约目标测试（各 6 passed）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django/FastAPI 模型差异契约治理已完成：新增 `scripts/model_contracts.py` 集中声明 Django → FastAPI 模型、表名和字段映射；新增 `scripts/validate_model_contracts.py` 并纳入 CI 文档校验阶段；FastAPI 导入契约测试开始对照共享模型契约，权限菜单 `keepAlive/alwaysShow` 映射已显式补齐。验证通过：模型契约校验、FastAPI 导入目标测试（23 passed）、FastAPI `make quality`（513 passed，覆盖率 83.71%）、文档/API/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django RBAC 权限边界契约治理已完成：新增 `backend/drf_admin/utils/test_rbac_permission_contract.py`，直接覆盖 `RBACPermission` 有权限放行、缺权限拒绝、无权限声明拒绝、白名单放行，并校验 `UsersViewSet` 自动生成的用户写操作权限码与共享端点契约一致。验证通过：目标测试（5 passed）、Django `uv run ruff check .`、Django `uv run pytest`（88 passed）、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

本轮 Django 用户写接口运行时契约治理已完成：`backend/drf_admin/utils/test_runtime_api_contracts.py` 已覆盖 `users_create/users_update/users_delete`，验证创建成功信封、更新落库和批量删除 `ids` 请求体契约；`scripts/validate_api_contracts.py` 已强制检查这些 Django 写接口运行时测试片段。验证通过：目标运行时契约测试（3 passed）、Django `uv run ruff check .`、Django `uv run pytest`（89 passed）、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

本轮错误码契约治理已完成：新增 `scripts/api_error_codes.py` 作为共享错误码契约目录，前端、Django、FastAPI 契约测试和 `scripts/validate_api_contracts.py` 已共同锁定 `40000/40001/40002` 的公共语义；FastAPI 登录失败、验证码失败已改为 `40000`，避免误触发前端 Access Token 刷新分支。验证通过：根目录文档/API/模型/路由组件契约校验、脚本编译、前端 `pnpm run quality`（64 files / 169 tests）、前端 `pnpm run build`、前端 `pnpm run test:e2e:smoke`（4 passed，沙箱监听失败后提权重跑通过）、Django `uv run ruff check .`、Django `uv run pytest`（90 passed）、FastAPI `make quality`（515 passed，覆盖率 83.76%）和 `git diff --check`。

本轮用户管理核心业务 E2E 已完成：新增 Playwright smoke 用例，使用显式 route mock 覆盖登录、动态路由、认证信息、部门、角色、用户列表和新增用户接口；`test:e2e:smoke` 已纳入该用例。验证通过：目标 E2E（1 passed）、完整 smoke E2E（5 passed）、前端 `pnpm run quality`（64 files / 170 tests）、前端 `pnpm run build`、根目录文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮 FastAPI 用户写接口运行时契约扩面已完成：`scripts/validate_api_contracts.py` 已把 `fastapi/tests/test_runtime_api_contracts.py` 纳入必备契约测试入口，并强制检查 `users_create/users_update/users_delete` 抽样片段；FastAPI 运行时测试已覆盖创建、更新、批量删除和删除后分页列表不可见。验证通过：RED 阶段契约校验失败符合预期，目标测试（3 passed）、`python3 scripts/validate_api_contracts.py .`、FastAPI `make quality`（516 passed，覆盖率 83.93%）、根目录文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮用户管理权限链路 E2E 已完成：`frontend/e2e/user-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增、批量删除、编辑、删除按钮会被 `v-hasPerm` 移除；认证 mock 支持按用例注入权限集合，未 mock 的接口继续返回 404 暴露遗漏。为避免本地 Playwright 登录 mock 并发竞争，`test:e2e:smoke` 改为 `--workers=1`，并由治理测试锁定。验证通过：RED 阶段受限权限仍显示新增按钮符合预期失败，目标 E2E（2 passed）、完整 smoke（6 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮角色管理权限链路 E2E 已完成：`frontend/e2e/role-management.spec.ts` 新增仅查询权限场景，RED 阶段确认 `新增角色` 仍可见；随后 `frontend/src/views/system/role/index.vue` 为新增、批量删除、分配权限、编辑、删除接入现有 `system:roles:*` 按钮权限码。`test:e2e:smoke` 已纳入角色管理用例，并由 Playwright 治理测试锁定。验证通过：目标 E2E（1 passed）、完整 smoke（7 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮菜单管理权限链路 E2E 已完成：`frontend/e2e/menu-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增菜单、新增、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入菜单管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/menu-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（8 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮文件上传 / 删除链路 E2E 已完成：`frontend/e2e/file-upload-delete.spec.ts` 新增浏览器级 smoke，用动态路由 mock 进入 demo 上传页，验证文件上传成功后删除请求使用后端返回的相对 `path`；`test:e2e:smoke` 已纳入该用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/file-upload-delete.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（9 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮部门管理权限链路 E2E 已完成：`frontend/e2e/dept-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增部门、批量删除、行内新增、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入部门管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/dept-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（10 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮字典管理权限链路 E2E 已完成：`frontend/e2e/dict-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增字典、批量删除、字典数据、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入字典管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/dict-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（11 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮字典项管理权限链路 E2E 已完成：`frontend/e2e/dict-item-management.spec.ts` 新增仅查询权限场景，验证用户可进入动态路由页面但新增字典项、批量删除、编辑、删除按钮会被既有 `v-hasPerm` 移除；`test:e2e:smoke` 已纳入字典项管理用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段治理测试因缺少 `e2e/dict-item-management.spec.ts` 失败，目标 E2E（1 passed）、完整 smoke（12 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮通知公告权限码治理已完成：`frontend/src/views/system/notice/index.vue` 的通知公告写操作按钮权限码已从 `sys:notice:*` 对齐到后端和权限种子的 `system:notices:*`；新增 `frontend/e2e/notice-management.spec.ts`，用后端标准权限验证新增通知、批量删除、发布、撤回、编辑、删除按钮可见；`test:e2e:smoke` 已纳入通知公告用例，并由 Playwright 治理测试锁定。验证通过：RED 阶段目标 E2E 因 `新增通知` 不可见失败，目标 E2E（1 passed）、完整 smoke（13 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、文档/API/模型/路由组件契约校验、脚本编译、敏感信息扫描和 `git diff --check`。

本轮通知公告关键 API 契约目录治理已完成本地验证：`scripts/api_endpoint_contracts.py` 已纳入通知公告分页、创建、更新、删除、发布、撤回端点，并将通知公告契约拆入 `scripts/api_endpoint_notice_contracts.py`，避免共享目录文件超过复杂度约束；FastAPI 运行时抽样覆盖 `notices_page`；`scripts/validate_api_contracts.py` 已锁定通知公告契约测试、文档片段和拆分后的契约模块。验证通过：FastAPI 目标契约测试（8 passed）、Django 目标契约测试（5 passed）、FastAPI `make quality`（516 passed，覆盖率 83.93%）、Django ruff、Django `uv run pytest`（90 passed）、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

通知公告关键 API 契约目录治理已通过 PR #109 合并：远端 CI 通过 Django Backend Quality、FastAPI Backend Quality、Frontend Quality，合并提交为 `0b2d026`。

本轮日志管理路径 E2E 治理已完成本地验证：`frontend/src/api/system/log-api.ts` 的日志分页基路径已从 `/api/v1/logs` 对齐为 `/api/system/logs`，经请求拦截器生成 `/api/v1/system/logs/page`；新增 `frontend/e2e/log-management.spec.ts` 复现并锁定该路径，`test:e2e:smoke` 已纳入日志管理用例，Playwright 治理测试同步检查。验证通过：RED 阶段目标 E2E 捕获实际路径 `/api/v1/logs/page`，GREEN 后目标 E2E（1 passed）、完整 smoke（14 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

日志管理路径 E2E 治理已通过 PR #110 合并：远端 CI 通过 Django Backend Quality、FastAPI Backend Quality、Frontend Quality，合并提交为 `917a9d4`。

本轮系统配置孤儿功能治理已完成本地验证：当前 Django/FastAPI 路由和权限种子均无系统配置契约，`frontend/src/api/system/config-api.ts`、`frontend/src/views/system/config/index.vue` 与 `frontend/src/styles/pages/_system-config.scss` 已删除，`frontend/src/views/__tests__/config-style-migration.spec.ts` 改为治理测试，防止无后端契约时继续保留前端配置模块；`docs/FRONTEND_OPTIMIZATION_BACKLOG.md` 已移除已删除页面引用。验证通过：RED 阶段目标治理测试捕获 `config-api.ts` 仍存在，GREEN 后目标测试（1 passed）、前端 `pnpm run quality`（64 files / 171 tests）、前端 `pnpm run build`、根目录文档/API/模型/路由组件契约校验、脚本编译和 `git diff --check`。

本轮角色分页关键 API 契约治理已完成本地验证：`scripts/api_endpoint_contracts.py` 已纳入 `roles_page`，FastAPI 角色分页已显式接受前端 `pageSize` 参数，运行时抽样测试会创建 2 个角色并断言 `pageSize=1` 真实生效；`scripts/validate_api_contracts.py` 已锁定角色分页契约测试片段。验证通过：RED 阶段目标测试捕获 `KeyError: 'roles_page'`，GREEN 后 FastAPI 目标契约测试（8 passed）、API/文档校验、脚本编译、Django 契约目标测试（8 passed）、Django ruff、Django `uv run pytest`（90 passed）、FastAPI `make quality`（516 passed，覆盖率 83.97%）和 `git diff --check`。

本轮部门 E2E 登录 bootstrap 稳定性治理已完成本地验证：远端 CI 曾在 `dept-management.spec.ts` 首次运行时停留 `/login?redirect=%2Fsystem%2Fdepartments` 后重试通过；本轮为部门 smoke 登录后显式等待登录、用户信息和动态路由响应，再断言目标 URL，并新增治理测试锁定该等待边界。验证通过：RED 阶段治理测试捕获缺少 `waitForDepartmentLoginBootstrap`，GREEN 后治理测试（6 passed）、部门 E2E 重复 10 次（10 passed）、部门 E2E 复核 3 次（3 passed）、前端 `pnpm run quality`（64 files / 172 tests）、前端 `pnpm run test:e2e:smoke`（14 passed）、前端 `pnpm run build`、文档校验和 `git diff --check`。

本轮部门树关键 API 契约治理已通过 PR #116 合并：共享端点目录新增 `depts_tree`，Django/FastAPI 运行时抽样已覆盖部门树 `search/status`，FastAPI 部门树接口已真实应用前端查询参数；远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过，合并提交为 `5d8c361`。

本轮角色写接口运行时契约治理已通过 PR #117 合并：共享端点目录新增角色创建、更新、批量删除、菜单 ID 查询和权限分配契约；Django/FastAPI 均补齐 `PUT /api/v1/system/roles/{id}/menus/`，运行时抽样覆盖角色创建、更新、分配权限和删除闭环；远端 Django Backend Quality、FastAPI Backend Quality、Frontend Quality 均通过，合并提交为 `f042741`。

本轮通知公告写接口运行时契约治理已完成本地验证：FastAPI 通知公告响应恢复 camelCase 输出，Django 补齐 `system_notices` 模型、管理端创建/更新/删除/发布/撤回路径和运行时抽样测试；共享 API 契约校验和模型契约校验已纳入通知公告写接口测试入口。验证通过：FastAPI 契约组（15 passed）、Django 契约组（14 passed）、Django `uv run pytest`（96 passed）、FastAPI `make quality`（522 passed，覆盖率 84.75%）、文档/API/模型/路由组件契约校验、脚本编译、ruff、敏感信息扫描和 `git diff --check`。

本轮 FastAPI 模型表名契约治理已完成本地验证：`scripts/validate_model_contracts.py` 已静态解析 `fastapi/app/db/models/system.py` 与 `fastapi/app/db/models/oauth.py` 的 `Meta.table`，并对照 `scripts/model_contracts.py` 中的共享表名契约；`fastapi/tests/test_import_django_model_contracts.py` 已补充运行时断言，避免 Django → FastAPI 模型迁移或导入链路出现表名漂移。验证通过：模型契约校验、FastAPI 目标测试（2 passed）、FastAPI `make quality`（523 passed，覆盖率 84.75%）、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 字段别名目标契约治理已完成本地验证：`scripts/model_contracts.py` 新增 `iter_fastapi_alias_targets`，集中暴露 Django → FastAPI 字段别名的目标字段集合；`scripts/validate_model_contracts.py` 已静态解析 FastAPI `BaseModel/system/oauth` 模型字段，并校验别名目标字段真实存在；FastAPI 契约测试同步增加运行时断言。验证通过：RED 阶段目标测试因缺少字段级入口失败，GREEN 后目标测试（3 passed）、FastAPI `make quality`（524 passed，覆盖率 84.75%）、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 多对多关联表契约治理已完成本地验证：`scripts/model_contracts.py` 新增 Django/FastAPI 多对多 through 表契约，覆盖角色-权限与用户-角色两条关联；`scripts/validate_model_contracts.py` 新增静态 through 表校验，并把 AST 解析 helper 拆入 `scripts/model_contract_ast.py`，避免契约校验脚本超过单文件复杂度约束；FastAPI 契约测试同步增加运行时断言。验证通过：RED 阶段目标测试因缺少关联契约入口失败，GREEN 后目标测试（4 passed）、FastAPI `make quality`（525 passed，覆盖率 84.75%）、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 Django 迁移链跟踪治理已完成本地验证：新增 `scripts/validate_django_migrations.py`，将 `system` 完整迁移链纳入 Git 跟踪，并在 `.gitignore` 和 CI 文档校验阶段显式覆盖全局 ignore 漂移；`docs/DATABASE_SCHEMA.md` 与 `docs/AI_CONTEXT.md` 已同步迁移链校验入口。验证通过：RED 阶段捕获 4 个未跟踪 migration 和 3 条缺失 unignore 规则，GREEN 后迁移链校验、文档/API/模型/路由组件契约校验、脚本编译、Django `makemigrations --check --dry-run`、Django ruff、Django `uv run pytest`（96 passed）、敏感关键词扫描和 `git diff --check`。

本轮 GitHub Actions Node 24 runtime 治理已完成本地验证：质量门禁 workflow 将 `pnpm/action-setup` 升级到 v6，并由 `scripts/validate_docs.py` 反向校验，避免 CI 继续依赖目标为 Node 20 的 v4 action。验证通过：RED 阶段文档校验先捕获缺少 Node 24 opt-in，随后捕获仍使用 `pnpm/action-setup@v4`；GREEN 后文档/API/模型/路由组件/Django 迁移校验、脚本编译、敏感关键词扫描和 `git diff --check` 均通过。

本轮 FastAPI 字段元数据契约治理已完成本地验证：`scripts/model_contracts.py` 新增字段类型、`null`、`default` 契约，覆盖基础时间戳、权限菜单布尔字段和字典数据关键字段；`scripts/model_contract_ast.py` 静态解析 FastAPI 字段声明，`scripts/validate_model_contracts.py` 与 FastAPI 导入契约测试共同锁定字段元数据，避免字段类型或默认值漂移。验证通过：RED 阶段目标测试因缺少字段元数据契约入口失败，GREEN 后目标测试（5 passed）、FastAPI `make quality`（526 passed，覆盖率 84.75%）、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 字段约束契约治理已完成本地验证：新增 `scripts/model_field_contracts.py` 承载字段元数据与字段约束契约，避免主契约文件继续膨胀；新增 `scripts/model_constraint_validation.py` 静态校验字段 `max_length`、`unique`、`index`，覆盖权限、角色、字典和用户的关键字段约束；FastAPI 导入契约测试同步增加运行时断言。验证通过：RED 阶段目标测试因缺少字段约束契约入口失败，GREEN 后目标测试（6 passed）、模型契约校验、FastAPI `make quality`（527 passed，覆盖率 84.75%）、根目录文档/API/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 模型索引契约治理已完成本地验证：新增 `scripts/model_index_contracts.py` 承载模型级 `Meta.indexes` 契约，覆盖权限、角色、部门、通知公告、字典、字典项和用户关键查询索引；新增 `scripts/model_index_ast.py` 与 `scripts/model_index_validation.py` 静态解析并校验模型索引声明；FastAPI 导入契约测试同步增加运行时断言。验证通过：RED 阶段目标测试因缺少模型索引契约入口失败，GREEN 后目标测试（7 passed）、模型契约校验、FastAPI `make quality`（528 passed，覆盖率 84.75%）、根目录文档/API/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 FastAPI 模型唯一组合契约治理已完成本地验证：`scripts/model_index_contracts.py` 新增 `NoticeReads` 的 `Meta.unique_together` 共享契约，锁定通知已读记录按通知和用户唯一；`scripts/model_index_ast.py` 与 `scripts/model_index_validation.py` 已静态解析并校验唯一组合声明；FastAPI 导入契约测试同步增加运行时断言。验证通过：RED 阶段目标测试因缺少唯一组合契约入口失败，GREEN 后目标测试（8 passed）、模型契约校验、FastAPI `make quality`（529 passed，覆盖率 84.75%）、根目录文档/API/路由组件/迁移契约校验、脚本编译和 `git diff --check`。

本轮 Django 模型表名契约治理已完成本地验证：`scripts/validate_model_contracts.py` 已静态解析 Django `system` 模型的 `Meta.db_table`，并对照 `scripts/model_contracts.py` 中的共享表名契约；Django 契约测试同步增加运行时断言，避免 Django 表名与共享模型迁移契约漂移。验证通过：RED 阶段目标测试因缺少 Django 表名契约入口失败，GREEN 后目标测试（1 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、Django ruff、Django `uv run pytest`（97 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）、脚本编译和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只新增 Django 表名契约入口、静态校验和运行时测试；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮只增强内部契约校验与测试入口，不改变对外 API、数据库结构或用户可见流程；剩余风险是 Django 静态解析目前覆盖 `system` 相关模型文件，后续新增其他 Django app 模型时需要同步扩展契约目录。

本轮模型契约校验脚本拆分已完成本地验证：`validate_model_contracts.py` 不再直接维护 Django/FastAPI 测试片段清单，新增 `scripts/model_test_validation.py` 承接测试入口校验职责，并用 Django 治理测试锁定拆分边界。验证通过：RED 阶段目标测试因缺少 `model_test_validation` 导入失败，GREEN 后目标测试（1 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（98 passed）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只拆分模型契约测试入口校验职责，不改变模型契约内容和对外 API；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，`scripts/validate_model_contracts.py` 已降至 248 行，新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮是内部校验脚本结构调整，不改变用户可见功能、API 或数据库结构；剩余风险是后续继续扩展 Django 字段契约时仍需继续拆分主入口中的其他职责。

本轮 Django 字段元数据契约治理已完成本地验证：新增 `iter_django_field_metadata_contracts`，覆盖 `Permissions.keepAlive/alwaysShow` 与 `Dicts.dict_code/remark` 的字段类型、`null` 和默认值；`scripts/model_django_ast.py` 已能静态解析 Django `models.*Field` 字段元数据，`scripts/validate_model_contracts.py` 已接入 Django 字段元数据校验。验证通过：RED 阶段目标测试因缺少 Django 字段契约入口失败，GREEN 后目标测试（2 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（99 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只增加 Django 字段元数据契约，不改变数据库结构、对外 API 或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，相关文件均小于 300 行；Document-refresh: not-needed，原因：本轮是内部契约测试和校验扩面，不改变用户可见功能、API 或数据库结构；剩余风险是本轮只覆盖字段元数据，Django 字段 `max_length/unique/index` 约束仍需后续单独治理。

本轮 Django 字段约束契约治理已完成本地验证：新增 `iter_django_field_constraint_contracts`，覆盖 `Permissions.name/route_path/perm`、`Roles.name`、`Dicts.dict_code`、`Users.username/mobile/email` 的 `max_length/unique/index` 关键约束；Django 静态 AST 解析已扩展字段约束，并显式合并 `AbstractUser` 继承字段元数据，避免静态校验漏掉有效模型字段。验证通过：RED 阶段目标测试因缺少 Django 字段约束入口失败，GREEN 后目标测试（3 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（100 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只增加 Django 字段约束契约，不改变数据库结构、对外 API 或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，相关文件均小于 300 行；Document-refresh: not-needed，原因：本轮是内部契约测试和校验扩面，不改变用户可见功能、API 或数据库结构；剩余风险是 `scripts/model_field_contracts.py` 已增至 287 行，下一轮继续扩展字段契约前应先拆分该文件。

本轮字段约束契约拆分已完成本地验证：`scripts/model_field_contracts.py` 只保留字段元数据契约，字段约束 dataclass、目录、自检和迭代器已迁移到 `scripts/model_field_constraint_contracts.py`；`NO_DEFAULT` 哨兵值拆入 `scripts/model_contract_sentinel.py`，避免新旧契约模块互相导入形成循环依赖；Django 治理测试已锁定字段约束目录不再回流到元数据契约入口。验证通过：RED 阶段目标测试因缺少约束契约拆分失败，GREEN 后目标测试（2 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（101 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只做内部契约模块拆分，不改变数据库结构、对外 API 或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，`scripts/model_field_contracts.py` 降至 138 行，`scripts/model_field_constraint_contracts.py` 为 163 行，新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮是内部契约代码结构调整，不改变用户可见功能、API 或数据库结构；剩余风险是后续如果字段元数据或约束目录继续扩展，仍需要按领域或后端类型继续拆分。

本轮 Django 多对多 through 表契约治理已完成本地验证：共享关联契约新增 `iter_django_relation_through_contracts` 入口，Django 运行时测试会校验 `Roles.permissions` 与 `Users.roles` 的 through 表；`scripts/model_django_ast.py` 已静态解析 `models.ManyToManyField(..., db_table=...)`，`scripts/validate_model_contracts.py` 已接入 Django through 表校验，避免共享契约只约束 FastAPI 侧。验证通过：RED 阶段目标测试因缺少 Django through 表契约入口失败，GREEN 后目标测试（4 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（102 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只增加 Django through 表契约校验，不改变数据库结构、对外 API 或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，相关文件均小于 300 行；Document-refresh: not-needed，原因：本轮是内部契约测试和校验扩面，不改变用户可见功能、API 或数据库结构；剩余风险是 `scripts/validate_model_contracts.py` 已增至 256 行，后续继续扩展模型契约校验前应优先拆分 FastAPI 校验职责。

本轮 FastAPI 模型校验拆分已完成本地验证：`scripts/validate_model_contracts.py` 不再直接承载 FastAPI 表名、字段别名目标、关联 through 表和字段元数据校验细节，新增 `scripts/model_fastapi_validation.py` 承接这些职责，CLI 主入口回到流程编排角色。验证通过：RED 阶段结构治理测试因缺少 `model_fastapi_validation` 导入失败，GREEN 后目标测试（3 passed）、模型契约校验、根目录文档/API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（103 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只拆分内部 FastAPI 模型契约校验职责，不改变数据库结构、对外 API 或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，`scripts/validate_model_contracts.py` 降至 140 行，`scripts/model_fastapi_validation.py` 为 137 行；Document-refresh: not-needed，原因：本轮是内部校验脚本结构调整，不改变用户可见功能、API 或数据库结构；剩余风险是后续继续扩展 FastAPI 字段约束或索引校验时，可能还需要继续拆分 `model_constraint_validation.py` 或 `model_index_validation.py`。

本轮文档契约入口校验拆分已完成本地验证：`scripts/validate_docs.py` 不再直接承载 API、模型、迁移和 workflow 契约入口细节，新增 `scripts/docs_contract_validation.py` 承接这些职责，主入口回到文档结构、AI 摘要和链接校验编排角色。验证通过：RED 阶段目标测试因缺少 `docs_contract_validation` 导入失败，GREEN 后目标测试（1 passed）、文档校验、API/模型/路由组件/迁移契约校验、脚本编译、Django ruff、Django `uv run pytest`（104 passed）、FastAPI `make quality`（529 passed，覆盖率 84.75%）和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只拆分内部文档契约入口校验职责，不改变用户可见功能、API、数据库结构或运行时业务逻辑；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；复杂度检查通过，`scripts/validate_docs.py` 降至 265 行，`scripts/docs_contract_validation.py` 为 86 行；Document-refresh: not-needed，原因：本轮是内部校验脚本结构调整，不改变用户可见文档内容、API 或数据库结构；剩余风险是 `validate_docs.py` 仍承载 authority、AI_CONTEXT 和链接校验，后续继续扩展前可按职责继续拆分。

本轮字典字段命名统一已完成本地验证：FastAPI `DictData` 内部字段已从 `code/desc` 改为 `dict_code/remark`，共享模型契约不再登记 `system.dicts` 的业务字段别名，Django fixture 导入改为同名字段写入；schema 仍接受 `dictCode/code` 与 `remark/desc`，响应继续输出 `dictCode/remark`。验证通过：RED 阶段目标测试因 `dict_code -> code`、`remark -> desc` 字段别名债失败，GREEN 后 FastAPI 目标测试（76 passed）、FastAPI `make quality`（531 passed，覆盖率 84.74%）、Django 模型契约测试（4 passed）、根目录模型/API/文档/路由组件/迁移契约校验和 `git diff --check`。

Review-gate：finished；Spec 符合度通过，本轮只统一字典主表内部字段名，不修改表名 `system_dict_data`、字典项外键、前端调用或 API 路径；安全检查未发现本轮新增 secret、mock 或静默 fallback；复杂度检查通过，本轮未新增超大函数或超大文件；Document-refresh: not-needed，原因：本轮不改变用户可见 API、数据库表名或产品文档事实；剩余风险是 FastAPI 字典表名仍与 Django `system_dicts` 不一致，需要后续独立迁移计划处理。

Review-gate：finished；Spec 符合度通过，本轮只统一 FastAPI 字典主表表名和共享模型契约，不修改 Django 模型、字典项外键、前端 API 或权限契约；安全检查未发现新增 secret、mock、双表读写或静默 fallback；复杂度检查通过，本轮代码仅新增一个目标契约测试并修改两个表名常量，未新增超长函数；Document-refresh: needed，原因：数据库表名事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧表 `system_dict_data`，需要通过显式迁移切换到 `system_dicts`。

字典主表表名统一已通过 PR #152 合并：合并提交为 `10477de4c95141788700125ecd88ba8387c30dc6`，远端 Django Backend Quality、FastAPI Backend Quality 和 Frontend Quality 均通过。

关联表命名统一已通过 PR #155 合并：FastAPI 角色-权限和用户-角色 through 表已统一到 Django 命名，合并提交为 `08811baafe4e3f15d866657b299eaf97a6807b55`，远端 Django Backend Quality、FastAPI Backend Quality 和 Frontend Quality 均通过。

Review-gate：finished；Spec 符合度通过，本轮只统一 FastAPI 两张 M2M through 表字段名和共享关联契约，不修改 Django 模型、主表、前端 API、权限码或业务响应；安全检查未发现新增 secret、mock、双字段读写或静默 fallback；复杂度检查通过，本轮扩展一个目标契约测试并修改两个 M2M key 常量，未新增超长函数；Document-refresh: needed，原因：数据库关联字段事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧字段 `user_id/role_id/permission_id`，需要显式迁移到 Django 命名字段，且字典项字段差异仍需后续独立治理。

关联表字段命名统一已通过 PR #158 合并：FastAPI 用户-角色和角色-权限 through 字段已统一到 Django 命名，合并提交为 `11eeda849cfdc6bd3188150c5df2ca07c0d26c6f`，远端 Django Backend Quality、FastAPI Backend Quality 和 Frontend Quality 均通过。

Review-gate：finished；Spec 符合度通过，本轮只移除 FastAPI 字典项 `is_default/remark` 扩展字段，并同步 schema、service、目标测试、数据库文档和技术债，不修改 Django 模型、前端页面或字典项 `label/value/sort` 后续治理范围；安全检查未发现新增 secret、mock、扩展字段 fallback 或静默兼容；复杂度检查通过，本轮删除字段读写并新增一个目标契约测试，未新增复杂分支；Document-refresh: needed，原因：数据库字典项字段事实和技术债状态已变化；剩余风险是已有 FastAPI 数据库如果仍存在旧列 `is_default/remark`，需要显式迁移删除或忽略，且 `fastapi/app/schemas/system.py`、`fastapi/app/services/system/dict_service.py`、`fastapi/tests/test_dict_service.py` 仍为既有超 300 行文件，后续应单独拆分治理。

字典项 FastAPI-only 字段收口已通过 PR #161 合并：FastAPI `DictItems.is_default/remark` 已移除，合并提交为 `d0b7c7740e6251b39d384a7859320b44925758d3`，远端 Django Backend Quality、FastAPI Backend Quality 和 Frontend Quality 均通过。
