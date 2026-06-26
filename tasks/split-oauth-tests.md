# FastAPI OAuth 接口测试拆分

## 目标

- 将 `fastapi/tests/test_oauth.py` 按职责拆为登录、验证码登录、会话信息三个测试文件。
- 保持 OAuth 接口测试断言、fixture 使用和接口路径不变。
- 降低单文件维护成本，让登录、验证码和会话菜单测试可以分别扩展。

## 非目标

- 不修改 OAuth 运行时代码。
- 不调整登录、验证码、用户信息、菜单或登出接口契约。
- 不处理 `test_oauth_schemas.py`、`test_oauth_user_access.py` 的后续拆分。
- 不引入新的 mock、fallback、跳过测试或静默降级。

## 当前事实

- 当前分支基于 `master` 最新提交 `9b9f766` 创建。
- `fastapi/tests/test_oauth.py` 当前为 255 行，集中覆盖登录、验证码、带验证码登录、用户信息、菜单路由和登出。
- 本轮只做测试结构治理，不修改 `app/api/v1/oauth/` 运行时代码。

## 决策日志

- 方案 A：拆为 login、captcha、session 三个文件。
  - 优点：按业务入口分组，文件数量适中，迁移风险低。
  - 缺点：captcha 文件同时包含验证码接口和带验证码登录。
- 方案 B：拆为 login、captcha、login_with_captcha、info、menus、logout 六个文件。
  - 优点：职责最细。
  - 缺点：当前总行数 255，拆成六个文件会制造过多碎片，收益不足。
- 结论：采用方案 A。先按主要行为域分离，保持简单可维护。

## 执行计划

- [x] 串行：创建 `fastapi/tests/test_oauth_login.py`，迁移基础登录测试。
- [x] 串行：创建 `fastapi/tests/test_oauth_captcha.py`，迁移验证码接口和带验证码登录测试。
- [x] 串行：创建 `fastapi/tests/test_oauth_session.py`，迁移用户信息、菜单和登出测试。
- [x] 串行：删除原 `fastapi/tests/test_oauth.py`。
- [x] 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_oauth_login.py tests/test_oauth_captcha.py tests/test_oauth_session.py tests/test_oauth_schemas.py tests/test_oauth_user_access.py -q`
- `cd fastapi && uv run ruff check tests/test_oauth_login.py tests/test_oauth_captcha.py tests/test_oauth_session.py tests/test_oauth_schemas.py tests/test_oauth_user_access.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## 进度记录

- 已建立任务计划。
- 已将 OAuth 接口测试拆为 login/captcha/session 三个职责文件。
- 已完成目标测试、FastAPI 聚合质量门禁、文档校验和 diff 检查。

## 验证结果

- `cd fastapi && uv run pytest tests/test_oauth_login.py tests/test_oauth_captcha.py tests/test_oauth_session.py tests/test_oauth_schemas.py tests/test_oauth_user_access.py -q`：23 passed，3 warnings。
- `cd fastapi && uv run ruff check tests/test_oauth_login.py tests/test_oauth_captcha.py tests/test_oauth_session.py tests/test_oauth_schemas.py tests/test_oauth_user_access.py`：All checks passed。
- `cd fastapi && make quality`：565 passed，5 warnings，覆盖率 88.05%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

Review-gate：finished；Spec 符合度通过，本轮只拆分 `fastapi/tests/test_oauth.py`，未修改 OAuth 运行时代码、登录/验证码/用户信息/菜单/登出接口契约；安全检查未发现新增 secret、mock 假成功或静默 fallback；复杂度检查通过，拆分后 login/captcha/session 三个测试文件分别为 67、153、50 行，均低于 300 行；Document-refresh: not-needed，原因：本轮是测试结构治理，不改变用户可见 API、数据库事实或产品文档内容；剩余风险是 `test_oauth_captcha.py` 仍包含验证码接口与验证码登录两类场景，但体量可控，暂不继续拆细。
