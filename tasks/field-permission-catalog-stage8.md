# 字段权限目录补齐阶段 8

## 目标

- 补齐已经由 Django/FastAPI 运行时校验的字段权限码，使其进入可分配权限目录。
- 新增目录守卫，避免后续出现“代码校验了权限码，但 seed/fixture 无法授予”的漂移。

## 非目标

- 不改变字段脱敏、写入拒绝和数据范围行为。
- 不修改前端 UI。
- 不新增业务对象字段权限。

## 当前事实

- Django 与 FastAPI 当前均声明 6 个字段权限码。
- `backend/init_data.json` 当前只收录 `system:users:field:write` 与 `system:notices:target:write`。
- `fastapi/tests/fixtures/permissions.py` 当前只收录上述两个写权限。

## 决策日志

- 采用字段权限码契约目录 + seed/fixture 校验，不做运行时自动补权限。
- 普通用户角色不默认拥有字段权限。
- admin 角色 seed 收录全部字段权限，便于初始化后完整管理。

## 执行计划

- [x] 新建字段权限码契约目录。
- [x] 接入根 API 契约校验。
- [x] 补齐 Django 初始权限树。
- [x] 补齐 FastAPI 测试权限 fixture。
- [x] 更新架构与技术债文档。
- [x] 执行最小充分验证。

## 进度记录

- 2026-07-06：用户确认计划，创建 `codex/field-permission-catalog-stage8` 分支。
- 2026-07-06：新增字段权限码契约与双后端目录测试。
- 2026-07-06：补齐 Django 初始权限树和 FastAPI 测试权限 fixture，字段权限码进入可分配目录。

## 验证结果

- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `python3 -m py_compile scripts/field_permission_contracts.py scripts/field_permission_contract_validation.py scripts/validate_api_contracts.py`：通过。
- `cd backend && uv run ruff check .`：通过。
- `cd backend && uv run pytest`：169 passed。
- `cd fastapi && make quality`：627 passed，覆盖率 88.25%。

## Review 小结

- 本轮只处理字段权限目录可分配性和目录守卫，未修改脱敏、写入拒绝、数据范围和前端行为。
