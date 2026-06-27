# FileUpload 展示与上传结果 helper 抽取

## 现状分析

- `frontend/src/components/Upload/FileUpload.vue` 当前 279 行，同时承担上传 UI、modelValue 到 fileList 的展示映射、上传完成判断、成功文件收集、失败文件清理、删除路径解析和上传/下载 API 编排。
- 现有 `frontend/src/components/__tests__/upload-file-path-governance.spec.ts` 已守住删除接口必须使用后端返回的相对 `path`。
- 本轮目标只抽离可纯测的数据转换规则，不改变 `FileAPI.upload`、`FileAPI.delete`、`FileAPI.download` 调用方式、`v-model` 数据结构或 Element Plus 上传组件契约。

## 执行计划

- [ ] 新增 `frontend/src/components/Upload/fileUploadHelpers.ts`，承接文件展示映射、上传完成判断、成功结果收集、失败文件清理索引和删除路径解析。
- [ ] 精简 `frontend/src/components/Upload/FileUpload.vue`，保留 UI、API 编排和消息提示。
- [ ] 新增 `frontend/src/components/__tests__/file-upload-helpers.test.ts`，覆盖 helper 纯规则和 `FileUpload.vue` 行数守卫。
- [ ] 执行最小充分验证：目标 Vitest、前端静态检查、类型检查、全量单测、构建、文档校验和 diff 检查。

## 并行策略

- 不启用 subagent。原因：本轮改动集中在同一上传组件边界，helper 与组件测试需要同步调整，串行更能避免写冲突。

## 验收标准

- `frontend/src/components/Upload/FileUpload.vue` 明显低于 300 行，职责更聚焦于上传组件编排。
- 展示映射、上传完成判断、成功结果收集和删除路径解析有纯 helper 测试覆盖。
- 不改变上传请求参数、删除路径契约、下载行为、`modelValue` 结构或后端 API。

## 验证记录

- `node_modules/.bin/vitest run src/components/__tests__/file-upload-helpers.test.ts src/components/__tests__/upload-file-path-governance.spec.ts src/components/__tests__/upload-error-type-governance.spec.ts`：3 files / 10 tests passed。
- `node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `node_modules/.bin/vue-tsc --noEmit`：通过。
- `node_modules/.bin/vitest run`：88 files / 255 tests passed。
- `node_modules/.bin/vite build`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review Gate

- 终态：finished。
- Spec 符合度：通过；只抽取 FileUpload 展示和上传结果纯规则，未修改 `FileAPI.upload`、`FileAPI.delete`、`FileAPI.download` 调用方式、`modelValue` 结构或上传组件 UI 契约。
- 安全检查：通过；未新增外部输入、secret、网络请求、SQL 或命令执行；删除路径仍通过上传返回的相对 `path` 解析。
- 测试与验证：通过；目标测试、全量前端单测、类型检查、静态检查、构建和通用文档校验均已执行。
- 复杂度检查：通过；`FileUpload.vue` 从 279 行降至 255 行，新增 helper 63 行，新增测试 120 行。
- Document-refresh: not-needed；本轮只调整内部前端上传组件组织和任务记录，不改变产品文档、API、数据库或架构事实。
- 剩余风险：未启动浏览器人工上传/删除文件；当前以 helper 单测、上传路径治理测试、全量前端单测、构建和远端门禁作为最小充分验证。
- 潜在技术债：`FileUpload.vue` 仍包含上传请求 formData 构造和 API 编排，后续可单独评估是否抽出上传请求编排 composable。
- 结论：通过。
