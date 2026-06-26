# FastAPI deps token helper 拆分

## 目标

- 将 `fastapi/app/api/deps.py` 中的 Authorization 头解析、access token payload 校验、用户 ID 提取拆入纯 helper。
- 降低 `get_current_user()` 的分支密度，保持认证、黑名单、用户查询和权限检查行为不变。

## 非目标

- 不修改 `PermissionChecker`、`RoleChecker`、`require_permissions()` 或路由权限契约。
- 不修改 JWT 生成、Token 黑名单服务、数据库模型或 API 响应格式。
- 不引入新的 fallback、mock 或静默降级。

## 当前事实

- `fastapi/app/api/deps.py` 当前 259 行，包含 token 提取、黑名单检查、JWT payload 校验、用户查询、权限检查器和角色检查器。
- 当前没有专门覆盖 Authorization 头解析和 payload 校验边界的单测。
- 相关路由通过 `Depends(get_current_user)`、`require_permissions()` 和 `require_roles()` 使用该模块。

## 设计原则

- helper 保持同步纯函数，便于单测。
- `get_current_user()` 继续负责异步编排：黑名单检查、用户撤销检查、数据库查询和 request.state 写入。
- 不改变错误消息，避免影响前端或契约测试。

## 方案对比

- 方案 A：只把 Authorization 头解析抽成函数。
  - 优点：改动最小。
  - 缺点：`get_current_user()` 仍混合 token 类型、subject 校验等分支。
- 方案 B：抽出 token 提取、access payload 校验和 user_id 提取。
  - 优点：降低主函数分支密度，同时不触碰异步依赖和数据库行为。
  - 缺点：需要新增 helper 单测覆盖错误边界。
- 方案 C：把 `get_current_user()` 整体拆成异步服务类。
  - 优点：分层更彻底。
  - 缺点：会影响依赖注入结构，范围过大。

## 推荐方案

- 采用方案 B。
- 新增 `fastapi/app/api/deps_tokens.py`：
  - `extract_bearer_token()`
  - `require_access_token_payload()`
  - `require_token_user_id()`
- 新增 `fastapi/tests/test_deps_tokens.py` 覆盖 token helper 行为。
- 更新 `fastapi/app/api/deps.py::get_current_user()` 调用 helper。

## 执行计划

- [x] 串行：新增 token helper 和单测。
- [x] 串行：更新 `get_current_user()` 调用 helper。
- [x] 串行：运行 deps token 定向测试和相关认证测试。
- [x] 串行：运行 FastAPI `make quality` 和仓库文档门禁。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_deps_tokens.py tests/test_oauth_login.py tests/test_oauth_session.py tests/test_token_blacklist_tokens.py -q`
- `cd fastapi && uv run ruff check app/api/deps.py app/api/deps_tokens.py tests/test_deps_tokens.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已完成只读分析，确认本轮只拆同步 token helper。
- 已新增 `deps_tokens.py` 和对应单测，并将 `get_current_user()` 切换为 helper 编排。
- 已完成本地定向验证、FastAPI 全量质量门禁、仓库文档门禁和 diff 空白检查。

## 验证结果

- `cd fastapi && uv run pytest tests/test_deps_tokens.py tests/test_oauth_login.py tests/test_oauth_session.py tests/test_token_blacklist_tokens.py -q`：25 passed，3 warnings。
- `cd fastapi && uv run ruff check app/api/deps.py app/api/deps_tokens.py tests/test_deps_tokens.py`：All checks passed。
- `cd fastapi && make quality`：ruff、isort、mypy 通过；577 passed，5 warnings，覆盖率 88.35%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- Spec 符合：本轮只拆同步 token helper，未修改权限检查器、JWT 生成、Token 黑名单服务、数据库模型或 API 响应格式。
- 安全边界：`get_current_user()` 仍保留黑名单检查、用户批量撤销检查、数据库查询、用户状态检查和 request.state 写入；helper 只负责 token 提取、access payload 校验和用户 ID 提取。
- 复杂度变化：`fastapi/app/api/deps.py` 从 259 行降至 242 行；新增 `fastapi/app/api/deps_tokens.py` 46 行；新增 `fastapi/tests/test_deps_tokens.py` 86 行。
- 文档判断：未变更 API、数据库模型、架构流程或运行命令，不需要同步产品文档。
- 剩余风险：本地门禁已通过，远端 CI 尚未执行。
