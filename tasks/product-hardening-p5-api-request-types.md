# P5 API 请求泛型收口计划

## 目标

- 禁止 `frontend/src/api` 继续使用 `request<any, T>`。
- 将 Axios 请求第一泛型从 `any` 收口为 `unknown`，保留第二泛型返回类型不变。
- 用守卫测试防止 API 层重新引入 `request<any, T>`。

## 非目标

- 不重写 `frontend/src/utils/request.ts`。
- 不改变接口路径、请求参数、响应返回类型或错误处理流程。
- 不处理非 API 层的全部 `any` 技术债。

## 当前事实

- P4 已收口 `useTokenRefresh.ts` 的 P2 遗留 `any`。
- `frontend/src/api` 仍有多处 `request<any, T>`，第一泛型会把 Axios 原始响应体继续标成 `any`。
- 这些调用已通过第二泛型声明前端实际返回类型，第一泛型可改为 `unknown` 降低类型逃逸。

## 决策日志

- 采用机械替换方案：`request<any,` → `request<unknown,`。
- 不新增封装函数，避免为了类型治理引入额外抽象层。

## 执行计划

- [x] 新增 API 请求泛型治理测试，并确认当前代码会失败。
- [x] 将 `frontend/src/api` 的 `request<any, T>` 改为 `request<unknown, T>`。
- [x] 运行目标测试和前端类型检查。
- [x] 运行前端质量、文档校验和 diff 检查。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| API 泛型守卫 | `pnpm --dir frontend run test:unit -- api-request-type-governance` |
| 前端类型检查 | `pnpm --dir frontend run type-check` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 文档校验 | `python3 scripts/validate_docs.py . --profile generic` |

## HARD-GATE

用户已要求继续推进，本轮按 P5 小切片执行；如类型检查显示需要重写请求层或接口返回结构，则先停下重新规划。

## 进度记录

- 2026-05-18：确认 P4 已合并，选定 `frontend/src/api` 的 `request<any, T>` 作为 P5 类型治理切片。
- 2026-05-18：新增 `api-request-type-governance` 守卫测试；RED 阶段失败并定位 14 个仍使用 `request<any, T>` 的 API 文件。
- 2026-05-18：将 API 层 `request<any, T>` 机械替换为 `request<unknown, T>`；目标测试和 `pnpm --dir frontend run type-check` 通过。
- 2026-05-18：`pnpm --dir frontend run quality`、`python3 scripts/validate_docs.py . --profile generic`、`git diff --check` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收口 `frontend/src/api` 的请求第一泛型，未修改接口路径、请求参数、返回类型或请求层逻辑。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径。
- 测试与验证：通过；API 泛型治理测试先红后绿，前端类型检查、完整前端质量聚合、文档校验和 diff 检查均通过。
- 复杂度检查：通过；新增守卫测试 35 行，本轮未新增业务函数或额外抽象。
- Document-refresh: not-needed。原因：未改变 API、数据库、架构契约或用户可见行为，只更新本轮任务计划与验证记录。
- 剩余风险：非 API 层仍存在部分历史 `any`，需要后续按模块继续治理。
- 潜在技术债：`frontend/src/utils/request.ts` 仍沿用 Axios 实例拦截器改变返回值的历史模式，后续若要进一步收紧应设计专用 request wrapper。
- 结论：通过。
