# API 路由覆盖契约增强计划

## 目标

- 在现有端点契约证据校验基础上，增加“已登记关键端点必须能对应到双后端真实路由”的静态守卫。
- 优先覆盖系统管理、认证、文件上传删除这些已进入 `scripts/api_endpoint_contracts.py` 的关键端点。
- 降低 `docs/API_ENDPOINTS.md`、前端 API 文件、Django URL、FastAPI router 之间继续漂移的风险。

## 非目标

- 不自动生成完整 API 文档。
- 不在本轮新增业务端点。
- 不修改现有 API 路径、权限码、请求字段或响应字段。
- 不把 FastAPI 独占或 Django 独占能力强行登记为双后端共享能力。

## 当前事实

- `scripts/validate_api_contracts.py` 当前会校验契约文件存在、文档片段、测试片段、证据文件和证据片段。
- `scripts/api_endpoint_contracts.py` 当前维护 `CRITICAL_ENDPOINT_CONTRACTS` 和 `REQUIRED_ENDPOINT_KEYS`。
- Django 系统路由集中在 `backend/drf_admin/apps/system/urls.py`，router 注册覆盖 users/roles/menus/dicts/dict-items/departments，显式 path 覆盖 notices/logs/options 等。
- FastAPI v1 路由入口为 `fastapi/app/api/v1/__init__.py`，系统路由由 `fastapi/app/api/v1/system/__init__.py` include 到 users/roles/menus/departments/dicts/dict-items/notices/logs。
- 现有校验仍偏“证据片段存在”，没有统一解析契约路径并检查路由入口是否至少覆盖对应前缀。

## 决策日志

- 选择静态路由覆盖守卫，不启动服务抓 OpenAPI，避免新增运行时依赖和环境波动。
- 第一轮只覆盖已登记的关键契约，不扫描全仓所有路由，避免把未确认端点误判为债务。
- Django 与 FastAPI 采用不同解析策略：Django 以 `urlpatterns` 和 `AdminRouter.register` 为主；FastAPI 以 `include_router` 前缀和端点装饰器片段为主。

## 方案对比

### 方案 A：静态 AST/文本解析路由覆盖

- 优点：速度快，能接入 `python3 scripts/validate_api_contracts.py .`，不需要启动数据库或后端服务。
- 缺点：只能验证路由注册形态，不能验证运行时中间件、权限和响应行为。

### 方案 B：启动后端并抓 OpenAPI/URLConf

- 优点：更接近真实运行时。
- 缺点：需要服务启动、环境变量、数据库和端口协调；Django/FastAPI 两套实现的启动成本高，不适合作为轻量契约门禁第一步。

## 推荐方案

采用方案 A。先把关键端点和路由入口的覆盖关系静态锁住，后续如果需要运行时 OpenAPI 对账，再作为第二轮增强。

## 执行计划

- [x] 新增 `scripts/api_route_coverage_validation.py`
  - `validate_route_coverage(root: Path) -> list[str]`
  - 读取 `scripts.api_endpoint_contracts.iter_critical_endpoint_contracts()`
  - 对 Django/FastAPI 路由入口做最小静态覆盖判断
- [x] 更新 `scripts/validate_api_contracts.py`
  - import 并调用 `validate_route_coverage(root)`
- [x] 补 Django 结构测试
  - 修改 `backend/drf_admin/utils/test_docs_validator_structure.py` 或新增 API 契约结构测试
  - 断言路由覆盖校验已从 CLI 主入口拆出
- [x] 根据校验结果补齐必要的路由映射例外
  - 文件接口为 FastAPI 独占，按现有能力契约/证据处理
  - 认证、系统管理共享端点必须双端覆盖
- [x] 更新任务记录
  - 完成后回写本文件进度、验证结果和 Review 小结

## 验证矩阵

- `python3 scripts/validate_api_contracts.py .`
- `python3 -m py_compile scripts/validate_api_contracts.py scripts/api_route_coverage_validation.py`
- `cd backend && uv run pytest drf_admin/utils/test_docs_validator_structure.py -q`
- `cd backend && uv run ruff check drf_admin/utils/test_docs_validator_structure.py`
- `git diff --check`

## HARD-GATE

用户确认前不进行实现代码修改。本文件只是下一轮执行计划。

## 进度记录

- 新增 `scripts/api_route_coverage_validation.py`，静态读取 Django OAuth/system URLConf、AdminRouter 注册、DRF detail action，以及 FastAPI v1/system router include 前缀。
- `scripts/validate_api_contracts.py` 已接入 `validate_route_coverage(root)`。
- `backend/drf_admin/utils/test_docs_validator_structure.py` 已补结构测试，防止路由覆盖规则堆回 API 契约 CLI。
- 首次运行发现并显式处理两类真实路由形态：
  - `/api/v1/files/` 归一化后无二级路径片段，按 FastAPI 一级 `files.router` 覆盖。
  - Django 通知更新和删除共用 `notices/<str:ids>` 路由，校验时允许 `{ids}` 映射为单 ID 更新路径。

## 验证结果

- `python3 scripts/validate_api_contracts.py .`：通过。
- `python3 -m py_compile scripts/validate_api_contracts.py scripts/api_route_coverage_validation.py`：通过。
- `cd backend && uv run pytest drf_admin/utils/test_docs_validator_structure.py -q`：3 passed。
- `cd backend && uv run ruff check drf_admin/utils/test_docs_validator_structure.py`：通过。
- `git diff --check`：通过。

## Review 小结

- 本轮只增强契约校验与结构测试，没有修改业务路由、权限码、请求字段或响应字段。
- 静态校验覆盖已登记关键端点；未登记端点仍不作为本轮债务处理。
- 剩余限制：该守卫只确认路由入口覆盖，不替代运行时权限、响应结构和 OpenAPI 对账。
