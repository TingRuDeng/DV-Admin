# FastAPI OAuth API 拆分治理计划

## 目标

- 将 `fastapi/app/api/v1/oauth/auth.py` 从 750 行混合认证路由文件拆分为按职责组织的小模块。
- 保持 `from app.api.v1.oauth.auth import router` 兼容入口不变，避免影响 OAuth 总路由和历史引用。
- 不改变 URL 路径、HTTP 方法、请求参数、响应模型、错误码或认证业务行为。

## 非目标

- 不修改 JWT 生成、刷新令牌校验、黑名单、验证码或用户权限业务逻辑。
- 不调整前端 API 调用、Django 后端接口或共享 API 契约语义。
- 不清理 OpenAPI 长描述文本；本轮只移动端点定义。

## 当前事实

- `fastapi/app/api/v1/oauth/auth.py` 当前 750 行，包含 OAuth2 token 登录、JSON 登录、刷新令牌、登出、当前用户信息、菜单路由和验证码端点。
- `fastapi/app/api/v1/oauth/__init__.py` 只从 `app.api.v1.oauth.auth` 导入 `router` 并挂载到 `/oauth`。
- `scripts/api_endpoint_contracts.py` 的认证契约证据仍指向 `fastapi/app/api/v1/oauth/auth.py`，拆分后需要同步到新子模块路径。
- 相关接口测试集中在 `fastapi/tests/test_oauth.py`、`fastapi/tests/test_oauth_schemas.py`、`fastapi/tests/test_logging_sensitive_paths.py`。

## 决策日志

- 方案 A：新增 `fastapi/app/api/v1/oauth/routes/`，按登录、会话、用户信息、菜单、验证码拆分子 router，再由 `auth.py` include 子 router。
  - 优点：外部导入入口不变，职责清楚，`auth.py` 可收缩为聚合入口。
  - 缺点：需要同步契约脚本证据路径，并保留必要函数级导出。
- 方案 B：直接将 `auth.py` 改为包目录 `auth/`。
  - 优点：模块名更直观。
  - 缺点：文件到目录迁移影响更大，历史 import 和文档证据更容易受影响。
- 方案 C：只抽 helper，端点仍留在 `auth.py`。
  - 优点：改动较小。
  - 缺点：不能解决路由文件职责混杂和单文件体量问题。

推荐方案：采用方案 A。它保留兼容入口，拆分粒度与认证端点职责一致，影响范围最小。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `routes/login.py`，迁移 OAuth2 token 登录和 JSON 登录端点。
- [x] P3 串行：新增 `routes/session.py`，迁移刷新令牌和登出端点。
- [x] P4 串行：新增 `routes/profile.py`，迁移当前用户信息端点。
- [x] P5 串行：新增 `routes/menus.py`，迁移菜单路由端点。
- [x] P6 串行：新增 `routes/captcha.py`，迁移验证码端点。
- [x] P7 串行：将 `auth.py` 收缩为兼容聚合入口，并同步 API 契约证据路径。
- [x] P8 串行：执行 OAuth 目标测试、API 契约校验、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P9 串行：执行 review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_oauth.py tests/test_oauth_schemas.py tests/test_logging_sensitive_paths.py -q`
- `python3 scripts/validate_api_contracts.py .`
- `python3 scripts/validate_docs.py . --profile generic`
- `cd fastapi && make quality`
- `git diff --check`

## Review 小结

- OAuth 路由职责拆分已完成：`auth.py` 保留兼容聚合入口和函数级导出，登录、会话、用户信息、菜单和验证码端点已拆入 `routes/` 子模块；API 契约证据和 API 文档 source_of_truth 已同步到新路径。验证通过：OAuth 目标测试（23 passed）、API 契约校验、文档校验、OAuth 路由 ruff 检查、FastAPI `make quality`（539 passed，覆盖率 85.21%）和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮只拆分 OAuth API 路由职责，不改变 URL、HTTP 方法、请求参数、响应模型、错误码、JWT、验证码、黑名单或用户权限业务逻辑；安全检查未发现新增 secret、mock、静默 fallback 或硬编码凭据；复杂度检查通过，`auth.py` 已降至 37 行，新增路由文件均低于 300 行；Document-refresh: needed，原因：OAuth source_of_truth 代码路径已变化，已同步 `docs/API_ENDPOINTS.md`；剩余风险是本轮只处理 API 路由层，OAuth 依赖的 token 黑名单和验证码服务仍保持原结构，后续如继续治理应单独规划。
