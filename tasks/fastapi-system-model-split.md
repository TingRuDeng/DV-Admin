# FastAPI system model 拆分治理计划

## 目标

- 将 `fastapi/app/db/models/system.py` 从 339 行混合模型文件拆分为按领域组织的小模块。
- 保持 `from app.db.models.system import ...` 兼容入口不变，避免影响服务层、测试、导入脚本和 Tortoise 注册配置。
- 不改变表名、字段名、字段约束、索引、关联表、关联字段或 ORM 行为。

## 非目标

- 不修改数据库迁移策略，不新增旧表/旧字段 fallback。
- 不修改 `fastapi/app/core/config.py` 中的 Tortoise model module 配置。
- 不调整服务层、API 层或测试层导入路径。

## 当前事实

- `fastapi/app/db/models/system.py` 当前 339 行，包含 `Permissions`、`Roles`、`Departments`、`Notices`、`NoticeReads`、`DictData`、`DictItems`、`OperationLog`。
- 外部调用集中使用 `from app.db.models.system import ...`。
- Tortoise 配置通过 `app.db.models.system` 注册系统模型；因此本轮必须保留该模块中可发现的模型类导出。

## 决策日志

- 方案 A：新增 `system_permission.py`、`system_dept.py`、`system_notice.py`、`system_dict.py`、`system_log.py`，再由 `system.py` 统一 re-export。
  - 优点：外部兼容，Tortoise 注册模块不变，职责清晰，单文件低于 300 行。
  - 缺点：模型真实定义模块变化，需要用全量 FastAPI 门禁验证 Tortoise 发现和 FK 字符串注册。
- 方案 B：直接修改 Tortoise 配置，注册多个模型模块。
  - 优点：模型定义和注册模块更直接。
  - 缺点：影响配置、测试数据库初始化和契约校验面更大，本轮收益不足。
- 方案 C：只拆 `OperationLog` 或通知模型，其他保留。
  - 优点：改动更小。
  - 缺点：主文件仍然偏大，不能完整解决结构债。

推荐方案：采用方案 A。它保留原注册模块和导入入口，避免扩大运行时配置影响。

## 执行计划

- [x] P1 串行：完成现状分析与计划写入。
- [x] P2 串行：新增按领域拆分的模型模块。
- [x] P3 串行：将 `system.py` 收缩为兼容导出入口。
- [x] P4 串行：执行目标模型契约测试、FastAPI 质量门禁、文档校验和 diff 检查。
- [x] P5 串行：执行 review-gate。
- [ ] P6 串行：提交、推送、创建 PR 并等待 CI。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_import_django_model_contracts.py tests/test_import_django_data.py tests/test_import_django_data_golden.py -q`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分 FastAPI system 模型内部文件结构，并保留 `from app.db.models.system import ...` 兼容入口；不改变 Tortoise model module 配置、表名、字段名、字段约束、索引、关联表、关联字段或 API 行为。安全检查未发现本轮新增 secret、mock、fallback 或静默降级，敏感词扫描命中仅来自 `tasks/todo.md` 历史摘要。测试与验证通过：目标模型契约测试 33 passed；FastAPI `make quality` 通过，539 passed，覆盖率 84.98%；`python3 scripts/validate_docs.py . --profile generic` 通过；`git diff --check` 通过。复杂度检查通过，`system.py` 从 339 行收缩为 20 行兼容导出入口，新增模型文件均低于 300 行。Document-refresh: not-needed，原因：本轮是内部模型文件结构拆分，不改变用户可见 API、数据库结构或产品文档事实。剩余风险是 FastAPI `users.py`、`auth.py` 和 `user_service.py` 仍为既有大文件，需要后续独立规划治理。
- CI 修复补充：PR #176 首轮 Frontend Quality 在 `validate_model_contracts.py` 失败，根因是静态契约 loader 仍只扫描旧 `system.py` 单文件；已将拆分后的 `system_permission.py`、`system_dept.py`、`system_notice.py`、`system_dict.py`、`system_log.py` 纳入 `FASTAPI_MODEL_FILES`，并复核 `validate_model_contracts.py`、`validate_docs.py`、目标模型测试和 FastAPI `make quality` 均通过。
