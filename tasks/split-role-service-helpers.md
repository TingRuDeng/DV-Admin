# FastAPI 角色服务 helper 拆分

## 目标

- 将 `fastapi/app/services/system/role_service.py` 中的角色输出转换、更新字段构建、菜单输出转换等纯 helper 拆入专用模块。
- 保持 `RoleService` 的公开方法、RBAC 权限语义、缓存清理和 API 响应结构不变。
- 降低 `role_service.py` 文件复杂度，为后续角色服务继续治理留出清晰边界。

## 非目标

- 不修改角色、权限、菜单的数据模型和数据库表结构。
- 不修改角色 API 路径、权限码、缓存 key 或缓存 TTL。
- 不调整角色创建、更新、分配菜单、删除的数据库写入顺序。
- 不引入新的 fallback、mock 成功路径或静默降级。

## 当前事实

- `fastapi/app/services/system/role_service.py` 当前 270 行，同时包含服务编排、输出转换、更新字段构建和菜单输出转换。
- 现有测试已拆分为查询、写操作、删除、菜单权限等文件，覆盖 `RoleService.get_page()`、`get()`、`create()`、`update()`、`assign_menus()`、`get_menu_ids()`、`get_menus()`。
- 低风险拆分点集中在纯 helper：`RoleOut` 构建、`RoleWithPermissions` 构建、`RoleUpdate` 字段过滤、角色菜单列表转换。

## 设计原则

- `role_service.py` 保留服务入口和数据库写操作编排。
- 新 helper 不访问数据库、不持有全局状态，只接收模型或 schema 参数并返回结构化结果。
- 不改变缓存清理时机，避免 RBAC 变更后权限状态陈旧。
- 不改测试夹具和 API 契约，只补充 helper 级测试锁定边界。

## 方案对比

### 方案 A：新增 `role_serializers.py`

- 做法：迁移 `RoleOut`、`RoleWithPermissions`、更新字段构建和菜单 item 构建 helper。
- 优点：改动最小，纯函数容易测试，服务层职责更清晰。
- 缺点：服务类仍保留查询和写操作编排。

### 方案 B：拆成 query/mutation/menu/cache 多个 mixin

- 做法：按职责把整个 `RoleService` 拆成多个 mixin 或子服务。
- 优点：最终结构更细。
- 缺点：本轮会触碰更多数据库路径和导入关系，容易扩大 RBAC 回归面。

## 推荐方案

- 采用方案 A。它能先移走无状态重复转换逻辑，降低文件复杂度，同时保持服务层行为稳定。
- 淘汰方案 B 的原因：角色服务虽然接近 300 行，但当前主要风险是 RBAC 语义稳定性，过度拆分写路径不符合小步推进。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/services/system/role_serializers.py`，迁移角色输出、详情输出、更新字段和菜单输出 helper。
- [x] P2 串行：更新 `fastapi/app/services/system/role_service.py`，使用 helper，保留原公开方法和缓存清理逻辑。
- [x] P3 串行：新增 `fastapi/tests/test_role_serializers.py`，覆盖纯 helper 的字段映射、更新字段过滤和菜单类型过滤。
- [x] P4 串行：更新 `tasks/todo.md` 当前任务状态。
- [x] P5 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_role_serializers.py tests/test_role_service_query.py tests/test_role_service_mutation.py tests/test_role_service_menu.py tests/test_role_service_delete.py -q`
- `cd fastapi && uv run ruff check app/services/system/role_service.py app/services/system/role_serializers.py tests/test_role_serializers.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## HARD-GATE

- 本线程已有用户确认“按顺序推进”，本轮按该确认继续执行。
- 若执行中发现需要修改角色 API、权限码、数据库模型、缓存 key 或写入顺序，立即停止并回到规划阶段。

## 进度记录

- [x] 已完成只读分析，确认本轮只拆纯 helper，不触碰 RBAC 写语义。
- [x] 已完成角色输出、详情输出、更新字段和菜单输出 helper 拆分。
- [x] 已补充 helper 级测试，覆盖字段映射、权限 ID 保留、更新字段过滤和菜单类型过滤。

## 验证结果

- 首轮目标验证失败：`role_service.py` 仍保留 `Any` 类型注解但导入被移除，已恢复最小导入。
- `cd fastapi && uv run ruff check app/services/system/role_service.py app/services/system/role_serializers.py tests/test_role_serializers.py`：通过。
- `cd fastapi && uv run pytest tests/test_role_serializers.py tests/test_role_service_query.py tests/test_role_service_mutation.py tests/test_role_service_menu.py tests/test_role_service_delete.py -q`：32 passed，3 warnings。
- `cd fastapi && make quality`：565 passed，5 warnings，覆盖率 88.05%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分角色服务纯 helper，不修改角色 API、权限码、数据库模型、缓存 key 或写入顺序。
- 安全检查未发现新增 secret、mock 假成功、静默 fallback 或权限绕过；RBAC 写操作仍由 `RoleService` 原方法编排。
- 复杂度检查通过，`role_service.py` 已从 270 行降至 210 行，新增 `role_serializers.py` 为 65 行，目标测试文件为 85 行。
- Document-refresh: not-needed，原因：本轮只调整内部 helper 组织，不改变用户可见 API、数据库结构或产品文档事实。
- 剩余风险：`role_service.py` 仍包含查询、写操作、菜单权限和缓存清理编排；后续若继续治理应按 query/mutation/menu/cache 独立切片推进。
