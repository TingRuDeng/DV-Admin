# P0-P3 产品化治理全量收口计划

## 目标

- 把当前审计清单中尚未真正闭环的 P0、P1、P2、P3 项收口到可验证状态。
- 优先补齐发布前会直接影响安全、稳定性和双后端替代关系的缺口。
- 将长期治理项转成代码门禁、测试或权威文档，避免继续依赖人工记忆。

## 非目标

- 不一次性统一 Django 与 FastAPI 的响应字段命名；本轮用契约测试锁住现状兼容边界。
- 不引入外部 SaaS 或需要线上账号的错误追踪服务；先做 request id、结构化日志和可落地的错误定位闭环。
- 不凭空设计大规模业务功能；审计日志 UX、批量操作、导入导出状态只做当前代码中可验证的基础能力和治理入口。
- 不重写所有系统页面；前端页面级治理只补核心回归测试和可访问性/性能 smoke 门禁。

## 当前事实

- 富文本风险已基本收口：`frontend/src/components/SafeHtml/index.vue` 使用 `sanitizeHtml`，通知详情入口已替换为 `SafeHtml`；`frontend/src/utils/safe-html.ts:sanitizeHtml` 有单测。
- CI 已加入文档校验和最小 E2E smoke：`.github/workflows/quality-gates.yml` 的 `frontend` job 运行 `scripts/validate_docs.py` 与 `pnpm run test:e2e:smoke`。
- Playwright 端口已改为读取 `VITE_APP_PORT`：`frontend/playwright.config.ts` 使用 `loadEnv` 和默认 `9527`。
- 双后端响应仍存在事实差异：`backend/drf_admin/utils/middleware.py:ResponseMiddleware.process_response` 输出 `{msg, errors, code, data}`；`fastapi/app/schemas/base.py:ResponseModel` 输出 `{code, message, data}`。
- 前端错误读取已做兼容：`frontend/src/utils/api-error.ts:getApiErrorMessage(payload, fallback)` 支持 `errors/msg/message`，但缺少跨 Django/FastAPI 的共享契约测试入口。
- `frontend/vitest.config.ts` 仍排除 `src/store/**` 和 `src/router/**`，`useUserStore`、`usePermissionStore`、`useTagsViewStore` 只有间接治理测试。
- `frontend/src/composables/websocket/useStomp.ts:useStomp(options)` 同时承担连接、重连、订阅、计时器和状态职责，适合拆出可注入的连接管理器。
- Django Ruff 全量打开 `F401/I001/F403/F405` 会暴露 53 个问题，其中 51 个可自动修复；主要集中在导入排序、未使用导入和 `settings_test.py` 星号导入。
- FastAPI `uv run mypy app` 当前暴露 85 个类型问题，主要集中在 Tortoise 关系字段标注、缓存空值边界、logger 类型和 service 层模型字段访问。
- FastAPI 已有结构化日志、request id、慢请求日志和健康检查：`fastapi/app/utils/logger.py`、`fastapi/app/middleware/logging_middleware.py`、`fastapi/app/middleware/slow_query_middleware.py`、`fastapi/app/api/health.py`；Django 侧缺少对等健康检查和 request id 响应头闭环。
- 本轮只读验证中，`pnpm --dir frontend run test:unit -- route-access route-meta view-cache api-error --run` 实际运行 43 个测试文件、107 条测试，全部通过。

## 设计原则

- 先补可阻断发布风险的门禁，再做重构和成熟产品能力。
- 契约测试优先锁住“前端真实依赖的公共语义”，不把历史字段差异伪装成已经统一。
- WebSocket 重构只抽出连接管理器，不改变协议、主题名、认证方式和重连默认值。
- 后端门禁采用“真实收紧，不静默跳过”的方式；确实属于框架测试配置的特殊情况，用 `per-file-ignores` 明确限定。
- P2/P3 采用可执行治理优先，所有新增能力必须有测试或 CI 检查。

## 决策驱动因素

- P0 的核心风险是发布门禁无法阻止契约漂移，而不是字段命名本身不同。
- P1 的核心风险是 store/router/WebSocket 这类高影响路径缺少直接行为测试。
- P2 的核心风险是线上问题不可定位；request id、健康检查和结构化日志比大而全监控系统更适合当前仓库。
- P3 的核心风险是双后端和文档长期漂移；应优先用脚本、CI 和权威文档把边界固定下来。

## 可行方案对比

### 方案 A：严格全量一次性重构

