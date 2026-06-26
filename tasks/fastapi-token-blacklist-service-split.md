# FastAPI Token 黑名单服务拆分治理计划

## 目标

- 将 `fastapi/app/services/token_blacklist.py` 从 302 行降到 300 行以内。
- 抽出 Token 黑名单 Key 生成和内存过期清理等无状态 helper，降低服务类职责密度。
- 保持 `app.services.token_blacklist.TokenBlacklistService` 和 `token_blacklist_service` 导入路径不变。

## 非目标

- 不修改 JWT 解码、过期时间计算或认证依赖逻辑。
- 不改变 Redis Key 格式、TTL、批量撤销语义或内存降级行为。
- 不新增 mock 假成功、静默 fallback 或跳过测试逻辑。

## 当前事实

- `fastapi/app/services/token_blacklist.py` 当前 302 行，是当前 FastAPI 最大业务文件。
- 文件内同时包含服务类、Redis 访问、Token 黑名单 Key 生成、用户撤销 Key 生成和内存过期清理。
- `fastapi/app/api/deps.py` 和 `fastapi/app/api/v1/oauth/routes/session.py` 通过 `app.services.token_blacklist` 使用全局服务实例。
- Token 黑名单测试已按职责拆分在 `fastapi/tests/test_token_blacklist_*.py`，覆盖 key、单 token、用户批量撤销、清理和内存降级场景。

## 决策日志

- 方案 A：新增 `fastapi/app/services/token_blacklist_keys.py`，迁移 Key 生成与内存清理 helper，服务类保留兼容方法并委托 helper。
  - 优点：改动小，外部导入路径和测试入口保持稳定，能直接解决超限文件问题。
  - 缺点：服务类仍保留 Redis 读写流程，后续若继续扩展仍可能再次接近 300 行。
- 方案 B：将 `token_blacklist.py` 改为 package，按 tokens、user_revocation、cleanup 拆多文件。
  - 优点：职责拆分更彻底。
  - 缺点：Python 模块到 package 的迁移影响导入、patch 路径和测试夹具，当前 302 行问题不需要这么大改动。
- 方案 C：只压缩注释或空行。
  - 优点：最小 diff。
  - 缺点：没有改善职责边界，属于表面降行数。

推荐方案：采用方案 A。本轮解决明确超限点，同时保持认证运行路径稳定。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/services/token_blacklist_keys.py`，迁移 Key 生成和内存清理 helper。
- [x] P3 串行：更新 `fastapi/app/services/token_blacklist.py`，保留原私有方法并委托新 helper。
- [x] P4 串行：执行 Token 黑名单目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P5 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_token_blacklist_keys.py tests/test_token_blacklist_tokens.py tests/test_token_blacklist_user_revocation.py tests/test_token_blacklist_cleanup.py tests/test_token_blacklist_memory_fallback.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Token 黑名单服务拆分已完成：`fastapi/app/services/token_blacklist.py` 从 302 行降至 288 行，新增 `fastapi/app/services/token_blacklist_keys.py` 承接黑名单 Key、用户撤销 Key 和内存过期清理 helper。
- 验证通过：Token 黑名单目标测试 `23 passed`；FastAPI `make quality` 通过，结果为 `551 passed`、覆盖率 `87.08%`；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。
- Review-gate：finished；Spec 符合度通过，本轮保留 `app.services.token_blacklist.TokenBlacklistService` 和 `token_blacklist_service` 导入路径，不修改 JWT 解码、Redis TTL、批量撤销语义或内存降级行为。
- 安全检查未发现新增 secret、mock 假成功、静默 fallback 或跳过测试；复杂度检查通过，本轮新增文件 37 行，目标文件 288 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只做内部服务职责拆分，不改变对外 API、数据库结构、认证契约或用户可见流程。
- 剩余风险：`fastapi/app/services/system/log_service.py`、`fastapi/app/services/system/notice_service.py` 和 `fastapi/app/db/import_django_data.py` 仍接近 300 行，后续可继续按职责拆分治理。
