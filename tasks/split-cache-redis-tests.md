# FastAPI Redis 缓存测试拆分

## 目标

- 将 `fastapi/tests/test_cache_redis.py` 按 Redis 缓存行为职责拆成多个小测试文件。
- 保持 `RedisCache` 对外行为、测试断言和异常暴露语义不变。
- 降低单文件维护成本，避免后续继续在一个测试类里堆叠所有 Redis 缓存场景。

## 非目标

- 不修改 `fastapi/app/core/cache_redis.py` 运行时代码。
- 不调整缓存 key 前缀、TTL 语义、异常返回值或清理行为。
- 不引入新的 mock 成功路径、fallback 或跳过测试。
- 不修改 API、数据库、前端或产品文档。

## 当前事实

- 当前分支基于 `master` 最新提交 `3649d79` 创建。
- `fastapi/tests/test_cache_redis.py` 当前为 268 行，集中覆盖连接获取、key 生成、读取、写入、删除、存在性检查和批量清理。
- `RedisCache` 运行时代码位于 `fastapi/app/core/cache_redis.py`，本轮只做测试结构治理。

## 决策日志

- 方案 A：只把原测试类按方法顺序拆成多个测试文件。
  - 优点：行为风险最低，迁移成本低。
  - 缺点：少量 mock 构造重复会保留。
- 方案 B：新增共享 fixture 文件，集中创建 Redis mock。
  - 优点：减少重复。
  - 缺点：当前重复很浅，共享 fixture 反而会降低单测可读性，并扩大变更面。
- 结论：采用方案 A。优先保持测试场景直接可读，只抽出清理错误场景所需的测试辅助类。

## 执行计划

- [x] 串行：创建 Redis 缓存连接与 key 测试文件。
- [x] 串行：创建 Redis 缓存读写测试文件。
- [x] 串行：创建 Redis 缓存删除、存在性与清理测试文件。
- [x] 串行：删除原 `fastapi/tests/test_cache_redis.py` 聚合大文件。
- [x] 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_cache_redis_*.py -q`
- `cd fastapi && uv run ruff check tests/test_cache_redis_*.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已建立任务计划。
- 已将原 Redis 缓存测试按连接/key、读写、删除/存在性/清理拆成 3 个文件。
- 已完成目标测试、FastAPI 聚合质量门禁、文档校验和 diff 检查。

## 验证结果

- `cd fastapi && uv run pytest tests/test_cache_redis_*.py -q`：19 passed，3 warnings。
- `cd fastapi && uv run ruff check tests/test_cache_redis_*.py`：All checks passed。
- `cd fastapi && make quality`：565 passed，5 warnings，覆盖率 88.05%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只拆分 `fastapi/tests/test_cache_redis.py`，未修改 `RedisCache` 运行时代码、缓存契约、API、数据库或前端；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后 3 个测试文件分别为 42、141、109 行，均低于 300 行；Document-refresh: not-needed，原因：本轮是测试结构治理，不改变用户可见 API、数据库事实或产品文档内容；剩余风险是 Redis 缓存运行时代码本身仍保留既有未覆盖分支，但本轮未扩大该风险。
