# FastAPI 通知服务测试拆分治理计划

## 目标

- 将 `fastapi/tests/test_notice_service.py` 从 356 行单文件拆分为职责清晰的小测试文件。
- 保持 `NoticeService` 现有分页、表单详情、创建更新、发布撤销、已读和我的通知列表断言不变。
- 抽出通知测试共享数据夹具，避免拆分后重复构造通知样本。

## 非目标

- 不修改 `fastapi/app/services/system/notice_service.py` 运行时代码。
- 不改变通知分页、发布、撤销、已读、目标用户校验或我的通知列表行为。
- 不调整通知 API、数据库模型、通知 schema 或前端调用。

## 当前事实

- `fastapi/tests/test_notice_service.py` 当前 356 行，是当前 FastAPI 测试中最大的单文件。
- 文件内包含 `TestNoticeServiceGetPage`、`TestNoticeServiceGetForm`、`TestNoticeServiceGetDetail`、`TestNoticeServiceCreate`、`TestNoticeServiceUpdate`、`TestNoticeServiceDelete`、`TestNoticeServicePublish`、`TestNoticeServiceRevoke`、`TestNoticeServiceReadAll`、`TestNoticeServiceGetMyPage`。
- 共享夹具 `test_notices_for_service` 和 `test_published_notice` 同时服务后台查询、详情、写操作、发布撤销和用户侧通知测试。
- `fastapi/app/services/system/notice_service.py` 当前 292 行，本轮不处理运行时代码体量。

## 决策日志

- 方案 A：抽 `notice_service_fixtures.py`，按 admin_query、detail、mutation、status、my_page 拆分测试文件。
  - 优点：边界与服务行为簇一致，夹具集中复用，新增文件体量可控。
  - 缺点：文件数量增加，需要确认 pytest 插件夹具加载正常。
- 方案 B：只拆创建更新与发布撤销测试，其余保留在原文件。
  - 优点：改动更小。
  - 缺点：原文件仍然偏大，查询、详情和我的通知列表仍耦合在一个文件。
- 方案 C：同步拆分 `NoticeService` 运行时代码。
  - 优点：可同时降低服务实现文件体量。
  - 缺点：会把测试组织调整和运行时重构混在一起，扩大风险。

推荐方案：采用方案 A。本轮只拆测试文件和共享夹具，不修改运行时代码。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增 `fastapi/tests/notice_service_fixtures.py`，迁移 `test_notices_for_service` 与 `test_published_notice`。
- [x] P3 串行：新增 `fastapi/tests/test_notice_service_admin_query.py`，迁移后台分页和表单测试。
- [x] P4 串行：新增 `fastapi/tests/test_notice_service_detail.py`，迁移详情与标记已读测试。
- [x] P5 串行：新增 `fastapi/tests/test_notice_service_mutation.py`，迁移创建、更新和删除测试。
- [x] P6 串行：新增 `fastapi/tests/test_notice_service_status.py`，迁移发布、撤销和全部已读测试。
- [x] P7 串行：新增 `fastapi/tests/test_notice_service_my_page.py`，迁移我的通知列表测试。
- [x] P8 串行：删除原 `fastapi/tests/test_notice_service.py`，确保没有重复测试或孤儿引用。
- [x] P9 串行：执行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [ ] P10 串行：review-gate、提交、PR、CI 和合并。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_notice_service_admin_query.py tests/test_notice_service_detail.py tests/test_notice_service_mutation.py tests/test_notice_service_status.py tests/test_notice_service_my_page.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

通知服务测试拆分已完成：原 356 行 `test_notice_service.py` 已拆为后台查询、详情、写操作、发布状态和我的通知列表 5 个职责测试文件，并抽出 `notice_service_fixtures.py` 复用通知样本夹具；运行时代码未修改。

验证通过：目标测试 30 passed；FastAPI `make quality` 539 passed，覆盖率 85.44%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。

Review-gate：finished；Spec 符合度通过，本轮只调整测试组织，不修改运行时代码、API、数据库结构或用户可见流程；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，新增测试文件均小于 300 行；Document-refresh: not-needed，原因：本轮不改变产品文档事实；剩余风险是 `fastapi/app/services/system/notice_service.py` 当前接近 300 行，后续若继续增长应单独拆分运行时服务职责。
