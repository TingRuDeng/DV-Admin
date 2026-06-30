# 通知分页字段收敛

## 目标

- 补齐 FastAPI `notices_page` 的 `targetUserIds` 和 `updateTime`。
- 从字段契约 `converge` 和技术债中移除该通知分页差异。
- 同步前端 `NoticePageVO` 类型声明和前端字段契约。

## 非目标

- 不处理用户、菜单、字典、部门等其他字段漂移。
- 不统一全局时间字段命名。

## 执行计划

- [x] RED：补 FastAPI 通知分页字段测试。
- [x] GREEN：补 schema 和序列化映射。
- [x] 更新字段契约、前端类型契约和技术债。
- [x] 执行验证并提交。

## 进度记录

- 开始执行：上一轮字段契约覆盖已提交，当前工作区干净。
- 红灯验证：`NoticePageOut` 缺少 `target_user_ids`，目标测试失败。
- 绿色实现：FastAPI 通知分页输出补齐 `target_user_ids` 与 `update_time`，并同步字段契约、前端类型和技术债。
- 验证通过：目标测试、通知服务字段契约测试、根契约校验、文档校验、前端字段契约测试、FastAPI 全量质量门禁、前端全量质量门禁均通过。

## Review 小结

- 本轮只收敛 `notices_page.targetUserIds/updateTime`，未处理其他字段漂移。
- 未新增兼容 fallback，字段由已有 Notice ORM 数据直接映射到分页输出。
- 剩余字段漂移继续由 `scripts/api_field_contracts.py` 与 `docs/TECH_DEBT.md` 跟踪。