- 内容：统一 Django/FastAPI 响应字段；重写 WebSocket 状态机；FastAPI 全量 mypy 立即归零；补所有业务 UX。
- 优点：终态看起来最彻底。
- 缺点：影响范围过大，容易把兼容变更、架构重构和业务功能混在一个 PR；双后端响应字段统一会破坏现有前端和文档契约。

### 方案 B：契约优先的全量收口

- 内容：保留现状兼容字段，用共享契约测试和 CI 锁住；补 store/router/WebSocket 直接测试；分层收紧 Ruff/mypy；补 Django request id/health；补性能和可访问性 smoke；更新 P3 权威文档和校验。
- 优点：能覆盖原清单风险点，改动可验证，兼容风险低。
- 缺点：不会把所有历史业务体验一次性重做，部分 P2 业务能力会以治理入口和测试边界收口。

## 推荐方案

推荐执行方案 B。

淘汰方案 A 的原因：它会把响应字段统一、WebSocket 重写、业务 UX 和后端类型治理塞进同一次大改，风险不随测试线性下降；更优雅的方式是先固定可验证契约，再逐层收紧。

## 执行计划

### 阶段 0：隔离与计划

- [x] 从最新 `origin/master` 创建 `codex/product-hardening-final-convergence`。
- [x] 写入本计划，并把总待办追加到 `tasks/todo.md`。

### 阶段 1：P0 剩余项真实收口

- [x] 新增共享 API 契约定义：`scripts/api_contracts.py`。
  - `normalize_api_envelope(payload: Mapping[str, object]) -> ApiEnvelope`
  - `assert_success_envelope(payload: Mapping[str, object], backend: str) -> None`
  - `assert_error_envelope(payload: Mapping[str, object], backend: str) -> None`
  - `assert_page_payload(payload: Mapping[str, object]) -> None`
- [x] 新增 Django 响应契约测试：`backend/drf_admin/utils/test_response_contract.py`。
  - 覆盖 `ResponseMiddleware.process_response(self, request, response)` 的成功、错误、幂等包裹行为。
- [x] 新增 FastAPI 响应契约测试：`fastapi/tests/test_api_contracts.py`。
  - 覆盖 `ResponseModel.success(data, message)`、`ResponseModel.error(code, message)`、`PageResult.create(total, page, page_size, results)`。
- [x] 新增前端契约兼容测试：`frontend/src/utils/__tests__/api-contract.test.ts`。
  - 覆盖 Django `msg/errors`、FastAPI `message`、分页 `list/total` 对前端边界层的兼容。
- [x] 更新 CI：`.github/workflows/quality-gates.yml`。
  - Django job 增加契约测试命令。
  - FastAPI job 保持契约测试随 pytest 执行。
  - Frontend job 保持 `test:e2e:smoke` 和文档校验。

### 阶段 2：P1 前端核心测试与 WebSocket 管理器

- [x] 调整 `frontend/vitest.config.ts`。
  - 从 `test.exclude` 移除 `src/store/**` 和 `src/router/**`。
  - 覆盖率排除是否保留按实际测试稳定性决定；如保留，必须说明原因。
- [x] 新增 `frontend/src/store/modules/__tests__/user-store.test.ts`。
  - 覆盖 `useUserStore.login(LoginFormData)`、`getUserInfo()`、`resetAllState()`、`refreshToken()`。
- [x] 新增 `frontend/src/store/modules/__tests__/permission-store.test.ts`。
  - 覆盖 `usePermissionStore.generateRoutes()`、`setMixLayoutSideMenus(parentPath)`、`resetRouter()`。
- [x] 新增 `frontend/src/store/modules/__tests__/tags-view-store.test.ts`。
  - 覆盖 `addView(view)`、`updateVisitedView(view)`、`delView(view)`、`delOtherViews(view)`、`delAllViews()`。
- [x] 抽出 WebSocket 连接管理器：`frontend/src/composables/websocket/stomp-connection-manager.ts`。
  - `createStompConnectionManager(options: StompConnectionManagerOptions): StompConnectionManager`
  - `connect(): void`
  - `disconnect(): void`
  - `subscribe(destination: string, callback: (_message: IMessage) => void): string`
  - `unsubscribe(subscriptionId: string): void`
  - `updateBrokerURL(nextBrokerURL: string): void`
- [x] 收窄 `frontend/src/composables/websocket/useStomp.ts:useStomp(options)` 职责。
  - 保留 Vue ref 对外 API，内部委托连接管理器。
