# FastAPI Token 黑名单记录 helper 拆分

## 目标

- 将 `fastapi/app/services/token_blacklist.py` 中的黑名单记录构造、TTL 计算和用户撤销记录构造拆入纯 helper。
- 降低 `TokenBlacklistService` 的职责密度，保持公开方法、Redis/内存降级和测试 patch 点不变。

## 非目标

- 不修改 JWT 解码逻辑、Redis 连接策略、内存降级策略或认证依赖。
- 不改变 Token 黑名单、用户批量撤销、清理接口的返回语义。
- 不处理 `fastapi/app/api/deps.py` 等其他临界文件。

## 当前事实

- `fastapi/app/services/token_blacklist.py` 当前 292 行，承担服务编排、Redis 分支、内存分支、TTL 计算和 Redis 写入值构造。
- 相关测试通过 `patch("app.services.token_blacklist.decode_token")` 和 `patch("app.services.token_blacklist.get_token_expiration")` 固定现有解码 patch 点。
- 现有 helper 已有 `token_blacklist_keys.py` 和 `token_blacklist_memory.py`，适合继续按“无状态记录构造”和“存储实现”分层。

## 设计原则

- 纯函数优先，helper 不访问 Redis、不访问 settings、不解码 JWT。
- 保留 `TokenBlacklistService` 的公开 API 和兼容属性。
- 新 helper 直接单测，服务层继续跑既有 token 黑名单测试。

## 方案对比

- 方案 A：把 `decode_token()` 和 `get_token_expiration()` 也移动到 helper。
  - 优点：服务方法更短。
  - 缺点：会破坏现有测试 patch 点，风险不必要。
- 方案 B：只移动 TTL、黑名单值和用户撤销记录构造。
  - 优点：不影响 patch 点和外部行为，能拆出纯逻辑。
  - 缺点：`TokenBlacklistService` 仍保留 Redis/内存编排职责。
- 方案 C：引入 Redis repository 抽象。
  - 优点：分层更彻底。
  - 缺点：本轮风险和改动面过大，容易变成架构重写。

## 推荐方案

- 采用方案 B。
- 新增 `fastapi/app/services/token_blacklist_records.py`：
  - `TokenBlacklistRecord`
  - `UserRevocationRecord`
  - `build_token_blacklist_record()`
  - `build_user_revocation_record()`
  - `is_token_revoked_by_time()`
- 更新 `TokenBlacklistService` 调用新 helper。
- 将内存存储兼容访问器拆入 `fastapi/app/services/token_blacklist_compat.py`，保持测试兼容入口但降低主服务文件体量。
- 新增 `fastapi/tests/test_token_blacklist_records.py` 覆盖纯 helper 行为。

## 执行计划

- [ ] 串行：新增记录 helper 和单测。
- [ ] 串行：更新 `TokenBlacklistService` 使用 helper。
- [ ] 串行：运行 token 黑名单定向测试。
- [ ] 串行：运行 FastAPI `make quality` 和仓库文档门禁。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_token_blacklist_records.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py tests/test_token_blacklist_memory_fallback.py -q`
- `cd fastapi && uv run ruff check app/services/token_blacklist.py app/services/token_blacklist_records.py tests/test_token_blacklist_records.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已完成只读分析，确认本轮只拆纯记录构造 helper。
- 已新增 `token_blacklist_records.py` 和对应单测，并将 `TokenBlacklistService` 切换到记录 helper。
- 复核发现主服务文件行数未下降，已继续把内存存储兼容访问器拆入 `token_blacklist_compat.py`。

## 验证结果

- 首轮 `cd fastapi && uv run pytest ... -q`：23 passed，1 failed；失败原因为新 helper 单测手写了错误的用户撤销 Key 期望，已改为现有 `get_user_revocation_key()` 的实际契约 `token_blacklist:user:{id}`。
- 首轮 `cd fastapi && make quality`：mypy 失败；原因是 `TokenBlacklistCompatibilityMixin` 未声明由子类提供的 `_memory_store` 属性，已补充类型声明。
- `cd fastapi && uv run pytest tests/test_token_blacklist_records.py tests/test_token_blacklist_keys.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py tests/test_token_blacklist_memory_fallback.py -q`：27 passed，3 warnings。
- `cd fastapi && uv run ruff check app/services/token_blacklist.py app/services/token_blacklist_records.py app/services/token_blacklist_compat.py tests/test_token_blacklist_records.py`：All checks passed。
- `cd fastapi && uv run mypy app`：Success。
- `cd fastapi && make quality`：569 passed，5 warnings，覆盖率 88.11%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：符合；拆出黑名单记录构造 helper 和兼容访问器，未改变公开服务 API。
- 安全检查：未修改 JWT 解码、认证依赖、Redis 连接策略、内存降级策略或 secret。
- 测试与验证：已补 `test_token_blacklist_records.py`，并完成 token 黑名单定向测试、mypy、Ruff、FastAPI `make quality` 和仓库文档门禁。
- 复杂度检查：`token_blacklist.py` 从 292 行降至 272 行；新增 `token_blacklist_records.py` 74 行，`token_blacklist_compat.py` 35 行，均低于 300 行。
- Document-refresh: not-needed；原因：本轮只调整内部服务实现和测试，不改变对外 API、启动命令或文档入口。
- 剩余风险：远端 CI 尚未执行。
- 潜在技术债：`token_blacklist.py` 仍保留 Redis/内存编排职责，后续可单独评估是否抽 Redis 操作层。
- 结论：通过。
