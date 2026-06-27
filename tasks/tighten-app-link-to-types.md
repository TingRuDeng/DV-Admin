# AppLink 跳转目标类型治理

## 目标

- [x] 串行：确认 `AppLink` 的真实调用点和跳转目标结构。
- [x] 串行：移除 `AppLink` 中 `linkProps(to: any)` 的显式 `any`。
- [x] 串行：补充治理测试，防止跳转目标类型回退。
- [x] 串行：执行前端类型检查、静态检查、单测和文档校验。
- [ ] 串行：交付前审查并提交 PR。

## 范围

- 修改：`frontend/src/components/AppLink/index.vue`
- 新增：`frontend/src/components/__tests__/app-link-type-governance.spec.ts`
- 不涉及：菜单路径拼接、外链判断规则、后端 API、路由配置生成

## 决策

- 使用组件本地 `AppLinkTo` 表达当前真实输入 `{ path, query }`，不放宽成 `RouteLocationRaw`。
- 原因：当前组件依赖 `to.path` 判断外链，真实调用点也只传对象；放宽类型会掩盖组件能力边界。

## 验证计划

- `cd frontend && ./node_modules/.bin/vitest run src/components/__tests__/app-link-type-governance.spec.ts`
- `cd frontend && ./node_modules/.bin/vue-tsc --noEmit`
- `cd frontend && ./node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`
- `cd frontend && ./node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`
- `cd frontend && ./node_modules/.bin/stylelint "**/*.{css,scss,vue}"`
- `cd frontend && ./node_modules/.bin/vitest run`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`
