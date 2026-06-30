# FastAPI 分页参数对齐

## 目标

- 将 FastAPI 对外分页参数统一为 `pageNum/pageSize`。
- 用运行时契约测试证明 `pageNum=2&pageSize=1` 会命中第二页。
- 同步端点契约和文档事实。

## 非目标

- 不修改前端分页组件。
- 不修改 Django 分页实现。
- 不扩展字段契约写端点覆盖。
- 不补 Django 操作日志能力。

## 执行计划

- [x] RED：补 FastAPI 分页行为测试。
- [x] GREEN：新增统一分页参数依赖并接入 users/roles/dicts/dict-items/logs。
- [x] 同步契约目录与文档。
- [x] 执行最小充分验证与 review-gate。

## 进度记录

- 开始执行：当前分支 `codex/frontend-field-contracts`，工作区干净；`git pull --ff-only` 因当前分支无 upstream 未执行合并。
- RED：`uv run pytest tests/runtime_api_contracts/test_read_and_file_contracts.py::test_fastapi_page_num_reaches_second_page -q` 失败，`pageNum=2` 请求仍返回第一页用户。
- GREEN：新增统一分页依赖并接入 FastAPI 分页端点后，同一测试通过。
- 契约与文档：端点契约公开参数已改为 `pageNum/pageSize`，文档同步更新。
- 验证：FastAPI quality、Django runtime contract、契约校验和文档校验均已通过。

## Review 小结

- 本轮只处理分页参数漂移，未扩展字段契约写端点覆盖。
- 旧 `page` 仅作为 FastAPI 隐藏兼容参数保留，不进入公开契约和文档。