- [x] 新增 WebSocket 管理器测试：`frontend/src/composables/websocket/__tests__/stomp-connection-manager.test.ts`。
  - 通过可注入 client factory 覆盖重复连接、授权缺失、超时重连、手动断开不重连、订阅清理。

### 阶段 3：P1 后端门禁收紧

- [x] 收紧 Django Ruff：`backend/pyproject.toml`。
  - 移除全局 `F401/I001/F403/F405` 忽略。
  - 对 `drf_admin/settings_test.py` 使用最小 `per-file-ignores = ["F403", "F405"]`。
- [x] 修复 Django Ruff 暴露问题。
  - 优先使用 `uv run ruff check . --select F401,I001 --fix`，再人工处理无法自动修复的导入和测试配置。
- [x] 扩大 FastAPI mypy：`fastapi/Makefile` 与 `.github/workflows/quality-gates.yml`。
  - 将 `mypy app/schemas` 提升为 `mypy app`。
- [x] 修复 FastAPI `mypy app` 85 个已知问题。
  - 模型字段：`fastapi/app/db/models/system.py`、`fastapi/app/db/models/oauth.py`。
  - 缓存边界：`fastapi/app/core/cache.py`、`fastapi/app/core/redis.py`。
  - 日志类型：`fastapi/app/utils/logger.py`。
  - 服务层字段访问：`fastapi/app/services/system/*.py`、`fastapi/app/api/v1/oauth/auth.py`、`fastapi/app/api/v1/information/profile.py`。
  - 异常处理器签名：`fastapi/app/main.py`。

### 阶段 4：P2 成熟产品基础能力

- [x] Django 增加 request id 中间件。
  - 文件：`backend/drf_admin/utils/request_id.py`。
  - 函数：`get_request_id() -> str | None`、`set_request_id(request_id: str) -> None`、`clear_request_id() -> None`。
  - 类：`RequestIdMiddleware.__call__(self, request)`。
- [x] Django 操作日志接入 request id。
  - 文件：`backend/drf_admin/utils/middleware.py`。
  - 函数：`OperationLogMiddleware.__call__(self, request)`。
- [x] Django 增加健康检查端点。
  - 文件：`backend/drf_admin/apps/system/views/health.py`。
  - 函数：`health_check(request)`、`liveness_check(request)`、`readiness_check(request)`。
  - 路由：`backend/drf_admin/urls.py` 增加 `/health`、`/health/live`、`/health/ready`。
- [x] 前端增加最小可访问性 smoke。
  - 文件：`frontend/e2e/accessibility-smoke.spec.ts`。
  - 先覆盖 `/login`、`/` 的标题、主 landmark 或表单标签，不引入外部扫描 SaaS。
- [x] 前端增加性能预算 smoke。
  - 文件：`frontend/e2e/performance-smoke.spec.ts`。
  - 覆盖登录页首屏响应和关键资源数量的宽松预算，避免失控回归。
- [x] 将 smoke 纳入 `frontend/package.json` 和 CI。
  - 新增或扩展 `test:e2e:smoke`，保持 CI 耗时可控。

### 阶段 5：P3 持续治理

- [x] 明确双后端长期策略。
  - 更新 `docs/ARCHITECTURE.md`、`docs/API_ENDPOINTS.md`。
  - 保持结论：当前是替代实现；共享契约由测试和文档共同约束。
- [x] 补 API 契约校验脚本入口。
  - 文件：`scripts/validate_api_contracts.py`。
  - 函数：`main(argv: Sequence[str] | None = None) -> int`。
  - 目标：校验契约定义文件、文档中标记的共享端点和测试覆盖清单一致。
- [x] 扩展文档校验。
  - 文件：`scripts/validate_docs.py`。
  - 增加对 API 契约脚本入口、AI_CONTEXT、权威文档链接的回归检查。
- [x] 更新 `docs/TECH_DEBT.md`。
  - 移除已完成或被测试覆盖的旧债务。
  - 保留仍需业务 PRD 的审计日志 UX、批量操作和导入导出任务状态。

## 验证矩阵

- 文档校验：`python3 scripts/validate_docs.py . --profile generic`
- API 契约校验：`python3 scripts/validate_api_contracts.py .`
- 文档脚本编译：`python3 -m py_compile scripts/validate_docs.py scripts/validate_api_contracts.py scripts/api_contracts.py`
- 前端质量：`pnpm --dir frontend run quality`
- 前端构建：`pnpm --dir frontend run build`
- 前端 E2E：`pnpm --dir frontend run test:e2e:smoke`
- Django Ruff：`cd backend && uv run ruff check .`
- Django 测试：`cd backend && uv run pytest`
- FastAPI 质量：`cd fastapi && make quality`
- FastAPI 全量 mypy：`cd fastapi && uv run mypy app`
- 最终 diff 审查：`git diff --check`、`git status --short`

