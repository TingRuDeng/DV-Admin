---
ai_summary:
  purpose: "记录万级用户数据范围与导入预加载的基线、回归门禁和测量边界。"
  read_when:
    - "修改数据范围过滤或用户导入查询时"
  source_of_truth:
    - "fastapi/tests/test_user_query_performance.py"
    - "backend/drf_admin/apps/system/test_user_query_performance.py"
    - "scripts/query_performance_probe.py"
    - "tests/test_import_lookup_contract.py"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 -m unittest discover -s tests -q"
  stale_when:
    - "数据范围查询、导入预加载、ORM 版本或测试数据规模变化"
---

# 用户查询性能基线

## Purpose

避免数据范围把全量用户 ID 带入应用层，以及小批量导入扫描全库唯一字段。测试约束查询形态和正确结果，不设置机器相关耗时门槛。

## Source of truth

- `fastapi/app/services/system/data_scope.py`
- `backend/drf_admin/apps/system/services/data_scope.py`
- `fastapi/app/services/system/user_services/import_parser.py`
- `backend/drf_admin/apps/system/services/user_import_export.py`
- 两端 `test_user_query_performance.py`、`scripts/query_performance_probe.py`、`tests/test_import_lookup_contract.py`

## Key facts

- 2026-09-07，本机 macOS/SQLite 隔离测试库，10,000 用户、两个部门各 5,000 人。数据准备不计入测量，所有密码为不可登录测试占位符，无真实数据。
- 数据范围测量包含权限范围解析、count 和首屏 10 条；日志与通知各有范围内外一条。权限角色始终从数据库重新读取，不借性能优化恢复跨请求授权缓存。
- 导入测量仅覆盖预加载阶段：文件涉及 1,001 个用户名/手机号，并引用一个有效角色和部门；不包含文件传输、密码哈希、写入、授权图准备。旧代码无输入筛选，仍读入全库 10,000 条；新代码先遍历输入引用，再每批最多 500 项查询。
- 下表为单次实测证据，不是统计基准或生产容量承诺。内存为 tracemalloc 的 Python 峰值字节，不是进程 RSS 或数据库内存。

| 实现/场景 | 查询数 前→后 | 最大参数数 前→后 | 总参数数 前→后 | 耗时 ms 前→后 | Python 峰值 bytes 前→后 |
| --- | --- | --- | --- | --- | --- |
| FastAPI 用户范围 | 5→4 | 5001→2 | 10004→5 | 63.17→3.47 | 1703313→77525 |
| FastAPI 日志范围 | 5→4 | 5001→2 | 10004→5 | 73.45→3.76 | 1570323→34302 |
| FastAPI 通知范围 | 5→4 | 5001→2 | 10004→5 | 60.86→3.61 | 1669581→26236 |
| Django 用户范围 | 5→4 | 5000→2 | 10004→5 | 38.76→5.77 | 1876759→64884 |
| Django 日志范围 | 5→4 | 5000→2 | 10004→5 | 38.28→8.11 | 1859760→47155 |
| Django 通知范围 | 5→4 | 5000→2 | 10004→5 | 40.79→7.26 | 1845063→33322 |
| FastAPI 导入预加载 | 5→9 | 3→500 | 4→2008 | 29.23→26.36 | 3291280→557759 |
| Django 导入预加载 | 4→8 | 1→500 | 1→2005 | 19.54→20.75 | 2420905→450840 |

导入查询数增加是将无限全表预加载改为有界定向查询的成本；不宣称所有规模下耗时都下降。缓存的用户名/手机号分别从 10,000 降到 1,001。

## 查询约束

- 用户直接用部门条件与 SELF 身份的 OR 并集过滤；日志/通知用单列用户子查询，不在 Python 构造可见用户 ID 列表。空角色集合不给任何数据，停用角色不参与，ALL/超管语义不变。
- 导入采用工作表两遍流式读取，只保留引用集合；部门/角色/唯一字段按 500 项拆分查询，角色行锁仍在原事务内，顺序稳定。逐行错误、同文件重复检查、默认部门/角色及意外失败整体回滚不变。
- 运行时测试检查真实结果、SQL 子查询、参数量和查询数；纯规则测试锁定两端打包代码一致及 500/500/1 分块。
- 使用 ORM 自带表达式，参考 [Tortoise Subquery](https://tortoise.github.io/expressions.html#subquery) 与 [Django Subquery](https://docs.djangoproject.com/en/4.2/ref/models/expressions/#subquery-expressions)，不手写拼接 SQL。

## How to verify

在 `fastapi/` 执行（环境覆盖仅用于本地旧配置未升级时的测试）：

```bash
PASSWORD_MIN_LENGTH=15 DEFAULT_PASSWORD='Test-only initial passphrase' uv run pytest tests/test_user_query_performance.py -q -s
```

在 `backend/` 执行：

```bash
uv run pytest drf_admin/apps/system/test_user_query_performance.py -q -s
```

根目录执行 `python3 -m unittest discover -s tests -q`。两端性能用例由既有全量 pytest CI 自动执行；无需显式开启 benchmark 标志。

## Stale when

- ORM/数据库、测试数据分布、授权模型、导入模板或预加载策略变化时重测。
- 新增排序/筛选/关联或逐行序列化逻辑时，本阶段基线不代表完整接口性能。

## 剩余风险

没有新增索引、队列或迁移。MySQL 的执行计划、并发写入锁和真实负载尚待目标部署测量；组织结构授权图仍需必要的部门元数据。超大组织的部门 ID 集合、导出全量输出、逐行哈希/授权/写入、完整列表字段权限查询仍可随数据增长，不以本次基线宣称整个系统性能问题已经解决。
