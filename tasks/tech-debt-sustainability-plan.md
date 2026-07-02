# 五类技术债顺序治理

## 目标

- 先提交 P2 文档事实修复，再依次推进 5 类值得优先处理的技术债。
- 用可执行契约和目标测试降低文档漂移、双后端行为差异和运行时回归风险。

## 非目标

- 不为行数继续拆兼容层。
- 不在没有慢查询证据前添加数据库索引。
- 不在没有 PRD 前直接实现审计日志、批量任务和导入导出大功能。

## 执行计划

- [x] 阶段 0：提交 P2 操作日志双实现文档事实修复。
- [x] 阶段 1：API 文档自动化 / 契约覆盖增强。
- [x] 阶段 2：错误处理统一。
- [x] 阶段 3：Django 测试覆盖补强。
- [ ] 阶段 4：模型差异迁移边界收口。
- [ ] 阶段 5：审计日志 UX、批量操作与导入导出状态 PRD。

## 进度记录

- 阶段 0：已提交 `docs: 修正操作日志双实现架构事实`。
- 阶段 1：新增 `scripts/docs_fact_validation.py`，由 `scripts/validate_docs.py` 调用，禁止操作日志旧独占事实回流到文档或能力契约脚本；补充 `backend/drf_admin/utils/test_docs_validator_structure.py` 结构测试。
- 阶段 2：补充前端错误归一化测试，覆盖后端适配层返回数字字符串错误码时仍识别共享认证错误码；`frontend/src/utils/api-error.ts` 仅接受安全整数或整数字符串，避免 token 刷新分支因错误码类型漂移失效。
- 阶段 3：在 Django 读接口运行时契约测试中补充用户分页第二页行为断言，确保 `pageNum=2&pageSize=1` 返回不同记录且 `total` 保持一致。

## 验证结果

- 阶段 1：
  - `cd backend && uv run pytest drf_admin/utils/test_docs_validator_structure.py -q`：2 passed。
  - `python3 scripts/validate_docs.py . --profile generic`：通过。
  - `python3 -m py_compile scripts/validate_docs.py scripts/docs_fact_validation.py`：通过。
- 阶段 2：
  - RED：`CI=true pnpm --dir frontend run test:unit -- api-error`：新增用例先失败，`code` 收到 `undefined`。
  - GREEN：`CI=true pnpm --dir frontend run test:unit -- api-error`：90 files / 261 tests passed。
  - `python3 scripts/validate_api_contracts.py .`：通过。
- 阶段 3：
  - `cd backend && uv run pytest drf_admin/utils/runtime_api_contracts/test_read_contracts.py -q`：2 passed。
  - `cd backend && uv run ruff check drf_admin/utils/runtime_api_contracts/test_read_contracts.py`：通过。
  - `python3 scripts/validate_api_contracts.py .`：通过。