## 风险与预想失败场景

- FastAPI 全量 mypy 可能暴露 Tortoise 类型系统与运行时字段不一致，需要使用框架推荐类型标注，而不是用 `type: ignore` 消音。
- Django Ruff 自动修复可能调整大量 import 顺序，执行后必须跑 Django 测试确认无导入副作用。
- WebSocket 连接管理器抽离可能改变重连时机；必须用 fake client 单测锁住旧行为。
- E2E 登录后路径如果依赖真实后端和数据，CI 只能保留稳定 smoke；完整业务 E2E 需要后续测试数据工厂。
- P2/P3 中涉及业务 UX 的事项缺少明确 PRD，本轮只做可验证基础能力和治理入口，不凭空扩展业务流程。

## HARD-GATE

当前只完成计划与只读核对。用户确认前不进行业务代码修改。

确认后执行方式：在当前 `codex/product-hardening-final-convergence` 分支按阶段 1 到阶段 5 顺序一次性推进；除非遇到会改变 API 兼容、需要删除业务功能或测试数据无法构造的阻塞，否则不再逐项停下询问。

## 进度记录

- 2026-05-21：从最新 `origin/master` 创建 `codex/product-hardening-final-convergence`，完成只读现状核对和失败面测量。
- 2026-05-21：Django Ruff 收紧测量发现 53 个问题，其中 51 个可自动修复。
- 2026-05-21：FastAPI `mypy app` 收紧测量发现 85 个问题。
- 2026-05-21：前端目标单测命令实际运行 43 个测试文件、107 条测试，全部通过。
- 2026-05-21：阶段 1 完成。新增共享 API 契约断言、Django/FastAPI/前端契约测试，并将 Django 契约测试纳入默认 pytest 与 CI；`python3 -m py_compile scripts/api_contracts.py`、Django 契约测试、FastAPI 契约测试、前端契约测试均通过。
- 2026-05-21：阶段 2 前半完成。移除 Vitest 对 store/router 的排除，新增 user/permission/tags-view store 直接测试，抽出 STOMP 连接管理器并新增连接、重连、订阅清理测试；`pnpm --dir frontend run test:unit -- stomp-connection-manager --run` 与 `pnpm --dir frontend run type-check` 通过。
- 2026-05-21：阶段 3 完成。Django Ruff 移除全局 `F401/I001/F403/F405` 忽略并通过 `uv run ruff check .`；FastAPI `mypy app` 从 85 个错误收敛到通过，并同步 `Makefile` 与 CI 门禁。
- 2026-05-21：阶段 4 完成。Django 增加 `X-Request-ID` 中间件、操作日志 request id 输出与 `/health` 探针；前端 smoke 扩展到登录页可访问性和性能预算，`VITE_APP_PORT=19527 pnpm run test:e2e:smoke` 通过。
- 2026-05-21：阶段 5 完成。新增 `scripts/validate_api_contracts.py`，扩展 `validate_docs.py` 对 API 契约入口和 CI 的检查，更新架构/API/AI_CONTEXT/技术债文档；文档校验、API 契约校验和脚本编译均通过。
- 2026-05-21：完整验证完成。`frontend quality/build/e2e smoke`、Django `ruff/pytest`、FastAPI `make quality/mypy app`、文档/API 契约校验、`git diff --check` 均通过；FastAPI 缓存 `get_or_set` 兼容直接值的回归已修复并通过 486 条测试。

## Review 小结

终态：finished。P0-P3 收口实现与已批准方案一致；新增契约测试、Django request id/health、前端可访问性与性能 smoke、FastAPI 全量 mypy 门禁和文档/API 契约校验均已落地。  
Document-refresh: needed  
原因：本轮改变了质量门禁、双后端契约、健康检查和技术债状态，已同步 `docs/ARCHITECTURE.md`、`docs/API_ENDPOINTS.md`、`docs/AI_CONTEXT.md` 与 `docs/TECH_DEBT.md`。  
剩余风险：业务级审计日志 UX、批量操作和导入导出任务状态仍需要独立 PRD；本轮只把基础治理入口与自动化门禁收口。
