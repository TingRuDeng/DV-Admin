# Django system 测试管理员用户 helper 抽取

## 目标

- 抽取 Django system 测试中重复的 `create_admin_user()`，降低测试数据维护成本。
- 保持用户、角色、权限种子数据和现有测试断言行为不变。

## 非目标

- 不修改 Django 运行时代码、权限逻辑、模型、序列化器或 API 响应契约。
- 不调整测试断言宽松度，不新增 mock、fallback 或静默降级。
- 不处理 FastAPI 或前端代码。

## 当前事实

- `backend/drf_admin/apps/system/test_menus.py`、`test_dicts.py`、`test_dict_items.py`、`test_roles.py`、`test_departments.py`、`test_notices.py`、`tests.py` 均定义了同名 `create_admin_user()`。
- 这些 helper 都创建 `admin/admin123` 用户，绑定 `超级管理员` 角色和同一组 system 按钮权限。
- 现有 system 测试文件最大 195 行，问题不是单文件超限，而是重复测试夹具导致后续权限种子变更需要多处同步。

## 设计原则

- 只抽测试 helper，不改变测试行为。
- 保留调用点函数名 `create_admin_user()`，降低 diff 和历史定位成本。
- helper 文件放在同一 Django app 下，避免引入跨 app 测试依赖。

## 方案对比

- 方案 A：继续保留各文件本地 helper，仅做格式统一。
  - 优点：风险最低。
  - 缺点：重复根因仍在，后续权限码变更仍需多处同步。
- 方案 B：新增 `backend/drf_admin/apps/system/test_helpers.py`，集中提供 `create_admin_user()`。
  - 优点：改动范围仍限测试，能消除重复根因。
  - 缺点：多个测试文件需要同步替换导入。
- 方案 C：抽成跨 Django/FastAPI 共享权限种子。
  - 优点：理论复用更多。
  - 缺点：跨技术栈耦合过重，本轮不采用。

## 推荐方案

- 采用方案 B。
- 新增 `backend/drf_admin/apps/system/test_helpers.py::create_admin_user()`。
- 从 7 个 system 测试文件移除本地重复 helper，改为导入共享 helper。

## 执行计划

- [ ] 串行：新增共享 `create_admin_user()`。
- [ ] 串行：替换 system 测试文件中的本地重复 helper。
- [ ] 串行：运行 system 定向测试。
- [ ] 串行：运行 Django 后端全量测试、Ruff 和仓库文档门禁。

## 验证矩阵

- `cd backend && uv run pytest drf_admin/apps/system -q`
- `cd backend && uv run ruff check drf_admin/apps/system`
- `cd backend && uv run pytest`
- `cd backend && uv run ruff check .`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已完成只读分析，确认 7 个 system 测试文件存在重复管理员用户 helper。
- 已新增 `backend/drf_admin/apps/system/test_helpers.py::create_admin_user()`，并将 7 个 system 测试文件切换为共享 helper。

## 验证结果

- `cd backend && uv run pytest drf_admin/apps/system -q`：51 passed。
- `cd backend && uv run ruff check drf_admin/apps/system`：All checks passed。
- `cd backend && uv run pytest`：105 passed。
- `cd backend && uv run ruff check .`：All checks passed。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：符合；只抽取 Django system 测试管理员用户 helper，未改运行时代码。
- 安全检查：未修改认证、权限、模型、序列化器或 API 响应契约；未新增 secret。
- 测试与验证：已完成 system 定向测试、Django 后端全量测试、Ruff 和仓库文档门禁。
- 复杂度检查：新增 `test_helpers.py` 为 60 行；被修改测试文件均低于 300 行。
- Document-refresh: not-needed；原因：本轮只调整测试内部 helper 组织，未改变对外文档入口或运行命令。
- 剩余风险：远端 CI 尚未执行。
- 潜在技术债：FastAPI 和 Django 仍有其他测试夹具可继续按模块收敛，但不属于本轮范围。
- 结论：通过。
