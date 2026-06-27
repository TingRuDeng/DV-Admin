# any 注释噪音清理

## 目标

- [x] 串行：确认生产源码中剩余 `any` 命中均来自注释。
- [x] 串行：删除废弃接口注释，调整上传错误 helper 注释文案。
- [x] 串行：验证生产源码 `any` 扫描不再命中非测试源码。
- [x] 串行：执行文档校验、diff 检查并提交 PR。

## 范围

- 修改：`frontend/src/api/system/dict-api.ts`
- 修改：`frontend/src/components/Upload/uploadError.ts`
- 不涉及：字典 API 类型、上传错误处理逻辑、运行时行为、后端 API

## 验证计划

- `rg -n "\\bany\\b|@ts-ignore|@ts-expect-error" frontend/src --glob '!**/__tests__/**' --glob '!**/*.d.ts' --glob '!**/node_modules/**'`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- `rg -n "\\bany\\b|@ts-ignore|@ts-expect-error" frontend/src --glob '!**/__tests__/**' --glob '!**/*.d.ts' --glob '!**/node_modules/**'`：无命中，退出码 1 代表未找到匹配项。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只清理注释噪音，没有改变字典 API 类型或上传错误处理逻辑。
- 安全检查：通过；未新增外部输入处理、secret、mock、fallback 或静默降级。
- 复杂度检查：通过；本轮删除废弃注释并调整一行注释，不增加函数或分支复杂度。
- Document-refresh: not-needed。原因：本轮不改变用户功能、API、数据库模型或架构事实。
- 剩余风险：无运行时风险；这是纯注释和任务状态治理。
- 潜在技术债：后续应把生产源码 `any` 扫描纳入常规治理守卫，避免再次回流。
