# FastAPI 缓存核心模块拆分治理计划

## 目标

- 将 `fastapi/app/core/cache.py` 从 353 行职责混合文件拆分为小模块。
- 保持 `from app.core.cache import MemoryCache / RedisCache / CacheService / CacheKeys / cache_service` 兼容入口不变。
- 让内存缓存、Redis 缓存、服务编排和缓存键模板各自拥有清晰文件边界。

## 非目标

- 不改变缓存行为、Redis 连接策略、内存缓存 TTL 语义或 `get_or_set` 兼容逻辑。
- 不新增 fallback、mock 成功路径或静默降级规则。
- 不修改业务服务调用点、缓存键命名或测试断言。

## 当前事实

- `fastapi/app/core/cache.py` 当前 353 行，是当前 FastAPI 最大运行时代码文件之一。
- 文件内同时包含 `CacheBackend`、`MemoryCache`、`RedisCache`、`CacheService`、全局 `cache_service` 和 `CacheKeys`。
- 现有测试已按职责拆分为 `test_cache_memory.py`、`test_cache_redis.py`、`test_cache_service.py`、`test_cache_keys.py`。
- 业务调用点仍统一从 `app.core.cache` 导入缓存类型或实例，兼容入口需要保留。

## 决策日志

- 方案 A：拆出 `cache_backend.py`、`cache_memory.py`、`cache_redis.py`、`cache_service.py`、`cache_keys.py`，保留 `cache.py` 作为兼容导出入口。
  - 优点：调用点不变，职责边界清楚，测试可直接复用。
  - 缺点：文件数量增加，需要防止循环导入。
- 方案 B：直接修改所有调用点改从新模块导入。
  - 优点：导入来源更精确。
  - 缺点：影响范围扩大，不利于本轮低风险结构拆分。
- 方案 C：只拆 `CacheKeys` 或只拆 Redis 后端。
  - 优点：改动更小。
  - 缺点：`cache.py` 仍然过大，核心职责耦合没有明显改善。

推荐方案：采用方案 A。本轮保留 `app.core.cache` 兼容导出入口，只拆内部实现文件。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/core/cache_backend.py`，迁移 `CacheBackend`。
- [x] P3 串行：新增 `fastapi/app/core/cache_memory.py`，迁移 `MemoryCache`。
- [x] P4 串行：新增 `fastapi/app/core/cache_redis.py`，迁移 `RedisCache`。
- [x] P5 串行：新增 `fastapi/app/core/cache_service.py`，迁移 `CacheService` 与 `cache_service`。
- [x] P6 串行：新增 `fastapi/app/core/cache_keys.py`，迁移 `CacheKeys`。
- [x] P7 串行：将 `fastapi/app/core/cache.py` 收缩为兼容导出入口。
- [x] P8 串行：执行目标缓存测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P9 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_cache_memory.py tests/test_cache_redis.py tests/test_cache_service.py tests/test_cache_keys.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

缓存核心模块拆分已完成：`cache.py` 已从 353 行收缩为 20 行兼容导出入口；`CacheBackend`、`MemoryCache`、`RedisCache`、`CacheService/cache_service` 和 `CacheKeys` 已分别迁移到专用模块。既有 `from app.core.cache import ...` 调用点保持不变。

验证通过：目标缓存测试 44 passed；FastAPI `make quality` 539 passed，覆盖率 85.47%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整缓存核心代码组织，不改变缓存行为、Redis 连接策略、TTL 语义、缓存键模板或业务调用点；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后所有新增文件均小于 300 行；Document-refresh: not-needed，原因：本轮不改变用户可见功能、API 或产品文档事实；剩余风险是 README/TESTING 中存在历史 `cache` 示例命名，与当前实际导出 `cache_service` 不完全一致，后续可单独做文档示例校准。
