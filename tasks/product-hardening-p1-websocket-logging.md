# P1 WebSocket 日志治理执行计划

## 目标

- 将 WebSocket 相关调试输出从直接 `console.log` 收口到统一 logger。
- 默认生产环境不输出调试日志，避免在线用户、字典同步和 STOMP 连接状态刷屏。
- 保留警告和错误输出，避免连接失败被静默吞掉。

## 非目标

- 不重写 WebSocket 连接状态机。
- 不修改重连策略、订阅主题、消息协议或鉴权方式。
- 不新增后端接口或测试数据依赖。

## 当前事实

- `frontend/src/composables/websocket/useStomp.ts` 存在多处连接、订阅、重连 `console.log`。
- `frontend/src/composables/websocket/useOnlineCount.ts` 存在在线人数连接生命周期 `console.log`。
- `frontend/src/composables/websocket/useDictSync.ts` 存在字典订阅和消息处理 `console.log`。
- `frontend/src/plugins/websocket.ts` 存在插件初始化和连接清理 `console.log`。
- 生产构建会提示 `useOnlineCount` 经 `@/composables` 汇总入口与 `plugins/websocket.ts` 形成循环分块风险，需要用具体模块导入收口。

## 执行计划

- [x] 从最新 `origin/master` 创建 `codex/websocket-logging-governance`。
- [x] 新增统一 logger 工具，支持 scope、debug/info/warn/error 和调试开关。
- [x] 替换 WebSocket 相关模块中的直接 `console.log`。
- [x] 将 WebSocket 插件导入从 `@/composables` 汇总入口改为具体模块，消除循环分块警告。
- [x] 增加 logger 单测和 WebSocket 日志治理守卫测试。
- [x] 运行最小充分验证并记录结果。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| logger 行为 | `pnpm --dir frontend run test:unit -- logger websocket-logging` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 前端构建 | `pnpm --dir frontend run build` |
| 文档计划 | `python3 scripts/validate_docs.py . --profile generic` |

## 进度记录

- 2026-05-16：创建分支并完成现状取证，确认本轮只治理日志出口。
- 2026-05-16：新增 `createLogger`，WebSocket 相关模块改为统一 logger；`pnpm --dir frontend run test:unit -- logger websocket-logging`、`pnpm --dir frontend run type-check` 通过。
- 2026-05-16：构建发现 WebSocket barrel 导入导致循环分块警告，已将插件导入改为具体模块；`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke`、`python3 scripts/validate_docs.py . --profile generic` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只治理 WebSocket 日志出口和构建暴露的同域导入循环，未修改连接状态机、订阅协议、重连策略或后端契约。
- 安全检查：通过；未新增 secret，warn/error 保持输出，未引入 mock、静默回退或伪成功路径。
- 测试与验证：通过；已执行前端质量门禁、生产构建、登录 smoke 和文档校验。
- 复杂度检查：新增 logger 为 39 行，守卫测试为 26 行；`useStomp.ts` 仍是历史 300 行以上文件，本轮未拆状态机以控制影响面。
- Document-refresh: not-needed。原因：未改变用户文档、API、数据库模型或架构入口，只新增本轮执行计划和验证记录。
- 剩余风险：本轮未接入真实 WebSocket 服务做端到端消息验证，日志出口和构建行为由单测、守卫测试和生产构建覆盖。
- 潜在技术债：WebSocket composable 仍有较高职责密度，后续如要调整重连或订阅生命周期，应先拆分状态机与订阅管理。
- 结论：通过。
