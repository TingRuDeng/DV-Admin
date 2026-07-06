# 通知后台数据范围第五阶段执行计划

## 目标

- 后台通知管理列表按当前用户角色 `dataScope/deptIds` 收敛可见通知。
- 后台通知按 ID 管理动作不能绕过数据范围，包括表单、更新、删除、发布和撤回。
- Django 与 FastAPI 以通知 `publisher_id` 映射数据范围，保持一致行为。

## 非目标

- 本轮不修改“我的通知”可见性逻辑。
- 本轮不修改通知已读状态逻辑。
- 本轮不新增通知数据库字段或迁移。
- 本轮不实现通知字段读取脱敏。

## 当前事实

- Django 通知后台列表位于 `backend/drf_admin/apps/system/views/notices.py` 的 `NoticesViewSet.list`，当前基于 `Notices.objects.all()`。
- FastAPI 通知后台列表位于 `fastapi/app/services/system/notice_service.py` 的 `NoticeService.get_page`，当前基于 `Notices.all()`。
- 双后端通知模型均已有 `publisher_id` 字段，可映射到已存在的数据范围用户集合。
- 现有数据范围 helper 已用于用户列表和操作日志列表，可扩展通知后台管理场景。

## 决策日志

- 通知后台管理数据范围按 `publisher_id` 过滤。
- 超级管理员或任一角色 `dataScope=全部数据` 时不过滤。
- “我的通知”继续按 `targetType/targetUserIds` 判断接收人可见性，不复用后台管理数据范围。
- 对按 ID 的后台管理动作，如果通知不在当前用户数据范围内，对外表现为“通知不存在”。

## 执行计划

- [x] RED：补 Django 通知后台列表与按 ID 管理动作数据范围测试。
- [x] RED：补 FastAPI 通知后台列表与按 ID 管理动作数据范围测试。
- [x] GREEN：实现 Django `apply_notice_admin_data_scope` 并接入 `NoticesViewSet.get_queryset`。
- [x] GREEN：实现 FastAPI `apply_notice_admin_data_scope`，并让通知后台 service 接收当前操作者。
- [x] 文档：同步架构与技术债说明。
- [x] 验证：运行文档、API、模型和三端必要质量门禁。

## 进度记录

- 2026-07-06：创建分支 `codex/notice-admin-data-scope-stage5` 并建立本计划。
- 2026-07-06：补充双后端 RED 测试，确认后台通知列表和发布动作可越过发布人部门数据范围。
- 2026-07-06：Django 通过 `NoticesViewSet.get_queryset` 统一接入 `apply_notice_admin_data_scope`。
- 2026-07-06：FastAPI 通过服务层 `current_user` 参数统一接入 `apply_notice_admin_data_scope`，并由后台管理路由传入当前操作者。
- 2026-07-06：同步 `docs/ARCHITECTURE.md`、`docs/API_ENDPOINTS.md` 和 `docs/TECH_DEBT.md` 的通知数据范围事实。

## 验证结果

- RED：`uv run pytest drf_admin/apps/system/test_notices.py::NoticesPublishTestCase::test_publish_rejects_notice_outside_publisher_dept_scope -q`，修复前真实 `PUT` 发布隐藏部门通知返回 200，测试失败。
- GREEN：`uv run pytest drf_admin/apps/system/test_notices.py::NoticesListTestCase::test_admin_list_filters_notices_by_publisher_dept_scope drf_admin/apps/system/test_notices.py::NoticesPublishTestCase::test_publish_rejects_notice_outside_publisher_dept_scope -q`，2 passed。
- GREEN：`uv run pytest tests/test_notice_service_admin_query.py::TestNoticeServiceGetPage::test_get_page_filters_notices_by_publisher_dept_scope tests/test_notice_service_status.py::TestNoticeServicePublish::test_publish_rejects_notice_outside_publisher_dept_scope -q`，2 passed。
- Django：`uv run ruff check .`，通过。
- Django：`uv run pytest`，162 passed。
- FastAPI：`make quality`，616 passed，覆盖率 88.16%。
- 前端：`CI=true pnpm --dir frontend run quality`，90 个测试文件、261 条测试通过。
- 文档：`python3 -m py_compile scripts/validate_docs.py`，通过。
- 文档：`python3 scripts/validate_docs.py . --profile generic`，通过。
- 契约：`python3 scripts/validate_api_contracts.py .`，通过。
- 模型：`python3 scripts/validate_model_contracts.py .`，通过。
- 最终：`git diff --check`，通过。

## Review 小结

- review-gate 通过：实现范围符合第五阶段计划，后台通知管理按 `publisher_id` 接入数据范围，“我的通知”、通知已读状态和数据库结构未被修改。
- 文档已修正为区分 Django/FastAPI 现有路由事实：Django 覆盖列表和按 ID 管理动作，FastAPI 额外覆盖表单查询。
- 2026-07-06 追补：FastAPI 删除越权路径已新增独立服务测试，确认不在 `publisher_id` 数据范围内的通知会返回 `NotFound` 且不会被删除；后续如扩展通知管理动作，应继续复用 `apply_notice_admin_data_scope`。
