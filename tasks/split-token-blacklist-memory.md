# 拆分 Token 黑名单内存降级存储

## 目标

- 将 `fastapi/app/services/token_blacklist.py` 中的内存降级存储职责拆入专用 helper。
- 保持 `TokenBlacklistService` 的公开方法、测试 patch 入口和 Redis 行为不变。
- 降低认证撤销服务的单文件复杂度，避免 Redis、Token 解析和内存存储逻辑继续混在同一个类中。

## 非目标

- 不修改 JWT 解码、过期时间计算或安全策略。
- 不修改 Redis Key 规则和现有 `token_blacklist_keys.py`。
- 不修改登出、刷新 Token 或用户批量撤销 API 契约。
- 不引入新的 fallback、mock 或静默降级路径。

## 当前事实

- `fastapi/app/services/token_blacklist.py` 当前为 288 行，仍承担 Redis 访问、Token 黑名单、用户批量撤销、清理和内存降级状态。
- `fastapi/app/services/token_blacklist_keys.py` 已承接 Key 生成与内存黑名单过期清理。
- 现有测试通过 `app.services.token_blacklist.decode_token`、`get_token_expiration` 和 `redis_manager` 进行 patch，拆分时必须保持这些入口稳定。

## 方案对比

- 方案 A：拆出 Token 解码和 TTL 计算。能减少部分行数，但会改变现有测试 patch 点，迁移成本高且容易误伤行为。
- 方案 B：拆出内存降级存储为 `TokenBlacklistMemoryStore`。外部行为和测试 patch 点稳定，主服务只负责 Redis 优先流程和错误处理。

## 推荐方案

采用方案 B。它对运行时行为影响最小，能把状态读写与过期清理集中到独立对象，同时保留主服务的公开方法和测试入口。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/services/token_blacklist_memory.py`，承接内存黑名单和用户撤销标记的读写清理。
- [x] P2 串行：调整 `TokenBlacklistService` 使用 `TokenBlacklistMemoryStore`，保留 `_memory_blacklist` 与 `_memory_user_revocations` 兼容属性。
- [x] P3 串行：补充或调整目标测试，锁定内存降级 helper 行为和现有服务行为。
- [x] P4 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_token_blacklist_keys.py tests/test_token_blacklist_memory_fallback.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py -q`
- `cd fastapi && uv run ruff check app/services/token_blacklist.py app/services/token_blacklist_keys.py app/services/token_blacklist_memory.py tests/test_token_blacklist_memory_fallback.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
- `wc -l fastapi/app/services/token_blacklist.py fastapi/app/services/token_blacklist_memory.py fastapi/app/services/token_blacklist_keys.py`

## 进度记录

- [x] 已确认当前分支为 `codex/split-token-blacklist-memory`，从最新 `master` 创建。
- [x] 已读取 `token_blacklist.py`、`token_blacklist_keys.py` 和 token 黑名单相关测试。
- [x] 已新增 `TokenBlacklistMemoryStore` 并让 `TokenBlacklistService` 委托内存降级读写。

## 验证结果

- `cd fastapi && uv run pytest tests/test_token_blacklist_keys.py tests/test_token_blacklist_memory.py tests/test_token_blacklist_memory_fallback.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py -q`：26 passed。
- `cd fastapi && uv run ruff check app/services/token_blacklist.py app/services/token_blacklist_keys.py app/services/token_blacklist_memory.py tests/test_token_blacklist_memory.py tests/test_token_blacklist_memory_fallback.py`：通过。
- `wc -l fastapi/app/services/token_blacklist.py fastapi/app/services/token_blacklist_memory.py fastapi/app/services/token_blacklist_keys.py fastapi/tests/test_token_blacklist_memory.py`：`token_blacklist.py` 为 292 行，新增 helper 42 行。
- `cd fastapi && make quality`：通过，554 passed，覆盖率 87.29%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只将 Token 黑名单内存降级状态拆入 `TokenBlacklistMemoryStore`，保留 `TokenBlacklistService` 的公开方法、Redis 优先流程、测试 patch 入口和兼容属性；安全检查未发现新增 secret、mock、无依据 fallback 或静默降级；测试与验证已覆盖目标 token 黑名单测试、FastAPI 全量质量门禁、文档校验、脚本编译、diff 检查和行数边界；复杂度检查通过，`token_blacklist.py` 为 292 行，新增 helper 为 42 行；Document-refresh: not-needed，原因：本轮只调整内部服务结构，不改变对外 API、认证策略或数据库结构；剩余风险是 `token_blacklist.py` 仍接近 300 行，后续若继续扩展 Token 撤销策略，应优先拆 Redis 写入或 Token TTL 计算职责。
