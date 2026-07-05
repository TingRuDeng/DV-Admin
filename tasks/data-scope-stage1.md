# 数据权限第一阶段执行计划

## 目标

- 为角色增加 `dataScope` 数据范围字段。
- 为角色增加自定义部门范围关系 `deptIds`。
- 用户列表和操作日志列表由后端按当前用户角色数据范围强制过滤。
- Django 与 FastAPI 保持同一外部契约。
- 前端角色表单支持配置数据范围和自定义部门。

## 非目标

- 本轮不实现字段级读写权限。
- 本轮不实现租户隔离。
- 本轮不改变既有菜单、按钮和接口权限码。
- 本轮不依赖前端隐藏数据作为安全边界。

## 当前事实

- Django `Roles` 模型尚无数据范围字段和自定义部门关系。
- FastAPI `Roles` 模型尚无数据范围字段和自定义部门关系。
- 用户列表与日志列表当前按接口权限放行后查询全量数据。
- 前端角色表单仅配置基础信息和菜单权限，`dataScope` 仍是注释字段。

## 决策日志

- 采用角色级 `dataScope` + 角色-部门 M2M。
- 多角色数据范围取并集；任一角色拥有全部数据则不追加过滤。
- 超级管理员默认拥有全部数据。
- 日志列表通过 `OperationLog.user_id` 对应用户部门做过滤，不新增日志冗余部门字段。

## 执行计划

- [x] RED：补 Django/FastAPI 角色字段和越权过滤测试。
- [x] GREEN：实现 Django 模型、迁移、serializer、helper 和查询过滤。
- [x] GREEN：实现 FastAPI 模型、schema、service、helper 和查询过滤。
- [x] 前端：角色表单增加数据范围和自定义部门控件。
- [x] 契约与文档：更新字段契约、模型契约、数据库文档、技术债和 API 报告。
- [x] 验证：运行文档、API、模型、迁移和三端质量门禁。

## 进度记录

- 2026-07-05：创建分支 `codex/data-scope-stage1` 并建立本计划。
- 2026-07-05：补充 Django/FastAPI RED 测试，确认当前均因 `Roles.DATA_SCOPE_*` 缺失失败。
- 2026-07-05：实现 Django 数据范围字段、迁移、serializer、helper 和用户/日志过滤；相关子集 11 passed。
- 2026-07-05：实现 FastAPI 数据范围字段、schema、service、helper 和用户/日志过滤；相关子集 13 passed。
- 2026-07-05：前端角色表单增加数据范围下拉和自定义部门多选树。
- 2026-07-05：同步 API 字段契约、前端字段契约、模型契约、数据库/架构/API/技术债文档，并重新生成 API 契约报告。

## 验证结果

- `uv run pytest`（backend）：147 passed。
- `make quality`（fastapi）：602 passed，覆盖率 88.04%。
- `pnpm run quality`（frontend）：90 个测试文件、261 passed。
- `pnpm run build`（frontend）：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 scripts/validate_model_contracts.py .`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只完成数据范围第一阶段：角色配置、用户列表过滤、操作日志过滤和双后端契约闭环。
- 字段级读写权限、通知等其他业务对象的数据范围过滤仍按后续阶段处理。
- 前端只负责配置 `dataScope/deptIds`，安全边界在后端查询过滤。
