# PageContent Excel 文件处理逻辑抽取

## 目标

将 `frontend/src/components/CURD/PageContent.vue` 中的 Excel 读写、浏览器文件保存和导入解析逻辑抽到独立 helper，降低历史兼容层组件职责密度。

## 现状证据

- `PageContent.vue` 的 `handleExports()` 直接创建 `ExcelJS.Workbook`、写入 worksheet 并保存文件。
- `PageContent.vue` 的 `handleImports()` 直接持有 `FileReader`、Excel 解析和业务提交分发。
- `PageContent.vue` 的 `saveXlsx()` 直接操作 `Blob`、`URL.createObjectURL` 和临时下载链接。

## 执行计划

- [x] P1 串行：新增 `frontend/src/components/CURD/pageContentExcel.ts`，承接 Excel buffer 写入、文件读取、行解析和浏览器保存。
- [x] P2 串行：更新 `frontend/src/components/CURD/PageContent.vue`，移除直接 `ExcelJS` 依赖，只保留业务编排和 UI 提示。
- [x] P3 串行：新增 `frontend/src/components/CURD/__tests__/page-content-excel.spec.ts`，覆盖导出 buffer、导入解析、空表和读取失败。
- [x] P4 串行：运行前端目标测试、类型检查、lint、聚合质量检查、构建、文档校验和 diff 检查。
- [ ] P5 串行：完成 review-gate，并在 `tasks/todo.md` 记录合并状态。

## 并行策略

本轮不启用 subagent。原因：改动集中在同一组件和同一 helper，存在文件写冲突，串行推进更稳。

## 验证命令

```bash
cd frontend && pnpm run test:unit -- page-content-excel curd-deprecation-governance
cd frontend && pnpm run type-check
cd frontend && pnpm run lint:check
cd frontend && pnpm run quality
cd frontend && pnpm run build
python3 scripts/validate_docs.py . --profile generic
python3 -m py_compile scripts/validate_docs.py
git diff --check
```

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只抽取 `PageContent.vue` 的 Excel 文件处理职责，不改变 CURD 兼容层对外 props、emits、`defineExpose()`、导入导出业务分支或提示文案；安全检查未发现本轮新增 secret，敏感词扫描命中仅来自历史任务摘要；测试与验证通过，覆盖目标 helper、CURD 退场守卫、前端类型、lint、完整质量门禁、构建、文档校验、脚本编译和 diff 检查；复杂度检查通过，`PageContent.vue` 从 534 行降至 486 行，新增 helper 92 行、测试 99 行；Document-refresh: not-needed，原因：本轮是内部职责拆分，不改变用户可见功能、API、数据库结构或产品文档事实；剩余风险是 `PageContent.vue` 仍超过 300 行，后续还需继续拆分数据获取和分页状态职责。
