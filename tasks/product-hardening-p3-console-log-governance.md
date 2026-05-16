# P3 前端直接 console 收口计划

## 目标

- 将 `frontend/src` 中剩余直接 `console.*` 收口到统一 `createLogger`。
- 用治理测试锁住回归，避免后续组件、视图、demo 或历史兼容层继续绕过统一日志出口。
- 保持错误暴露，不引入静默回退、mock、伪成功路径或业务控制流变化。

## 非目标

- 不调整复制、上传、登录、菜单、面包屑、用户导入、个人资料、旧 CURD 或 demo 页的业务行为。
- 不改 `createLogger` 输出策略；`warn/error` 仍保持可见。
- 不改 API 契约、路由权限、请求拦截器或后端实现。

## 当前事实

- `frontend/src/utils/logger.ts` 已提供统一日志出口 `createLogger`。
- P1 已收口 WebSocket 与关键运行时路径，P2 已修复 Token 刷新失败挂起请求。
- 当前直接 `console.*` 剩余在通用组件、布局组件、登录/个人资料/用户导入视图、旧 `CURD` 容器和 `demo/dict-sync` 页面。

## 组件边界

- 不新增组件，不拆分既有 SFC。
- 本轮只在现有 SFC 的 `<script setup>` 或脚本区引入局部 logger 实例。
- 旧 `CURD/PageContent.vue` 保持原职责和事件流，仅替换错误输出出口。

## 方案对比

### 方案 A：全量禁止 `frontend/src` 直接 `console`

- 范围：除 `src/utils/logger.ts`、测试文件和类型声明外的所有前端源码。
- 优点：规则清晰，能防止组件层和 demo 页继续散落直接日志。
- 缺点：一次性触碰文件较多，但都只替换日志出口。

### 方案 B：只收口非 demo、非旧 CURD 文件

- 范围：布局、通用组件和业务视图。
- 优点：影响面更小。
- 缺点：规则不彻底，`demo` 与旧兼容层仍会成为后续复制粘贴来源。

## 推荐方案

采用方案 A。

原因：P0-P2 已完成关键路径治理，P3 的价值在于把剩余低优先级项彻底收口；本轮只替换日志出口，不改变业务控制流，适合用全量守卫测试约束。

## 执行计划

- [x] 新增全量直接 `console.*` 治理测试，并先确认当前代码会失败。
- [x] 为剩余 SFC/组件引入 `createLogger` 并替换直接 `console.warn/error`。
- [x] 运行目标测试，确认治理测试由红转绿。
- [x] 运行前端质量、构建、smoke 和文档校验。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| 全量 console 守卫 | `pnpm --dir frontend run test:unit -- direct-console-governance` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 前端构建 | `pnpm --dir frontend run build` |
| 前端 smoke | `pnpm --dir frontend run test:e2e:smoke` |
| 文档计划 | `python3 scripts/validate_docs.py . --profile generic` |

## HARD-GATE

用户已明确要求“继续推进，直到把 p0,p1,p2,p3 都做完”，本计划作为已授权执行范围内的轻量 Spec 执行。

## 进度记录

- 2026-05-16：#49 已合并，确认 P2 完成；本轮进入 P3 前端直接 `console.*` 收口。
- 2026-05-16：新增 `direct-console-governance` 守卫测试；首次运行按预期失败，列出 10 个仍直接调用 `console.*` 的生产源码文件。
- 2026-05-16：剩余直接 `console.*` 已迁移到 `createLogger`；`pnpm --dir frontend run test:unit -- direct-console-governance` 通过，34 个测试文件、98 条测试全绿。
- 2026-05-16：`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、`pnpm --dir frontend run test:e2e:smoke`、`python3 scripts/validate_docs.py . --profile generic`、`git diff --check` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮按方案 A 全量禁止生产前端源码直接 `console.*`，仅保留 `frontend/src/utils/logger.ts` 作为统一出口。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径，原异常仍通过 `warn/error` 暴露。
- 测试与验证：通过；治理测试先红后绿，完整前端质量门禁、生产构建、登录 smoke、文档校验和 diff 检查均通过。
- 复杂度检查：通过；新增测试文件 48 行，未新增超过 50 行的函数；被改 SFC 只新增局部 logger 实例和日志调用替换。
- Document-refresh: not-needed。原因：未改变 API、数据库、架构契约或用户可见功能，只更新本轮任务计划与验证记录。
- 剩余风险：本轮不改变错误处理控制流，因此仍沿用旧组件原有失败提示粒度。
- 潜在技术债：`CURD/PageContent.vue` 仍是历史兼容容器，文件体量和职责边界不属于本轮日志治理范围。
- 结论：通过。
