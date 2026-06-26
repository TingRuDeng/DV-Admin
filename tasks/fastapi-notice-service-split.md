# FastAPI 通知服务拆分治理计划

## 目标

- 将 `fastapi/app/services/system/notice_service.py` 从 292 行降到更可维护的体量。
- 抽出通知时间辅助、输出转换和已读状态 helper，降低 `NoticeService` 职责密度。
- 保持 `app.services.system.notice_service.notice_service`、`NoticeService` 和 `local_now` 导入路径不变。

## 非目标

- 不修改通知 API 路由、请求参数、分页响应或详情响应契约。
- 不修改 `Notices`、`NoticeReads` 数据模型、数据库表结构或已读语义。
- 不新增 mock 假成功、静默 fallback 或跳过测试逻辑。

## 当前事实

- `fastapi/app/services/system/notice_service.py` 当前 292 行，是当前 FastAPI 最大业务服务文件。
- 文件内同时包含后台分页、详情、创建、更新、删除、发布、撤回、全部已读、我的通知分页和输出转换。
- `fastapi/app/api/v1/system/notices.py` 通过 `notice_service` 调用该服务，测试已按 admin_query、detail、mutation、status、my_page 分层覆盖。

## 决策日志

- 方案 A：新增 `notice_time.py`、`notice_serializers.py`、`notice_read_helpers.py`，迁移无状态 helper，`notice_service.py` 保留服务编排和兼容导入。
  - 优点：改动小，外部导入路径稳定，直接降低服务类职责密度。
  - 缺点：服务文件仍承载后台和我的通知两类业务方法。
- 方案 B：将 `notice_service.py` 改成 package，按 admin、status、my_page 拆服务类。
  - 优点：职责拆分更彻底。
  - 缺点：模块到 package 的迁移影响导入路径、测试 patch 路径和调用方，当前风险偏高。
- 方案 C：只压缩注释或格式。
  - 优点：diff 小。
  - 缺点：不能改善职责边界，不解决长期可持续性问题。

推荐方案：采用方案 A。本轮保持运行时契约稳定，只拆无状态 helper。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/app/services/system/notice_time.py`，迁移时间辅助函数并在 `notice_service.py` 兼容导入。
- [x] P3 串行：新增 `fastapi/app/services/system/notice_serializers.py`，迁移后台分页、表单、详情、我的通知输出转换。
- [x] P4 串行：新增 `fastapi/app/services/system/notice_read_helpers.py`，迁移已读状态集合与未读过滤 helper。
- [x] P5 串行：更新 `notice_service.py` 委托 helper，并保持对外方法行为不变。
- [x] P6 串行：执行通知服务目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P7 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_notice_service_admin_query.py tests/test_notice_service_detail.py tests/test_notice_service_mutation.py tests/test_notice_service_status.py tests/test_notice_service_my_page.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- 通知服务拆分已完成：`fastapi/app/services/system/notice_service.py` 从 292 行降至 225 行，新增 `notice_time.py`、`notice_serializers.py`、`notice_read_helpers.py` 承接时间辅助、输出转换和已读状态 helper。
- 验证通过：通知服务目标测试 `30 passed`；FastAPI `make quality` 通过，结果为 `551 passed`、覆盖率 `87.19%`；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。
- Review-gate：finished；Spec 符合度通过，本轮保留 `app.services.system.notice_service.notice_service`、`NoticeService` 和 `local_now` 导入路径，不修改通知 API 路由、分页响应、详情响应、数据模型或已读语义。
- 安全检查未发现新增 secret、mock 假成功、静默 fallback 或跳过测试；复杂度检查通过，本轮新增文件分别为 13、62、23 行，目标文件 225 行，均低于 300 行。
- Document-refresh: not-needed，原因：本轮只做内部服务职责拆分，不改变对外 API、数据库结构、通知契约或用户可见流程。
- 剩余风险：`fastapi/app/db/import_django_data.py` 仍为 292 行，后续可继续按职责拆分治理。
