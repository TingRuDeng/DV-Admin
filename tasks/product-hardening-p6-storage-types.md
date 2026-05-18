# P6 Storage 类型边界收口计划

## 目标

- 收口 `frontend/src/utils/storage.ts` 的写入参数类型，避免 `any` 继续从存储工具向外扩散。
- 保持 `localStorage` 与 `sessionStorage` 的 JSON 序列化/反序列化行为不变。
- 用守卫测试防止 `storage.ts` 重新引入 `any`。

## 非目标

- 不重写存储格式。
- 不改变 `Storage.get<T>` / `Storage.sessionGet<T>` 调用契约。
- 不处理组件层、CURD 兼容层或 WebSocket 模块的其他 `any`。

## 当前事实

- `Storage.set(key, value: any)` 与 `Storage.sessionSet(key, value: any)` 仍使用 `any`。
- 这两个入口只做 `JSON.stringify(value)`，改为 `unknown` 不影响运行时序列化行为。
- 现有 `frontend/src/utils/__tests__/storage.test.ts` 已覆盖字符串、数字、对象、默认值、删除与 session 存储行为。

## 决策日志

- 采用最小类型边界收口：`any` → `unknown`。
- 不新增泛型 set 方法，避免让调用方误以为写入类型会被运行时校验。

## 执行计划

- [x] 新增 `storage.ts` 类型治理测试，并确认当前代码会失败。
- [x] 将 `Storage.set` 和 `Storage.sessionSet` 的 `value` 参数改为 `unknown`。
- [x] 保持现有存储行为测试通过。
- [x] 运行前端类型检查、前端质量、文档校验和 diff 检查。
- [x] 使用 `review-gate` 做交付前审查。

## 验证矩阵

| 改动 | 验证命令 |
|------|----------|
| Storage 类型守卫 | `pnpm --dir frontend run test:unit -- storage-type-governance` |
| Storage 行为 | `pnpm --dir frontend run test:unit -- storage` |
| 前端类型检查 | `pnpm --dir frontend run type-check` |
| 前端质量 | `pnpm --dir frontend run quality` |
| 文档校验 | `python3 scripts/validate_docs.py . --profile generic` |

## HARD-GATE

用户已要求继续推进，本轮按 P6 小切片执行；如需要改变存储格式或调用契约，则先停下重新规划。

## 进度记录

- 2026-05-18：确认 P5 已合并，选定 `Storage.set/sessionSet` 的 `any` 参数作为 P6 类型治理切片。
- 2026-05-18：新增 `storage-type-governance` 守卫测试；RED 阶段失败并定位 `Storage.set` 与 `Storage.sessionSet` 两处 `any`。
- 2026-05-18：将写入参数改为 `unknown`；目标测试、原有存储行为测试和 `pnpm --dir frontend run type-check` 通过。
- 2026-05-18：`pnpm --dir frontend run quality`、`python3 scripts/validate_docs.py . --profile generic`、`git diff --check` 通过。

## Review 小结

- 终态：finished。
- Spec 符合度：通过；本轮只收口 `Storage.set/sessionSet` 写入参数类型，未改变存储格式、读取泛型或清理方法。
- 安全检查：通过；未新增 secret、mock、静默回退或伪成功路径。
- 测试与验证：通过；Storage 类型治理测试先红后绿，现有存储行为测试、前端类型检查、完整前端质量聚合、文档校验和 diff 检查均通过。
- 复杂度检查：通过；新增守卫测试 23 行，生产代码只修改两个参数类型。
- Document-refresh: not-needed。原因：未改变 API、数据库、架构契约或用户可见行为，只更新本轮任务计划与验证记录。
- 剩余风险：组件层、WebSocket 模块和 CURD 兼容层仍存在历史 `any`，需后续按模块继续治理。
- 潜在技术债：`Storage.get<T>` 仍依赖调用方指定返回类型，未做运行时 schema 校验。
- 结论：通过。
