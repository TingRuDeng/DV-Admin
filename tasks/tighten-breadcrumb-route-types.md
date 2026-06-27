# Breadcrumb 路由项类型治理

## 目标

- [x] 串行：确认 `Breadcrumb` 实际使用的路由字段和显式 `any` 位置。
- [x] 串行：移除 dashboard fallback 的 `as any` 和 `handleLink(item: any)`。
- [x] 串行：补充治理测试，防止面包屑路由类型回退。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [x] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/Breadcrumb/index.vue`
- 新增：`frontend/src/components/__tests__/breadcrumb-route-type-governance.spec.ts`
- 不涉及：路由表生成、权限路由、面包屑 UI 样式、后端 API

## 决策

- 使用本地 `BreadcrumbRoute` 表达面包屑实际使用的 `path/name/meta/redirect` 字段。
- dashboard fallback 不伪装为完整 `RouteLocationMatched`，避免继续使用 `as any`。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/breadcrumb-route-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## 验证结果

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/breadcrumb-route-type-governance.spec.ts`：通过，1 个测试文件、2 个用例。
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`：通过。
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `cd frontend && ./node_modules/.bin/vitest run`：通过，84 个测试文件、232 个用例。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `git diff --check`：通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收紧 Breadcrumb 路由项类型边界，没有改变路由生成、权限路由、UI 样式或后端 API。
- 安全检查：通过；未新增外部输入处理、secret、mock、fallback 或静默降级。
- 复杂度检查：通过；`Breadcrumb/index.vue` 为 105 行，新增治理测试为 21 行，未触发文件大小或函数长度硬约束。
- Document-refresh: not-needed。原因：本轮不改变用户功能、API、数据库模型或架构事实。
- 剩余风险：未启动浏览器做面包屑交互人工验证；当前以类型检查和单测约束类型回退。
- 潜在技术债：面包屑仍依赖运行时路由 `meta.title` 约定，后续如治理动态路由元信息，可统一收紧路由元数据来源。
