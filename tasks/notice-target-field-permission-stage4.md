# 通知目标字段写入权限第四阶段执行计划

## 目标

- 建立通知 `targetUserIds` 字段写入权限最小闭环。
- 普通管理员即使拥有通知新增或编辑权限，也不能创建或更新指定用户通知。
- 拥有通知目标字段写入权限或超级管理员可以写入 `targetUserIds`。
- Django 与 FastAPI 保持同一写入拒绝行为。

## 非目标

- 本轮不修改个人中心资料维护路径。
- 本轮不新增字段权限配置 UI。
- 本轮不改变通知发布、撤回、我的通知已读逻辑。
- 本轮不改变通知响应字段集合。

## 当前事实

- Django 通知写入入口位于 `backend/drf_admin/apps/system/views/notices.py` 的 `NoticesViewSet`。
- Django 通知写入校验位于 `backend/drf_admin/apps/system/serializers/notices.py` 的 `NoticesSerializer`。
- FastAPI 通知写入入口位于 `fastapi/app/api/v1/system/notices.py`。
- FastAPI 通知写入实现位于 `fastapi/app/services/system/notice_service.py` 的 `NoticeService.create/update`。
- 前端个人中心当前只提交 `name`，不在本轮字段写入权限范围。

## 决策日志

- 新增独立权限码 `system:notices:target:write`，不复用通知新增或编辑权限。
- 字段写入权限只控制后台通知创建/更新路径中的指定用户目标字段。
- 请求显式创建或更新为 `targetType=2` 且携带非空 `targetUserIds` 时，要求 `system:notices:target:write` 或 `is_superuser`。
- 超级管理员默认拥有通知目标字段写入权限。

## 执行计划

- [x] RED：补 Django 通知创建/更新指定用户字段写入拒绝与授权通过测试。
- [x] RED：补 FastAPI 通知创建/更新指定用户字段写入拒绝与授权通过测试。
- [x] GREEN：实现 Django 通知目标字段写入权限 helper 并接入 `NoticesSerializer.validate`。
- [x] GREEN：实现 FastAPI 通知目标字段写入权限 helper，并让通知写入服务接收当前操作者。
- [x] 种子与文档：同步默认 admin 权限、架构、API 和技术债说明。
- [x] 验证：运行文档、API、模型和三端必要质量门禁。

## 进度记录

- 2026-07-05：创建分支 `codex/notice-target-write-permission-stage4` 并建立本计划。
- 2026-07-05：新增双后端通知创建/更新指定用户目标字段写入测试，RED 阶段确认当前无写入拒绝。
- 2026-07-05：Django 与 FastAPI 均接入 `system:notices:target:write` 判断，路由请求会传入当前操作者。
- 2026-07-05：同步 `backend/init_data.json`、FastAPI 测试权限树和架构/API/技术债文档。

## 验证结果

- `uv run pytest`（Django）：159 passed。
- `uv run ruff check .`（Django）：通过。
- `make quality`（FastAPI）：ruff/isort/mypy 通过，614 passed，覆盖率 88.17%。
- `CI=true pnpm --dir frontend run quality`：90 个测试文件、261 个测试通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `python3 -m json.tool backend/init_data.json`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只控制后台通知创建/更新路径中非空 `targetUserIds` 的写入，不改变通知响应字段集合。
- `targetUserIds` 只在请求显式携带非空值时要求 `system:notices:target:write` 或 `is_superuser`。
- 默认种子 admin 角色已补通知目标字段写入权限，避免全新部署的超级管理员权限数据缺口。
- 剩余风险：通知字段读取脱敏、通知数据范围过滤和个人中心资料维护仍需后续单独评估。
