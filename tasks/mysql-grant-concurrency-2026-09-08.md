# MySQL 并发授权回归

> 交付更新：本轮代码已通过 PR [#376](https://github.com/TingRuDeng/DV-Admin/pull/376) 合并到 `master`（`add845e`），合并前后 CI 均 9/9 通过；未部署。以下“本地提交/未推送”描述保留提交前阶段记录。

## 目标与边界

- 分支：`codex/mysql-grant-concurrency`，基于 `origin/master` 的 `81d428a`。
- 补双后端真实 MySQL 并发撤权/授权、旧快照和事务回滚守卫；仅修复测试证实的关联读取缺陷。
- 不更改授权政策、对外 API、前端、数据库结构、真实凭据或生产数据；实现阶段不自动提交，后续交付仅做本地提交，不推送或部署。

## 实施

- [x] 独立 MySQL 8 容器，仅监听本机随机端口，临时数据卷。
- [x] 每个后端/隔离级别使用随机 `dv_admin_grant_test_<uuid>` 库，结束后仅删除本次创建的库。
- [x] 两个独立 ORM 连接控制执行顺序，第三个连接查询锁等待表，不以固定 sleep 推断竞争。
- [x] 六个场景：撤权先提交、授权先提交、实际关联写入后回滚、旧快照下撤销权限/角色关系/部门范围。
- [x] 两端关联查询改为锁定当前读；FastAPI 不使用会丢失锁标志的 `values_list()`。
- [x] CI 新增双后端 MySQL 任务，依赖按已有 uv 锁安装；根测试覆盖拒绝非测试库/远端地址及失败清理。
- [x] 最终门禁与 diff 复核，确认随机测试库无残留并删除本次专用容器。

## 验证证据

- RED：FastAPI `REPEATABLE READ` 的旧快照场景返回 `committed`，应为 `denied`；Django 同隔离级别的常规撤权先提交场景即返回 `committed`。两者均已实际观察到独立连接等待行锁。
- GREEN：MySQL 8.0.43，两端 × `READ COMMITTED` / `REPEATABLE READ` × 六个场景，共 24 项通过；20 个竞争场景观察到 InnoDB 锁等待，4 个回滚场景断言标量与关联均恢复。
- Django 全量：Ruff 通过，pytest 290 passed / 1 skipped（单独启用的浏览器测试）。
- FastAPI `make -C fastapi quality`：Ruff/isort、mypy 151 个文件、迁移检查通过；856 passed / 1 skipped，覆盖率 89.25%。首轮因 uv 缓存沙箱权限被阻止，获准重跑通过；测试进程使用 minLength=15 及合规临时初始密码，不修改本地环境文件。
- 根 `python3 -m unittest discover -s tests -p 'test_*.py'`：41 tests passed，含 3 个新测试库安全/清理守卫。
- 文档 generic、API、模型、动态路由组件、Django 迁移静态校验均通过；Python 编译、workflow YAML/双后端矩阵解析和 `git diff --check` 通过。
- 最终代码重跑两端 MySQL 24 项全部通过；本机仅使用专用容器的随机端口 51430，库清理后查询无残留，容器 `dv-admin-grant-mysql-20260908` 已删除。
- 提交前复核：业务实现未再变化；重新运行 Django 权限回归 12 passed、FastAPI 权限回归 16 passed、根测试 41 passed；两端 lint、文档/API/模型校验通过。全量后端及 MySQL 证据沿用上述同一实现的验证，本次未重建 MySQL 容器。

## 复现

只连接独立测试 MySQL 8，测试账户需创建/删除测试库及读取 `performance_schema` 的权限。
`GRANT_MYSQL_PORT` 指向其本机端口；`GRANT_MYSQL_PASSWORD` 使用该临时实例的测试密码。
Django 需要已有 `.env.test`（CI 单独生成），运行器覆盖测试配置，不复制或改写本地配置文件。

```bash
backend/.venv/bin/python scripts/verify_mysql_grants.py --backend django
fastapi/.venv/bin/python scripts/verify_mysql_grants.py --backend fastapi
python3 -m unittest discover -s tests -p 'test_mysql_grant_testing.py'
```

## Review 与剩余风险

- 测试通过只证明上述交错顺序与回滚，不代表生产负载、全部授权写组合或死锁重试已验收。
- 新增关联锁可能增加竞争；菜单/部门拓扑并发、交叉管理员编辑、批量写操作仍需专门测试。
- 随机测试库清理包含子进程失败/超时路径；进程被外部强制终止时仍应删除专用测试容器，不连接生产实例运行。
- 前端未改动，本轮不重跑浏览器或前端构建；远端 CI 尚未执行。
- 本地 Django Python 3.13、FastAPI Python 3.10；新增 CI 沿用 Django 3.11 / FastAPI 3.10。未将本地通过解释为远端 CI 通过，未变更远端分支保护必需检查。
- 实际业务改动仅两个 `grant_boundary.py`，其余为测试、CI、文档和任务记录；保留原有 `.pnpm-store/`。交付范围为本地提交，未推送、开 PR、合并或部署。
