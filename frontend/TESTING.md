# 前端测试与验收

## 技术栈与边界

- 单元测试使用 Vitest、`@vue/test-utils` 和 happy-dom。
- `vitest.config.ts` 收集 `src/**/*.{test,spec}.{js,ts}`，仅排除依赖、构建产物和 E2E；不排除 store 或 router。
- `vitest.setup.ts` 提供自动导入函数与 `__APP_INFO__` 测试环境。路由交互测试需要按用例提供真实 router 或明确的 mock。
- 浏览器测试使用 Playwright Chromium。计算样式、抽屉位置、遮罩命中和键盘焦点必须在真实浏览器中验证，源码字符串断言不能替代这些验收。
- 常规 E2E 使用 `page.route` 拦截 API；开发 Mock 使用 `vite-plugin-mock-dev-server`。项目不再使用 MSW 或其 Service Worker。
- Vitest 与应用构建共用 Vite 8。Mock 插件需要显式的 `esbuild` 开发依赖，不能依赖旧 Vite 的传递依赖。

## 环境准备

要求 Node.js `>=24.0.0`，pnpm 版本由 `package.json#packageManager` 固定。按锁文件安装：

```bash
cd frontend
pnpm install --frozen-lockfile
```

测试数量随源码变化，以本次命令输出为准，不使用历史数量作为完成证明。

## 单元测试与静态检查

```bash
pnpm run test:unit
pnpm exec vitest run src/utils/__tests__/shell-audit-governance.test.ts
pnpm test
pnpm run test:ui
pnpm run quality
pnpm run build
pnpm run audit:prod
```

- `test:unit` 单次运行；`test` 为交互式监听。
- `quality` 依次执行只读 lint、类型检查和单元测试。
- `build` 包含类型检查；`audit:prod` 检查生产依赖公告及豁免有效期。
- `test:coverage` 是可选脚本，需要与 Vitest 版本匹配的 V8 coverage provider；不是当前前端 CI 的必跑入口。

## 常规浏览器验收

```bash
pnpm run test:e2e -- --list
pnpm run test:e2e:smoke
pnpm exec playwright test e2e/shell-layout.spec.ts --workers=1
pnpm run test:e2e:ui
```

默认配置排除 `real-backend-smoke.spec.ts`，因此列举常规测试不要求真实后端环境变量。
Playwright 自行启动 Vite，默认端口来自开发配置且不复用已有服务。若端口已占用，可为本次运行指定独立端口：

```bash
VITE_APP_PORT=19527 pnpm run test:e2e:smoke
```

壳层验收包括三种布局、动态路由与缓存、TagsView 的尺寸和键盘焦点、暗色标题、传送菜单背景，以及移动抽屉的位置、点击、关闭、焦点与滚动行为。
`shell-audit-governance.test.ts` 和 `playwright-config-governance.test.ts` 约束源码及门禁入口，仍需结合浏览器测试。

## 双后端真实浏览器验收

从仓库根目录分别运行：

```bash
(cd backend && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest \
  drf_admin/utils/runtime_api_contracts/test_live_http_contract.py::DjangoLiveHttpContractTestCase::test_shared_frontend_flow_over_real_django_http)
(cd fastapi && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest \
  tests/test_live_http_contract.py::test_shared_frontend_flow_over_real_fastapi_http)
```

这两项启动隔离数据库、临时上传目录和真实 HTTP 服务，不使用开发数据库，也不拦截 API。
共享用例覆盖代表页、用户生命周期、RBAC、文件归属、日志查询/详情/统计/删除/清理及菜单写入。
Django 和 FastAPI 必须分别通过；Mock E2E 通过不能推导真实后端通过。

runner 默认使用 Django 前端端口 9530、FastAPI 前端端口 9531，可通过 `REAL_FRONTEND_PORT` 覆盖。
端口分离不代表输出目录分离，本地建议串行运行两套真实 smoke，避免报告相互覆盖。

## 失败证据

CI 上传 `playwright-report/` 与 `test-results/`；真实后端配置保留失败截图和 trace。
本地 `test-results/.last-run.json` 仅描述最近一次运行，必须结合报告中的测试范围，不能当作全套验收结果。
重跑前保留必要的失败输出，不通过跳过用例、放宽业务断言或删除门禁处理失败。

## 添加测试

工具函数和接口适配测试放在对应模块的 `__tests__` 中，使用 `vi.mock` / `vi.mocked` 隔离明确的边界。
组件测试从 `@vue/test-utils` 导入 `mount` 或 `shallowMount`，断言用户可观察的行为，并等待异步更新：

```typescript
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import MyButton from "./MyButton.vue";

describe("MyButton", () => {
  it("点击后发出事件", async () => {
    const wrapper = mount(MyButton);
    await wrapper.get("button").trigger("click");
    expect(wrapper.emitted("click")).toHaveLength(1);
  });
});
```

导入 store 时按用例创建 Pinia；路由行为使用隔离 router。不要通过排除整个目录掩盖初始化问题。
涉及请求层时优先参考现有 `src/utils/__tests__` 和 `src/api/**/__tests__`；端到端权限、刷新令牌和持久化行为交由真实后端 smoke 证明。
