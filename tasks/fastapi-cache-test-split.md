# FastAPI 缓存测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_cache.py` 从 521 行单文件拆分为职责清晰的小测试文件。
- 保持 `app/core/cache.py` 的运行时行为、测试断言和 mock 语义不变。
- 所有新增测试文件低于 300 行，降低后续缓存服务拆分和回归定位成本。

## 非目标

- 不修改 `fastapi/app/core/cache.py` 运行时代码。
- 不改变缓存 key、TTL、Redis mock、异常处理或警告捕获断言。
- 不引入新的 fixture、mock 成功路径或静默 fallback。

## 当前事实

- `fastapi/tests/test_cache.py` 当前 521 行，是当前 FastAPI 自有测试中最大的单文件。
- 文件内包含 `FailingAsyncIterator`、`FailingScanRedis` 两个 Redis 清理错误辅助类。
- `TestMemoryCache` 覆盖内存缓存读写、TTL、删除、存在性、清理与过期清扫。
- `TestRedisCache` 覆盖 Redis 客户端获取、key 前缀、读写、删除、存在性和清理错误。
- `TestCacheService` 覆盖服务初始化、`get_or_set` 与 `is_using_redis`。
- `TestCacheKeys` 覆盖缓存 key 模板格式化。

## 决策日志

- 方案 A：按职责拆成 `test_cache_memory.py`、`test_cache_redis.py`、`test_cache_service.py`、`test_cache_keys.py`。
  - 优点：边界与被测类一致，文件体量可控，后续定位直接。
  - 缺点：会新增 4 个测试文件，需要确保导入和 mock 路径不漂移。
- 方案 B：只拆 Redis 测试，其他保留在原文件。
  - 优点：改动更少。
  - 缺点：原文件仍承担多个职责，不能彻底解决 521 行单文件问题。
- 方案 C：抽共享 fixture 后按同步/异步测试拆分。
  - 优点：可减少局部 import 重复。
  - 缺点：当前测试没有复杂共享夹具，抽象会增加不必要间接层。

推荐方案：采用方案 A。按被测类拆分，Redis 错误辅助类随 Redis 测试文件放置，删除原 `test_cache.py`。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/test_cache_memory.py`，迁移 `TestMemoryCache`。
- [x] P3 串行：新增 `fastapi/tests/test_cache_redis.py`，迁移 Redis 辅助类和 `TestRedisCache`。
- [x] P4 串行：新增 `fastapi/tests/test_cache_service.py`，迁移 `TestCacheService`。
- [x] P5 串行：新增 `fastapi/tests/test_cache_keys.py`，迁移 `TestCacheKeys`。
- [x] P6 串行：删除原 `fastapi/tests/test_cache.py`，确保没有重复测试或孤儿引用。
- [x] P7 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P8 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_cache_memory.py tests/test_cache_redis.py tests/test_cache_service.py tests/test_cache_keys.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 缓存测试拆分已完成：原 521 行 `test_cache.py` 已按被测类拆为内存缓存、Redis 缓存、缓存服务和缓存键模板 4 个测试文件，所有新增测试文件均低于 300 行，运行时代码未修改。验证通过：目标测试（44 passed）、FastAPI `make quality`（539 passed，覆盖率 85.44%）、文档校验和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮只拆分缓存测试文件和任务状态，不修改运行时代码、缓存行为、Redis mock 语义、错误处理或警告捕获断言；安全检查未发现新增 secret、硬编码凭据、无依据 fallback 或跳过测试；复杂度检查通过，新增测试文件均低于 300 行；Document-refresh: not-needed，原因：本轮只调整内部测试组织，不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `fastapi/app/core/cache.py` 仍为 353 行，后续如继续缓存模块治理应单独规划运行时代码拆分。
