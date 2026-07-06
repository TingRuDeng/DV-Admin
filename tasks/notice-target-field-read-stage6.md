# 通知目标字段读取权限第六阶段执行计划

## 目标

- 后台通知和我的通知输出中的 `targetUserIds` 不再对无字段原文权限用户暴露。
- Django 与 FastAPI 保持同一字段读取行为。
- 保持响应字段集合稳定：无权限时返回空数组，不移除字段。

## 非目标

- 本轮不修改通知内容 `content` 的读取策略。
- 本轮不新增字段权限配置 UI。
- 本轮不修改通知写入权限、数据范围、我的通知可见性和已读逻辑。
- 本轮不修改数据库结构。

## 当前事实

- Django 通知输出位于 `backend/drf_admin/apps/system/serializers/notices.py` 的 `NoticesSerializer`，覆盖后台列表和我的通知。
- Django 我的通知输出位于 `backend/drf_admin/apps/system/views/notices.py` 的 `NoticesAPIView.get`。
- FastAPI 通知输出位于 `fastapi/app/services/system/notice_serializers.py` 的 `notice_to_page_out`、`notice_to_form_out`、`notice_to_my_page_out`。
- 两端字段权限 helper 已覆盖用户与日志字段读取，可扩展通知目标用户字段读取权限。

## 决策日志

- 新增权限码：`system:notices:target:plain`。
- 超级管理员默认可看原文。
- 无权限时保留 `targetUserIds` 字段但返回空数组，避免破坏前端字段契约。
- 字段读取权限只影响响应输出，不改变查询范围和写入校验。

## 执行计划

- [x] RED：补 Django 通知目标字段读取权限测试。
- [x] RED：补 FastAPI 通知目标字段读取权限测试。
- [x] GREEN：实现 Django 通知目标字段读取权限 helper 并接入通知 serializer。
- [x] GREEN：实现 FastAPI 通知目标字段读取权限 helper 并接入通知输出转换。
- [x] 文档：同步架构、API、技术债和任务状态。
- [x] 验证：运行文档、API、模型和受影响质量门禁。

## 进度记录

- 2026-07-06：创建分支 `codex/notice-target-field-read-stage6` 并建立本计划。
- 2026-07-06：补充 Django 后台列表和我的通知目标用户字段读取 RED 测试，确认无权限时仍返回真实 ID。
- 2026-07-06：补充 FastAPI 后台列表、表单和我的通知目标用户字段读取 RED 测试，确认无权限时仍返回真实 ID 或服务不接收当前用户。
- 2026-07-06：Django 接入 `system:notices:target:plain`，后台列表和我的通知 GET 输出无权限时 `targetUserIds` 返回空数组。
- 2026-07-06：FastAPI 接入 `system:notices:target:plain`，读路径输出无权限时 `targetUserIds` 返回空数组。
- 2026-07-06：同步 `docs/ARCHITECTURE.md`、`docs/API_ENDPOINTS.md` 和 `docs/TECH_DEBT.md`。

## 验证结果

- RED：Django 新增 4 条目标字段读取测试中 2 条无权限路径失败，证明原实现会泄露真实 `targetUserIds`。
- RED：FastAPI 新增 6 条目标字段读取测试中 4 条失败，证明后台列表、表单和我的通知读路径尚未统一处理该字段。
- GREEN：`uv run pytest drf_admin/apps/system/test_notices.py -q`，22 passed。
- GREEN：`uv run pytest tests/test_notice_service_admin_query.py tests/test_notice_service_status.py tests/test_notice_service_mutation.py tests/test_notice_service_detail.py tests/test_notice_service_my_page.py tests/test_notices.py tests/runtime_api_contracts/test_notice_write_contracts.py -q`，53 passed。
- 局部 Ruff：Django 与 FastAPI 受影响文件均通过。
- Django：`uv run ruff check .`，All checks passed。
- Django：`uv run pytest`，166 passed。
- FastAPI：`make quality`，ruff、isort、mypy、pytest 全部通过；623 passed，覆盖率 88.22%。
- 前端：`CI=true pnpm --dir frontend run quality`，90 个测试文件、261 个测试通过。
- 文档：`python3 -m py_compile scripts/validate_docs.py`，通过。
- 文档：`python3 scripts/validate_docs.py . --profile generic`，通过。
- 契约：`python3 scripts/validate_api_contracts.py .`，通过。
- 模型：`python3 scripts/validate_model_contracts.py .`，通过。

## Review 小结

- 本轮只收敛通知目标用户字段读权限，未改变写入权限、数据范围、我的通知可见性和数据库结构。
- Django 与 FastAPI 均保留 `targetUserIds` 字段集合稳定；无 `system:notices:target:plain` 时返回空数组，有权限或超级管理员保留原文 ID。
- 剩余字段读取债务仍是通知正文 `content` 和其他未纳入字段权限体系的业务字段。
- 交付前审查终态：finished；Spec 符合度通过，安全检查未发现硬编码 secret，复杂度未越过本轮改动风险线。
- Document-refresh: needed；原因：字段读取权限边界变化已同步到架构、API 和技术债文档。
