# 字段读取权限第二阶段执行计划

## 目标

- 建立字段读取权限最小闭环。
- 普通管理员读取用户和操作日志敏感字段时只能看到脱敏值。
- 拥有字段原文权限或超级管理员读取敏感字段时返回原文。
- Django 与 FastAPI 保持同一字段读取行为。

## 非目标

- 本轮不实现字段移除，保持响应字段集合稳定。
- 本轮不实现字段写入拒绝。
- 本轮不新增字段权限配置 UI。
- 本轮不扩展到通知、角色、部门等其他对象。

## 当前事实

- 用户列表字段集合已由 `scripts/api_field_contracts.py` 锁定，前端展示 `mobile/email`。
- 操作日志字段集合已由 `logs_out` 契约锁定，输出含 `requestBody/responseBody/ip`。
- Django 用户输出位于 `backend/drf_admin/apps/system/serializers/users.py` 的 `UsersSerializer`。
- Django 日志输出位于 `backend/drf_admin/apps/system/serializers/logs.py` 的 `OperationLogSerializer`。
- FastAPI 用户输出位于 `fastapi/app/services/system/user_services/serializers.py`。
- FastAPI 日志输出位于 `fastapi/app/services/system/log_serializers.py`。

## 决策日志

- 采用“保留字段但脱敏”，避免破坏既有字段契约和前端表格结构。
- 权限码采用 `system:users:field:plain` 与 `system:logs:field:plain`。
- 超级管理员默认可看原文。
- 字段读取权限只影响响应输出，不影响数据库查询和写入校验。

## 执行计划

- [x] RED：补 Django/FastAPI 用户与日志字段脱敏测试。
- [x] GREEN：实现 Django 字段权限 helper 并接入用户/日志 serializer。
- [x] GREEN：实现 FastAPI 字段权限 helper 并接入用户/日志输出转换。
- [x] 契约与文档：同步架构、技术债和任务状态。
- [x] 验证：运行文档、API、模型和三端质量门禁。

## 进度记录

- 2026-07-05：创建分支 `codex/field-read-permission-stage2` 并建立本计划。
- 2026-07-05：新增双后端用户与日志字段读取测试，RED 阶段确认普通管理员仍可读取原文。
- 2026-07-05：Django 与 FastAPI 均接入字段原文权限，新增测试已转绿。

## 验证结果

- `uv run pytest`（Django）：151 passed。
- `make quality`（FastAPI）：ruff/isort/mypy 通过，606 passed，覆盖率 88.05%。
- `CI=true pnpm --dir frontend run quality`：90 个测试文件、261 个测试通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `git diff --check`：通过。

## Review 小结

- 字段集合保持不变，只在输出阶段脱敏，符合本轮非目标。
- Django 与 FastAPI 均使用同一组字段原文权限码，用户和日志新增行为测试覆盖无权限脱敏与有权限原文两类路径。
- 剩余风险：通知等其他对象的字段读取控制、字段写入拒绝仍属于后续阶段。
