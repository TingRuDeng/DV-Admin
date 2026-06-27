# 拆分 Django settings 配置构建职责

## 目标

- 将 `backend/drf_admin/settings.py` 中缓存、Channels 和日志配置的构建逻辑拆到专用 helper 模块。
- 保持所有 Django 设置值、环境变量语义、缓存别名、日志文件名和 Channels 行为不变。
- 增加设置 helper 的目标测试，避免后续配置拆分时发生行为漂移。

## 执行计划

- [x] 串行：新增 `backend/drf_admin/settings_helpers.py`，承接 Redis 地址、缓存配置、Channels 配置和日志配置构建。
- [x] 串行：更新 `backend/drf_admin/settings.py`，只保留配置编排和公开设置变量。
- [x] 串行：新增或更新 Django 目标测试，覆盖 Redis 与本地缓存分支、Channels 分支和日志文件路径。
- [x] 串行：运行 Django 后端验证、仓库契约校验和 diff 检查。
- [x] 串行：执行 review-gate 并记录结论。

## 边界

- 不修改 API 路径、响应结构、数据库模型、迁移或前端调用。
- 不新增 fallback，不改变缺失 Redis 配置时当前本地缓存行为。
- 不改动生产环境变量名称和默认值。

## 并行评估

- 本轮不启用 subagent。原因：改动集中在 Django 设置模块和一个测试文件，写冲突集中，串行更清晰。

## 验证命令

- `cd backend && uv run ruff check .`
- `cd backend && uv run pytest`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 scripts/validate_api_contracts.py .`
- `python3 scripts/validate_model_contracts.py .`
- `python3 scripts/validate_route_components.py .`
- `python3 scripts/validate_django_migrations.py .`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分 Django settings 配置构建职责，不改变 API、数据库模型、迁移、环境变量名称或运行时配置值。
- 安全检查：未新增硬编码 secret；敏感词扫描命中仅来自既有 `SECRET_KEY`、`REDIS_PWD`、JWT 环境变量读取和本任务边界说明。
- 测试与验证：目标 settings helper 测试 14 passed；Django 全量测试 116 passed；Django ruff、文档/API/模型/路由组件/迁移契约校验、脚本编译和 `git diff --check` 均通过。
- 复杂度检查：`settings.py` 从 469 行降至 259 行，`settings_helpers.py` 为 228 行，新增测试为 132 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只调整内部配置组织结构，不改变用户可见功能、API 或数据库结构。
- 剩余风险：后续继续拆分 settings 时，应避免把 `settings_helpers.py` 继续扩到 300 行以上。
