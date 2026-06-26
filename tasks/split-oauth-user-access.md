# FastAPI OAuth 用户访问逻辑拆分

## 目标

- 将 `fastapi/app/db/models/oauth.py` 中的权限查询、菜单查询和菜单树构建逻辑拆入专用 helper，降低用户模型文件复杂度。
- 保持 `Users.get_permissions()`、`Users.get_menus()`、`Users.has_perm()`、`Users.has_role()` 的方法名、返回语义和调用路径不变。
- 保持 OAuth 菜单接口、权限校验、缓存 key、缓存 TTL 和超级用户权限语义不变。

## 非目标

- 不修改 `Users` 数据库字段、表名、索引或关系定义。
- 不修改 OAuth API 路径、响应字段、前端动态路由格式或权限码。
- 不改登录、Token、验证码或用户服务逻辑。
- 不引入新的缓存 fallback、mock 成功路径或静默降级。

## 当前事实

- `fastapi/app/db/models/oauth.py` 当前 274 行，同时包含用户模型字段、权限查询、菜单查询、菜单树构建、角色判断。
- `fastapi/app/api/v1/oauth/routes/menus.py::get_user_menus` 通过 `current_user.get_menus()` 获取动态路由菜单。
- `fastapi/app/api/deps.py` 权限链路依赖 `current_user.has_perm()`。
- 现有测试覆盖 OAuth 登录、菜单接口和用户服务，但缺少对 `Users.get_permissions()`、`Users.get_menus()`、`Users.has_perm()`、`Users.has_role()` 的直接模型访问测试。

## 设计原则

- `oauth.py` 保留模型定义和兼容方法，复杂查询和树构建下沉到 helper。
- helper 不持有全局可变状态，所有依赖通过 `Users` 实例和参数传入。
- 缓存 key 与 TTL 保持原值，避免权限缓存行为变化。
- 菜单树输出结构保持原样，只把构建步骤命名化，避免在重构中改变前端契约。

## 方案对比

### 方案 A：新增 `oauth_user_access.py`

- 做法：新增 helper 模块，迁移权限集合查询、菜单 ID 查询、菜单 item 构建、空 children 清理等逻辑；`Users` 方法委托 helper。
- 优点：最小改动，模型文件明显收缩，外部调用路径稳定。
- 缺点：`Users` 仍保留薄方法作为兼容入口。

### 方案 B：新增独立 `UserAccessService`

- 做法：建立服务类，由路由和权限依赖直接注入服务。
- 优点：长期架构更纯粹。
- 缺点：需要改调用方和依赖链路，涉及认证/RBAC 核心路径，当前切片风险过大。

## 推荐方案

- 采用方案 A。它能解决当前模型文件职责混杂问题，同时不触碰 API、数据库或权限依赖入口。
- 淘汰方案 B 的原因：本轮目标是低风险治理，服务化会扩大调用链和测试面，不符合当前小步推进原则。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/db/models/oauth_user_access.py`，迁移权限查询、菜单查询和菜单树构建 helper。
- [x] P2 串行：更新 `fastapi/app/db/models/oauth.py`，让 `Users` 方法委托 helper，保留原公开方法。
- [x] P3 串行：新增 `fastapi/tests/test_oauth_user_access.py`，覆盖权限列表、权限命中、角色命中、菜单树和超级用户语义。
- [x] P4 串行：更新 `tasks/todo.md` 当前任务状态。
- [x] P5 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_oauth_user_access.py tests/test_oauth.py tests/test_permission_contracts.py -q`
- `cd fastapi && uv run ruff check app/db/models/oauth.py app/db/models/oauth_user_access.py tests/test_oauth_user_access.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## HARD-GATE

- 本线程已有用户确认“按顺序推进”，本轮按该确认继续执行。
- 若执行中发现需要修改数据库字段、OAuth API 响应、权限码或前端动态路由契约，立即停止并回到规划阶段。

## 进度记录

- [x] 已完成只读分析，确认 `oauth.py` 主要复杂度来自用户访问逻辑而非模型字段。
- [x] 已完成用户权限、菜单查询和菜单树构建 helper 拆分。
- [x] 已新增直接模型访问测试，覆盖权限、角色、菜单树和超级用户语义。

## 验证结果

- `cd fastapi && uv run ruff check app/db/models/oauth.py app/db/models/oauth_user_access.py tests/test_oauth_user_access.py`：通过。
- `cd fastapi && uv run pytest tests/test_oauth_user_access.py tests/test_oauth.py tests/test_permission_contracts.py -q`：24 passed，3 warnings。
- `cd fastapi && make quality`：561 passed，5 warnings，覆盖率 88.00%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分用户权限和菜单访问 helper，不修改用户模型字段、表名、索引、OAuth API、权限码或前端动态路由契约。
- 安全检查未发现新增 secret、mock 假成功、静默 fallback 或权限绕过；超级用户空权限列表和任意权限命中语义已由目标测试锁定。
- 复杂度检查通过，`oauth.py` 已从 274 行降至 169 行，新增 `oauth_user_access.py` 为 151 行，目标测试文件为 76 行。
- Document-refresh: not-needed，原因：本轮只调整内部模型 helper 组织，不改变用户可见 API、数据库结构或产品文档事实。
- 剩余风险：`Users.has_role()` 仍直接保留在模型内，逻辑很短且与角色关系强绑定，当前不单独拆分。
