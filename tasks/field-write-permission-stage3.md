# 字段写入权限第三阶段执行计划

## 目标

- 建立用户敏感字段写入权限最小闭环。
- 普通管理员即使拥有用户新增或编辑权限，也不能写入 `mobile/email`。
- 拥有字段写入权限或超级管理员可以写入 `mobile/email`。
- Django 与 FastAPI 保持同一写入拒绝行为。

## 非目标

- 本轮不处理操作日志写入权限；日志由系统中间件生成，没有公开编辑入口。
- 本轮不修改个人中心资料维护路径。
- 本轮不新增字段权限配置 UI。
- 本轮不改变字段读取脱敏逻辑。

## 当前事实

- Django 用户写入入口位于 `backend/drf_admin/apps/system/views/users.py` 的 `UsersViewSet`。
- Django 用户写入校验位于 `backend/drf_admin/apps/system/serializers/users.py` 的 `UsersSerializer.validate`。
- FastAPI 用户写入入口位于 `fastapi/app/api/v1/system/user_routes/mutation.py`。
- FastAPI 用户写入实现位于 `fastapi/app/services/system/user_services/mutation.py` 的 `UserMutationMixin.create/update`。
- 两端已存在字段读取权限 helper，可扩展写入权限判断。

## 决策日志

- 新增独立权限码 `system:users:field:write`，不复用 `system:users:field:plain`。
- 字段写入权限只控制后台用户管理接口的 `mobile/email` 写入。
- 无字段写入权限时，请求中只要显式包含 `mobile/email` 且值非空，就拒绝。
- 超级管理员默认拥有字段写入权限。

## 执行计划

- [x] RED：补 Django 用户创建/更新敏感字段写入拒绝与授权通过测试。
- [x] RED：补 FastAPI 用户创建/更新敏感字段写入拒绝与授权通过测试。
- [x] GREEN：实现 Django 字段写入权限 helper 并接入 `UsersSerializer.validate`。
- [x] GREEN：实现 FastAPI 字段写入权限 helper，并让用户写入路由传入 `current_user`。
- [x] 种子与文档：同步默认 admin 权限、架构、API 和技术债说明。
- [x] 验证：运行文档、API、模型和三端质量门禁。

## 进度记录

- 2026-07-05：创建分支 `codex/field-write-permission-stage3` 并建立本计划。
- 2026-07-05：新增双后端用户创建/更新敏感字段写入测试，RED 阶段确认当前无写入拒绝。
- 2026-07-05：Django 与 FastAPI 均接入 `system:users:field:write` 判断，路由请求会传入当前操作者。
- 2026-07-05：同步 `backend/init_data.json`、FastAPI 测试权限树和架构/API/技术债文档。

## 验证结果

- `uv run pytest`（Django）：155 passed。
- `make quality`（FastAPI）：ruff/isort/mypy 通过，610 passed，覆盖率 88.15%。
- `CI=true pnpm --dir frontend run quality`：90 个测试文件、261 个测试通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只控制后台用户管理写入路径，未改变个人中心资料维护路径，符合非目标。
- `mobile/email` 只在请求显式携带非空值时要求 `system:users:field:write` 或 `is_superuser`。
- 默认种子 admin 角色已补字段写入权限，避免全新部署的超级管理员菜单/权限数据缺口。
- 剩余风险：个人中心资料维护、通知等其他对象的字段写入拒绝仍需后续单独评估。
