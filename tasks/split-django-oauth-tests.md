# Django OAuth 测试拆分

## 目标

- 将 `backend/drf_admin/apps/oauth/tests.py` 按职责拆分到多个测试文件，消除单文件 300 行以上的维护压力。
- 保持 Django OAuth 登录、刷新、用户信息、菜单、登出和首页接口测试行为不变。

## 非目标

- 不修改 OAuth 运行时代码、URL、序列化器、模型或 API 响应契约。
- 不调整测试断言语义，不新增兼容分支、mock 或静默 fallback。
- 不处理前端或 FastAPI 代码。

## 当前事实

- `backend/drf_admin/apps/oauth/tests.py` 当前 323 行，包含共享建数 helper 和 6 个测试类。
- 测试覆盖 `UserLoginView`、`RefreshTokenAPIView`、`UserInfoView`、`RoutesAPIView`、`LogoutAPIView`、`HomeAPIView`。
- Django 测试文件发现模式已包含 `test*.py`，系统模块已有多个 `test_*.py` 文件。

## 设计原则

- 按接口职责拆分，不按行数机械拆分。
- 共享建数 helper 放入测试专用 helper 文件，避免重复构造角色、权限和用户。
- 保留现有测试类名和测试方法名，降低 pytest 迁移和历史定位成本。

## 方案对比

- 方案 A：保留 `tests.py`，只拆 helper。
  - 优点：改动最小。
  - 缺点：仍无法解决单文件职责混杂和行数超限问题。
- 方案 B：按登录、刷新、会话、首页拆成多个 `test_*.py` 文件，并移除原 `tests.py`。
  - 优点：职责边界清晰，符合现有系统模块测试组织方式。
  - 缺点：需要确认 pytest 能完整发现迁移后的测试。

## 推荐方案

- 采用方案 B。
- 拆分目标：
  - `backend/drf_admin/apps/oauth/test_helpers.py`：测试建数 helper。
  - `backend/drf_admin/apps/oauth/test_login.py`：登录接口测试。
  - `backend/drf_admin/apps/oauth/test_refresh_token.py`：刷新 Token 接口测试。
  - `backend/drf_admin/apps/oauth/test_session.py`：用户信息、菜单、登出测试。
  - `backend/drf_admin/apps/oauth/test_home.py`：首页接口测试。

## 执行计划

- [ ] 串行：迁移共享 helper。
- [ ] 串行：按职责拆分测试类。
- [ ] 串行：删除旧 `tests.py`，避免重复收集同一测试。
- [ ] 串行：运行 Django OAuth 定向测试。
- [ ] 串行：运行后端质量门禁和仓库文档门禁。

## 验证矩阵

- `cd backend && uv run pytest drf_admin/apps/oauth -q`
- `cd backend && uv run ruff check drf_admin/apps/oauth`
- `cd backend && uv run pytest`
- `cd backend && uv run ruff check .`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已完成只读分析，确认拆分范围仅限 Django OAuth 测试。
- 已拆分 OAuth 测试文件，并移除旧 `backend/drf_admin/apps/oauth/tests.py`。
- 已发现 `backend/TESTING.md` 仍引用旧 `drf_admin.apps.oauth.tests` 路径，并同步更新为当前 pytest 入口。
- 调试记录：`manage.py test drf_admin.apps.oauth` 会触发 Redis 连接失败；当前后端测试权威入口是 `pytest.ini` 配置下的 `uv run pytest`。

## 验证结果

- `cd backend && uv run pytest drf_admin/apps/oauth -q`：17 passed。
- `cd backend && uv run pytest drf_admin/apps/oauth/test_login.py::OAuthLoginTestCase -q`：4 passed。
- `cd backend && uv run ruff check drf_admin/apps/oauth`：All checks passed。
- `cd backend && uv run pytest`：105 passed。
- `cd backend && uv run ruff check .`：All checks passed。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：符合；仅拆分 Django OAuth 测试和同步过期测试文档入口。
- 安全检查：未修改运行时代码、认证逻辑、权限逻辑或 secret。
- 测试与验证：已完成 OAuth 定向测试、登录单类测试、Django 后端全量测试、Ruff 和仓库文档门禁。
- 复杂度检查：拆分后最大文件为 `test_session.py` 123 行，低于 300 行文件约束。
- Document-refresh: needed；原因：旧测试文档引用已删除的 `drf_admin.apps.oauth.tests` 模块。
- 剩余风险：远端 CI 尚未执行。
- 潜在技术债：Django 系统模块仍存在多个重复的 `create_admin_user()` helper，适合后续单独治理。
- 结论：通过。
