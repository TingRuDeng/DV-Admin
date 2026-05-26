# 测试权限夹具小范围治理计划

## 目标

- 拆分 `fastapi/tests/conftest.py` 中过长的权限种子构造逻辑。
- 统一 Django 历史测试数据中的菜单权限码命名，减少 `system:menus:*` 与 `system:permissions:*` 混用。
- 保持测试行为不变，只治理测试基础设施和测试数据表达。

## 非目标

- 不改生产接口、权限依赖、数据库模型或前端页面。
- 不重构无关测试夹具。
- 不调整业务权限模型。

## 当前事实

- `fastapi/tests/conftest.py` 的 `test_permissions` 与 `test_role` 承担权限树、按钮权限和角色绑定，文件已超过 600 行。
- FastAPI 当前生产权限码已由 `fastapi/tests/test_permission_contracts.py` 固定为 `system:permissions:*`、`system:dictitems:*` 和用户细分权限。
- Django 多个历史测试文件仍构造 `system:menus:*` 测试权限数据，包括 `backend/drf_admin/apps/system/test_menus.py`、`test_dicts.py`、`test_dict_items.py`、`test_roles.py`、`tests.py`、`test_departments.py`、`test_notices.py` 与 `backend/drf_admin/apps/oauth/tests.py`。

## 决策日志

- 方案 A：只替换 Django 历史测试里的 `system:menus:*`。改动最小，但不解决 FastAPI 夹具过大问题。
- 方案 B：拆 FastAPI 权限夹具，同时替换 Django 历史测试权限码。能同时解决两个已知技术债，影响范围仍局限在测试。
- 方案 C：进一步抽象跨 Django/FastAPI 的共享权限种子。范围过大，会引入跨技术栈耦合，本轮不采用。
- 执行中发现 `backend/drf_admin/apps/system/test_menus.py::MenusTreeTestCase.test_get_menus_tree` 使用未注册的 `/api/v1/system/menus/tree/`。旧权限码会让请求提前 403，统一为真实权限码后暴露 404；测试已改为现有菜单树列表接口 `/api/v1/system/menus/`。
- 复杂度复核发现 `fastapi/tests/conftest.py` 拆分权限后仍超过 300 行；已继续把数据库生命周期和同步 ASGI 客户端拆到 `fastapi/tests/fixtures/`，保持改动范围只限测试基础设施。

推荐方案：方案 B。

## 执行计划

- [x] 在 `fastapi/tests/fixtures/permissions.py` 新增权限树构造 helper。
- [x] 将 `fastapi/tests/conftest.py::test_permissions` 改为调用 helper。
- [x] 将 `fastapi/tests/conftest.py::test_role` 的权限绑定列表改为 helper 返回的稳定集合。
- [x] 替换 Django 历史测试数据中的 `system:menus:*` 为 `system:permissions:*`。
- [x] 执行最小验证和全量后端门禁。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_permission_contracts.py tests/test_menus.py tests/test_dict_items.py tests/test_users.py`
- `cd fastapi && make quality`
- `cd backend && uv run ruff check . && perl -e 'alarm shift; exec @ARGV' 60 uv run pytest`

## Review 小结

- P1 已完成，`cd fastapi && uv run pytest tests/test_permission_contracts.py tests/test_menus.py tests/test_dict_items.py tests/test_users.py` 通过，18 passed。
- P2 已完成，`cd backend && uv run pytest drf_admin/apps/system/test_menus.py drf_admin/apps/system/test_departments.py drf_admin/apps/oauth/tests.py drf_admin/apps/system/test_dicts.py drf_admin/apps/system/test_dict_items.py drf_admin/apps/system/test_notices.py drf_admin/apps/system/tests.py drf_admin/apps/system/test_roles.py` 通过，64 passed。
- P3 已完成，`cd fastapi && make quality` 通过，502 passed，覆盖率 81.16%；`cd backend && uv run ruff check . && perl -e 'alarm shift; exec @ARGV' 60 uv run pytest` 通过，80 passed。

## HARD-GATE

用户确认前不进行代码修改。
