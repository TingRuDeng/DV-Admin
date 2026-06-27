# NavbarActions 主题 class helper 抽取

## 目标

- 抽取 `frontend/src/layouts/components/NavBar/components/NavbarActions.vue` 中导航栏右侧动作区的主题文字 class 判定逻辑。
- 保持用户菜单、登出跳转、桌面工具项显示、系统设置入口和 CSS class 名称不变。

## 变更范围

- 新增 `frontend/src/layouts/components/NavBar/components/navbarActionsHelpers.ts`。
- 新增 `frontend/src/layouts/components/__tests__/navbar-actions-helpers.spec.ts`。
- 更新 `frontend/src/layouts/components/NavBar/components/NavbarActions.vue`。
- 更新 `tasks/todo.md`。

## 验证记录

- `node_modules/.bin/vitest run src/layouts/components/__tests__/navbar-actions-helpers.spec.ts`：通过，1 个文件 4 个用例。
- `node_modules/.bin/eslint "src/**/*.{vue,ts,js}"`：通过。
- `node_modules/.bin/prettier --check "**/*.{js,cjs,ts,json,css,scss,vue,html,md}"`：通过。
- `node_modules/.bin/stylelint "**/*.{css,scss,vue}"`：通过。
- `node_modules/.bin/vue-tsc --noEmit`：通过。
- `node_modules/.bin/vitest run`：通过，89 个文件 259 个用例。
- `node_modules/.bin/vite build`：通过。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review Gate

- 终态：finished
- Spec 符合度：通过；本轮只抽取主题文字 class 判定 helper，并补充覆盖暗黑主题、顶部/混合布局经典蓝和浅色分支的测试。
- 安全检查：未新增外部输入处理、请求调用、存储访问或 secret；无硬编码凭据。
- 测试与验证：目标测试、完整前端单测、类型检查、静态检查、构建和通用文档校验均通过。
- 复杂度检查：`NavbarActions.vue` 从 274 行降至 254 行；新增 helper 34 行，测试 58 行，均低于单文件 300 行限制；新增函数小于 50 行。
- Document-refresh: not-needed
- 原因：本轮是内部组件纯逻辑抽取，不改变对外 API、路由、数据库、权限或用户可见流程。
- 剩余风险：未做浏览器手动切换主题/布局验证；主题 class 组合已由纯逻辑测试覆盖，组件集成由类型检查和构建覆盖。
- 潜在技术债：`NavbarActions.vue` 样式仍占主要行数，后续可在样式治理轮次再评估是否迁移到共享 chrome 样式层。
- 结论：通过
