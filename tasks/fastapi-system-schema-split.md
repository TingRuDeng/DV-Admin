# FastAPI system schema 拆分治理计划

## 目标

- 将 `fastapi/app/schemas/system.py` 从 545 行混合 schema 文件拆分为按业务域组织的小模块。
- 保持 `from app.schemas.system import ...` 兼容入口不变，避免影响 API 层、服务层和测试层。
- 不改变字段名、别名、默认值、校验器、响应结构或分页兼容属性。

## 非目标

- 不修改 API 路径、权限码、数据库模型或运行时业务逻辑。
- 不拆分 `fastapi/app/db/models/system.py`，该文件后续单独治理。
- 不改调用方导入路径，除非验证证明必须调整。

## 当前事实

- `fastapi/app/schemas/system.py` 当前 545 行，包含用户、角色、通知、菜单、部门、字典、批量删除、用户导入和操作日志 schema。
- 外部调用集中使用 `from app.schemas.system import ...`，调用方覆盖 API、service 和测试。
- `fastapi/app/schemas/__init__.py` 也通过 `app.schemas.system` 聚合导出这些类型。

## 决策日志

- 方案 A：新增 `system_user.py`、`system_role.py`、`system_notice.py`、`system_menu.py`、`system_dept.py`、`system_dict.py`、`system_common.py`、`system_log.py`，再由 `system.py` 统一 re-export。
  - 优点：外部兼容，职责清楚，单文件容易低于 300 行。
  - 缺点：模块数量增加，需要维护 `system.py` 导出清单。
- 方案 B：直接把 `system.py` 改成包目录 `system/__init__.py`。
  - 优点：目录结构更自然。
  - 缺点：需要删除同名文件并调整更多 import，迁移面更大。
- 方案 C：只把日志和通知拆出去，其余保留。
  - 优点：改动更小。
  - 缺点：主文件仍然偏大，后续还会继续膨胀。

推荐方案：采用方案 A。它保留兼容入口，拆分粒度与业务域一致，影响范围最小。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增按业务域拆分的 schema 模块。
- [x] P3 串行：将 `system.py` 收缩为兼容导出入口。
- [x] P4 串行：执行目标 schema/import 验证、FastAPI 质量门禁、文档校验和 diff 检查。
- [x] P5 串行：执行 review-gate。
- [ ] P6 串行：提交、推送、创建 PR 并等待 CI。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_pagination_schema_compat.py tests/test_dict_service_dicts.py tests/test_dict_service_items.py tests/test_dict_service_item_flat.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

Review-gate：finished。Spec 符合度通过，本轮只拆分 FastAPI system schema 内部文件结构，并保留 `from app.schemas.system import ...` 兼容入口；不改变字段名、别名、默认值、校验器、响应结构、分页兼容属性、数据库结构或 API 路径。安全检查未发现本轮新增 secret、mock、fallback 或静默降级，敏感词扫描命中仅来自 `tasks/todo.md` 历史摘要。测试与验证通过：目标 schema/import 测试 52 passed；FastAPI `make quality` 通过，539 passed，覆盖率 84.92%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。复杂度检查通过，`system.py` 从 545 行收缩为 85 行兼容导出入口，新增 schema 文件均低于 300 行。Document-refresh: not-needed，原因：本轮是内部 schema 文件结构拆分，不改变用户可见 API、数据库结构或产品文档事实。剩余风险是 `fastapi/app/db/models/system.py` 仍为既有超大模型文件，需要后续独立治理。
