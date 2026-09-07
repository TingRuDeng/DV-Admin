# 字典选项契约修复

## 目标与边界

- 分支：`codex/fix-dict-option-contract`，基于合并后的 `origin/master` (`ef6bb44`)。
- 修复标签/选择器把分页对象当数组、旧字典编码筛选参数和持久化错误缓存的问题。
- 不新增业务能力、不改变响应契约、权限、数据库或部署配置。
- 验证中发现同一通知表单的用户选项路径导致 Django 301 跳转丢失代理前缀；最小修正为前端
  使用尾斜杠路径，FastAPI 显式接收该路径并保留无斜杠兼容入口。

## 实施

- [x] 先补测试复现分页对象进入缓存后 `dictItems.find is not a function`。
- [x] API 使用 `dictCode`，按每页 100 条取齐再返回数组；失败不返回部分结果。
- [x] 缓存键升级 v2，非数组条目重新加载；保留并发请求合并和失败后可重试。
- [x] `DictLabel` 继续负责根据 code/value 展示 label/tagType，不新增组件或抽象。
- [x] 双后端真实浏览器夹具使用相同值、不同字典及不同颜色，防止未筛选结果假绿。
- [x] 浏览器六条流程统一增加 `pageerror` 守卫，通知页断言标签文本与颜色。
- [x] 修正通知页 mock 为共享分页契约，不再模拟不存在的旧数组接口。
- [x] 用户选项补双路径不重定向测试；浏览器开通知表单时等待并断言选项 JSON 成功响应。
- [x] 完成全量前端门禁和相关后端/根契约校验。

## 验证证据

- RED：新增前端回归 9 failed，包含原始 `dictItems.find` 错误、旧缓存复用及分页缺失。
- GREEN：同一测试文件 9 passed。
- FastAPI 真实浏览器：pytest 1 passed（内部六条 Playwright 流程），含标签与 pageerror 断言。
- 初次沙箱运行因 macOS Chromium MachPort 权限失败；获准后在隔离环境重跑通过，不是业务断言失败。
- 最终 FastAPI 浏览器重跑：pytest 1 passed（内部六条流程，45.34 秒）。
- 最终 Django 浏览器及 HTTP：pytest 2 passed（内部六条浏览器流程，41.16 秒）。
- `pnpm --dir frontend run quality`：100 文件、317 tests passed；包含新增 9 条回归。
- `pnpm --dir frontend run build`：通过。
- `make -C fastapi quality`（测试环境覆盖合规初始密码和 minLength=15）：Ruff/isort、mypy 151 文件、迁移检查通过；856 passed/1 skipped，覆盖率 89.25%。
- `backend/.venv/bin/ruff check .`（backend 工作目录）：通过；新增夹具 import 的格式错误已自动修正。
- `backend/.venv/bin/pytest -q`（backend 工作目录）：290 passed/1 skipped；跳过项为单独启用运行的浏览器测试。
- 通知/字典项 mock Playwright：3 passed（独立 9532 端口）。字典项 mock 仍缺少壳层通知轮询响应，产生未 mock 404；不把这组测试通过解释为无控制台错误。两端真实浏览器使用严格 pageerror 守卫且通过。
- `python3 scripts/validate_api_contracts.py .`、`python3 scripts/validate_model_contracts.py .`、
  `python3 scripts/validate_docs.py . --profile generic`、`git diff --check`：通过。
- Django 首轮 1 failed/1 passed：字典标签正确，但 pageerror 守卫抓到用户选项 301 后收到 Vite HTML。
  Playwright trace 定位到 `NoticeFormDrawer.loadUserOptions`；FastAPI 尾斜杠入口测试 RED 为 422
  （误匹配用户 ID 路由），随后显式登记路径，未放宽或豁免脚本错误守卫。

## Review 与剩余风险

- 未通过空数组 fallback 隐藏服务端错误；空页但 total 未取齐会明确拒绝，允许重试。
- 分页不是数据库快照：加载期间字典被并发编辑可能影响完整性；未引入快照版本或新后端接口。
- 新版不复用旧缓存，但不删除其他 localStorage 数据；现有缓存更新机制与权限要求保持不变。
- 本轮只修这一条运行时消费链；不据此宣称双后端全部可替代。
- 最终本地复核未发现本轮新增阻断项；未部署或修改真实凭据/数据库。提交、PR 和合并后 CI 状态以对应 GitHub 记录为准。
