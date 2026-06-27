# 上传组件错误类型收口

## 目标

- 收紧 `frontend/src/components/Upload` 下上传失败回调的类型边界。
- 移除 `SingleImageUpload`、`FileUpload`、`MultiImageUpload` 中错误参数的显式 `any`。
- 补充治理测试，防止上传错误处理回退到 `error: any`。

## 范围

- 修改：`frontend/src/components/Upload/SingleImageUpload.vue`
- 修改：`frontend/src/components/Upload/FileUpload.vue`
- 修改：`frontend/src/components/Upload/MultiImageUpload.vue`
- 新增：`frontend/src/components/__tests__/upload-error-type-governance.spec.ts`
- 修改：`tasks/todo.md`
- 不涉及：上传请求、删除请求、文件列表结构、后端 API、样式重构

## 执行计划

- [x] 串行：为上传错误对象补局部窄化 helper。
- [x] 串行：将三个上传失败回调参数从 `any` 收紧为 `unknown`。
- [x] 串行：新增上传错误类型治理测试。
- [x] 串行：运行目标测试、前端类型检查、前端 lint、前端单测、文档校验和 diff 检查。
- [x] 串行：执行交付前 review-gate 并记录结论。

## 并行说明

本轮不启用 subagent。原因：三个组件属于同一上传错误处理模式，改动需要保持一致，串行更利于统一边界。

## 验证命令

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/upload-error-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished。
- Spec 符合度：通过，本轮只收紧上传失败回调类型并新增治理测试。
- 安全检查：无新增 secret、mock 或静默 fallback；未知错误只在 helper 中完成类型窄化后读取 `message`。
- 测试与验证：目标测试、前端类型检查、eslint、prettier、stylelint、完整前端单测、文档校验和 `git diff --check` 均通过。
- 复杂度检查：新增 helper 21 行，新增测试 30 行，三个上传组件均低于 300 行。
- Document-refresh: not-needed，原因：本轮不改变用户可见功能、API、数据库结构或产品文档事实。
- 剩余风险：WangEditor、Dict、Breadcrumb 等历史组件仍有显式 `any`，需要后续继续治理。
