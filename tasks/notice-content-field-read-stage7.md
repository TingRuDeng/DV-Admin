# 通知正文字段读取权限第七阶段执行计划

## 目标

- 后台通知管理输出中的 `content` 不再对无字段原文权限用户暴露。
- Django 与 FastAPI 保持同一字段读取行为。
- 保持响应字段集合稳定：无权限时返回脱敏文本，不移除字段。
- “我的通知”继续返回正文，避免破坏收件人阅读通知的产品语义。

## 非目标

- 本轮不修改通知发布、撤回、写入权限。
- 本轮不修改“我的通知”的可见性与已读逻辑。
- 本轮不修改数据库结构。
- 本轮不修改前端 UI。

## 当前事实

- Django 通知输出位于 `backend/drf_admin/apps/system/serializers/notices.py` 的 `NoticesSerializer`。
- Django 后台列表和我的通知都复用 `NoticesSerializer`，因此需要显式区分后台管理输出与我的通知输出。
- FastAPI 通知后台列表、表单和我的通知输出位于 `fastapi/app/services/system/notice_serializers.py`。
- `docs/TECH_DEBT.md` 已记录通知正文 `content` 尚未接入字段读取策略。

## 决策日志

- 新增权限码：`system:notices:content:plain`。
- 超级管理员默认可看后台通知正文原文。
- 后台通知管理读路径无权限时 `content` 返回 `[已脱敏]`。
- 我的通知读路径始终返回正文，因为收件人需要阅读通知内容。
- 字段读取权限只影响响应输出，不改变查询范围、字段集合和写入校验。

## 执行计划

- [x] RED：补 Django 后台通知正文读取权限测试，并确认无权限路径失败。
- [x] RED：补 Django 我的通知正文不脱敏测试。
- [x] RED：补 FastAPI 后台列表和表单正文读取权限测试，并确认无权限路径失败。
- [x] RED：补 FastAPI 我的通知正文不脱敏测试。
- [x] GREEN：实现 Django 通知正文后台读取权限。
- [x] GREEN：实现 FastAPI 通知正文后台读取权限。
- [x] 文档：同步架构、API、技术债和任务状态。
- [x] 验证：运行文档、API、模型和受影响质量门禁。

## 进度记录

- 2026-07-06：创建分支 `codex/notice-content-field-read-stage7` 并建立本计划。
- 2026-07-06：补充 Django/FastAPI 正文读取 RED 测试，确认后台读路径无权限时仍返回正文原文。
- 2026-07-06：Django 后台通知管理输出接入 `system:notices:content:plain`，我的通知正文保持可读。
- 2026-07-06：FastAPI 后台列表和表单输出接入 `system:notices:content:plain`，我的通知正文保持可读。
- 2026-07-06：同步 `docs/ARCHITECTURE.md`、`docs/API_ENDPOINTS.md` 和 `docs/TECH_DEBT.md`。

## 验证结果

- RED：`uv run pytest drf_admin/apps/system/test_notices.py::NoticesListTestCase::test_admin_list_masks_target_users_without_plain_permission drf_admin/apps/system/test_notices.py::NoticesListTestCase::test_admin_list_keeps_content_with_plain_permission drf_admin/apps/system/test_notices.py::NoticesMyPageTestCase::test_my_page_masks_target_users_without_plain_permission -q`，1 failed、2 passed；失败原因为后台列表 `content` 仍返回 `内容`。
- RED：`uv run pytest tests/test_notice_service_admin_query.py::TestNoticeServiceGetPage::test_get_page_masks_target_users_without_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetPage::test_get_page_keeps_content_with_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetForm::test_get_form_masks_target_users_without_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetForm::test_get_form_keeps_content_with_plain_permission tests/test_notice_service_my_page.py::TestNoticeServiceGetMyPage::test_get_my_page_masks_target_users_without_plain_permission -q`，2 failed、3 passed；失败原因为后台列表和表单 `content` 仍返回 `内容`。
- GREEN：`uv run pytest drf_admin/apps/system/test_notices.py::NoticesListTestCase::test_admin_list_masks_target_users_without_plain_permission drf_admin/apps/system/test_notices.py::NoticesListTestCase::test_admin_list_keeps_content_with_plain_permission drf_admin/apps/system/test_notices.py::NoticesMyPageTestCase::test_my_page_masks_target_users_without_plain_permission -q`，3 passed。
- GREEN：`uv run pytest tests/test_notice_service_admin_query.py::TestNoticeServiceGetPage::test_get_page_masks_target_users_without_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetPage::test_get_page_keeps_content_with_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetForm::test_get_form_masks_target_users_without_plain_permission tests/test_notice_service_admin_query.py::TestNoticeServiceGetForm::test_get_form_keeps_content_with_plain_permission tests/test_notice_service_my_page.py::TestNoticeServiceGetMyPage::test_get_my_page_masks_target_users_without_plain_permission -q`，5 passed。
- 受影响 Django：`uv run pytest drf_admin/apps/system/test_notices.py -q`，23 passed。
- 受影响 FastAPI：`uv run pytest tests/test_notice_service_admin_query.py tests/test_notice_service_status.py tests/test_notice_service_mutation.py tests/test_notice_service_detail.py tests/test_notice_service_my_page.py tests/test_notices.py tests/runtime_api_contracts/test_notice_write_contracts.py -q`，55 passed。
- 局部 Ruff：Django 与 FastAPI 受影响文件均通过。
- Django：`uv run ruff check .`，All checks passed。
- Django：`uv run pytest`，167 passed。
- FastAPI：`make quality`，ruff、isort、mypy、pytest 全部通过；625 passed，覆盖率 88.25%。
- 前端：`CI=true pnpm --dir frontend run quality`，90 个测试文件、261 个测试通过。
- 文档：`python3 -m py_compile scripts/validate_docs.py`，通过。
- 文档：`python3 scripts/validate_docs.py . --profile generic`，通过。
- 契约：`python3 scripts/validate_api_contracts.py .`，通过。
- 模型：`python3 scripts/validate_model_contracts.py .`，通过。

## Review 小结

- 交付前审查终态：finished。
- Spec 符合度：通过；本轮只控制后台通知管理 `content` 输出，“我的通知”正文保持原文。
- 安全检查：通过；未发现硬编码 secret，字段权限复用现有 RBAC 权限读取路径。
- 测试与验证：通过；RED 阶段已证明后台正文原文泄露，GREEN 后 Django、FastAPI、前端和契约门禁均通过。
- 复杂度检查：通过；新增函数和改动文件均低于本轮复杂度风险线。
- Document-refresh: needed；原因：后台通知正文读取权限边界变化已同步到架构、API 和技术债文档。
- 剩余风险：其他业务对象字段读取策略仍需后续单独评估。
- 潜在技术债：字段权限码仍分散在双后端常量中，后续如继续扩展字段权限，可考虑抽取共享权限目录。
- 结论：通过。
