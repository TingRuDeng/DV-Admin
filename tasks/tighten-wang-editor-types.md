# WangEditor 编辑器类型治理

## 目标

- [x] 串行：确认 `WangEditor` 编辑器实例和上传菜单配置的上游类型。
- [x] 串行：移除 `handleCreated(editor: any)` 和 `uploadImage` 配置 `as any`。
- [x] 串行：补充治理测试，防止编辑器类型回退。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/WangEditor/index.vue`
- 新增：`frontend/src/components/__tests__/wang-editor-type-governance.spec.ts`
- 不涉及：上传 API、富文本内容模型、通知表单、demo 页面、后端 API

## 决策

- 使用 `@wangeditor-next/editor` 导出的 `IDomEditor`、`IUploadImageConfig`、`IEditorConfig`、`IToolbarConfig`。
- `customUpload` 的上传和插入参数保持当前行为；补齐上游配置要求的基础字段，避免继续使用 `as any`。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/wang-editor-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
