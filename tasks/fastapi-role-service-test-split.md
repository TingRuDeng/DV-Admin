# FastAPI 角色服务测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_role_service.py` 从 456 行单文件拆分为职责清晰的小测试文件。
- 保持 `RoleService` 现有行为断言、异常断言和数据库夹具语义不变。
- 抽出主测试文件内的角色与权限共享夹具，避免拆分后重复定义。

## 非目标

- 不修改 `fastapi/app/services/system/role_service.py` 运行时代码。
- 不合并、不删除 `fastapi/tests/test_role_service_more.py` 中的补充测试。
- 不调整角色 API、权限菜单、缓存清理或模型契约。

## 当前事实

- `fastapi/tests/test_role_service.py` 当前 456 行，包含 2 个共享夹具和 8 个测试类。
- 查询类测试包括 `TestRoleServiceGetPage`、`TestRoleServiceGet`、`TestRoleServiceGetOptions`。
- 写操作测试包括 `TestRoleServiceCreate`、`TestRoleServiceUpdate`。
- 删除测试包括 `TestRoleServiceDelete`、`TestRoleServiceBatchDelete`。
- 菜单权限测试包括 `TestRoleServiceGetMenuIds`、`TestRoleServiceGetMenus`。
- `fastapi/tests/test_role_service_more.py` 当前 205 行，已有独立补充断言，本轮不改。

## 决策日志

- 方案 A：抽 `role_service_fixtures.py`，再按 query、mutation、delete、menu 拆分主测试文件。
  - 优点：职责边界清楚，夹具集中复用，所有新增文件体量可控。
  - 缺点：需要确认 pytest 夹具加载方式不影响 `test_role_service_more.py`。
- 方案 B：只拆写操作或删除测试，查询继续留在原文件。
  - 优点：改动更小。
  - 缺点：原文件仍然偏大，后续维护仍集中冲突。
- 方案 C：同时合并 `test_role_service_more.py` 的重复覆盖。
  - 优点：可能减少重复测试。
  - 缺点：会把去重决策和文件拆分混在一起，增加行为回归风险。

推荐方案：采用方案 A。本轮只拆原 `test_role_service.py`，保留 `test_role_service_more.py` 原状，并在目标测试中一起运行，确认夹具和断言没有冲突。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/role_service_fixtures.py`，迁移共享角色和权限夹具。
- [x] P3 串行：新增 `fastapi/tests/test_role_service_query.py`，迁移分页、详情和选项测试。
- [x] P4 串行：新增 `fastapi/tests/test_role_service_mutation.py`，迁移创建和更新测试。
- [x] P5 串行：新增 `fastapi/tests/test_role_service_delete.py`，迁移删除和批量删除测试。
- [x] P6 串行：新增 `fastapi/tests/test_role_service_menu.py`，迁移菜单 ID 和菜单列表测试。
- [x] P7 串行：删除原 `fastapi/tests/test_role_service.py`，确保没有重复测试或孤儿引用。
- [x] P8 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P9 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_role_service_query.py tests/test_role_service_mutation.py tests/test_role_service_delete.py tests/test_role_service_menu.py tests/test_role_service_more.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 角色服务测试拆分已完成：原 456 行 `test_role_service.py` 已拆为查询、写操作、删除、菜单权限 4 个职责测试文件，并抽出 `role_service_fixtures.py` 复用角色与权限夹具；`test_role_service_more.py` 保持原状。验证通过：目标测试（44 passed）、FastAPI `make quality`（539 passed，覆盖率 85.44%）、文档校验和 `git diff --check`。
- Review-gate：finished；Spec 符合度通过，本轮只拆分主角色服务测试文件和任务状态，不修改 `RoleService` 运行时代码、角色 API、权限菜单、缓存清理或模型契约；安全检查未发现新增 secret、硬编码凭据、无依据 fallback 或跳过测试；复杂度检查通过，新增测试文件均低于 300 行；Document-refresh: not-needed，原因：本轮只调整内部测试组织，不改变用户可见 API、数据库结构或产品文档事实；剩余风险是 `test_role_service_more.py` 仍与主角色服务测试存在部分覆盖重叠，后续若要去重应单独规划。
