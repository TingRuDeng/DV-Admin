# FastAPI Token 黑名单测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_token_blacklist.py` 从 384 行单文件拆分为职责清晰的小测试文件。
- 保持 `TokenBlacklistService` 现有行为断言、Redis mock、内存降级断言和异常断言不变。
- 抽出共享的服务状态重置夹具，避免拆分后各测试文件重复维护全局实例清理逻辑。

## 非目标

- 不修改 `fastapi/app/services/token_blacklist.py` 运行时代码。
- 不改变 token 黑名单 key、Redis TTL、用户批量撤销、删除清理或内存降级行为。
- 不引入新的 mock 成功路径、跳过测试或静默 fallback。

## 当前事实

- `fastapi/tests/test_token_blacklist.py` 当前 384 行，只有 `TestTokenBlacklistService` 一个测试类。
- 测试内容可按行为分为 key/redis 属性、添加与检查单个 token、用户批量撤销、删除清理、Redis 不可用时内存降级。
- 当前测试通过 `setup_method` 重置全局 `token_blacklist_service` 状态，拆分后更适合改为 `autouse` 夹具集中处理。
- `fastapi/app/services/token_blacklist.py` 当前 302 行，本轮不处理运行时代码体量。

## 决策日志

- 方案 A：抽 `token_blacklist_fixtures.py`，再按 key、token、user_revocation、cleanup、memory_fallback 拆分测试文件。
  - 优点：职责边界清楚，文件体量可控，共享状态重置逻辑集中。
  - 缺点：文件数量增加，需要确认 autouse 夹具在所有拆分文件中生效。
- 方案 B：只拆内存降级测试，其他保留在原文件。
  - 优点：改动更少。
  - 缺点：原文件仍然偏大，不能解决主要维护成本。
- 方案 C：同步拆分 `TokenBlacklistService` 运行时代码。
  - 优点：可同时降低服务文件体量。
  - 缺点：会把测试组织调整和运行时重构混在一起，风险不必要升高。

推荐方案：采用方案 A。本轮只拆测试文件和共享状态重置夹具，运行时代码后续单独规划。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/token_blacklist_fixtures.py`，迁移全局服务状态重置夹具。
- [x] P3 串行：新增 `fastapi/tests/test_token_blacklist_keys.py`，迁移 key 和 redis 属性测试。
- [x] P4 串行：新增 `fastapi/tests/test_token_blacklist_tokens.py`，迁移添加与检查单个 token 测试。
- [x] P5 串行：新增 `fastapi/tests/test_token_blacklist_user_revocation.py`，迁移用户批量撤销测试。
- [x] P6 串行：新增 `fastapi/tests/test_token_blacklist_cleanup.py`，迁移移除 token 和清除用户撤销测试。
- [x] P7 串行：新增 `fastapi/tests/test_token_blacklist_memory_fallback.py`，迁移 Redis 不可用内存降级测试。
- [x] P8 串行：删除原 `fastapi/tests/test_token_blacklist.py`，确保没有重复测试或孤儿引用。
- [x] P9 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P10 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_token_blacklist_keys.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py tests/test_token_blacklist_memory_fallback.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Token 黑名单测试拆分已完成：原 384 行 `test_token_blacklist.py` 已拆为 key/redis 属性、单 token 黑名单、用户批量撤销、删除清理、内存降级 5 个测试文件，并抽出 `token_blacklist_fixtures.py` 集中重置全局服务状态；运行时代码未修改。验证通过：目标测试（23 passed）、FastAPI `make quality`（539 passed，覆盖率 85.44%）、文档校验和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮只拆分 Token 黑名单测试文件和任务状态，不修改 `TokenBlacklistService` 运行时代码、Redis TTL、用户撤销、删除清理或内存降级行为；安全检查未发现新增 secret、硬编码凭据、无依据 fallback 或跳过测试；复杂度检查通过，新增测试文件均低于 300 行；Document-refresh: not-needed，原因：本轮只调整内部测试组织，不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/app/services/token_blacklist.py` 仍为 302 行，后续如继续治理应单独规划运行时代码拆分。
