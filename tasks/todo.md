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
