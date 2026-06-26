# FastAPI 验证码服务拆分

## 目标

- 将 `fastapi/app/services/captcha_service.py` 中的缓存实现与服务编排拆开，降低认证边界文件复杂度。
- 保持 `CaptchaService`、`get_captcha_service()`、`create_captcha()`、`verify_captcha()` 的导入路径和行为不变。
- 保持 OAuth 验证码接口、登录验证码校验、一次性使用语义和大小写不敏感校验不变。

## 非目标

- 不修改验证码图片生成逻辑。
- 不修改登录接口是否强制验证码的产品语义。
- 不新增 Redis 连接失败后的静默成功路径。
- 不修改 API 路径、响应字段、数据库模型或前端调用。

## 当前事实

- `fastapi/app/services/captcha_service.py` 当前 277 行，同时包含 `CaptchaCache`、`MemoryCaptchaCache`、`RedisCaptchaCache`、`CaptchaService`、全局单例和便捷函数。
- OAuth 路由通过 `fastapi/app/api/v1/oauth/routes/captcha.py::get_captcha` 调用 `create_captcha()`。
- 登录路由通过 `fastapi/app/api/v1/oauth/routes/login.py::login` 调用 `verify_captcha()`。
- 现有测试覆盖 `fastapi/tests/test_captcha_service.py`、`fastapi/tests/test_captcha.py`、`fastapi/tests/test_oauth.py`。

## 设计原则

- 保留 `captcha_service.py` 作为兼容入口，避免修改外部调用点。
- 将纯缓存实现拆入专用模块，服务入口只保留业务编排和兼容导出。
- 不引入新 fallback，不改变 Redis 缺包或连接异常的暴露语义。
- 优先用现有测试证明行为不变，必要时补充缓存 helper 的目标测试。

## 方案对比

### 方案 A：只拆缓存模块

- 做法：新增 `captcha_cache.py`，迁移 `CaptchaCache`、`MemoryCaptchaCache`、`RedisCaptchaCache`，`captcha_service.py` 保留服务编排和兼容导入。
- 优点：改动最小，调用路径稳定，能直接把缓存职责从服务入口剥离。
- 缺点：单例工厂仍留在服务入口，后续如果继续扩展可能还需二次拆分。

### 方案 B：拆成 cache、factory、service 三个模块

- 做法：缓存实现、单例工厂、业务服务分别拆文件。
- 优点：职责最彻底。
- 缺点：本轮涉及认证边界，拆得过细会扩大导入和测试调整面，收益不足。

## 推荐方案

- 采用方案 A。它能解决当前文件职责混杂的主要问题，同时保持导入路径和行为稳定。
- 淘汰方案 B 的原因：当前文件只有 277 行，单例工厂逻辑较短，过早三拆会增加模块跳转和回归风险。

## 执行计划

- [x] P1 串行：新增 `fastapi/app/services/captcha_cache.py`，迁移缓存接口、内存缓存和 Redis 缓存。
- [x] P2 串行：更新 `fastapi/app/services/captcha_service.py`，从新模块导入缓存类，保留兼容导出。
- [x] P3 串行：按需补充或调整验证码服务测试，锁定内存缓存过期清理、一次性删除和验证码大小写不敏感行为。
- [x] P4 串行：更新 `tasks/todo.md` 当前任务状态。
- [x] P5 串行：运行目标测试、FastAPI 质量门禁、文档校验和 diff 检查。

## 验证矩阵

- `cd fastapi && uv run pytest tests/test_captcha_service.py tests/test_captcha.py tests/test_oauth.py -q`
- `cd fastapi && uv run ruff check app/services/captcha_service.py app/services/captcha_cache.py tests/test_captcha_service.py`
- `cd fastapi && make quality`
- `python3 scripts/validate_docs.py . --profile generic`
- `python3 -m py_compile scripts/validate_docs.py`
- `git diff --check`

## HARD-GATE

- 本线程已有用户确认“按顺序推进”，本轮按该确认继续执行。
- 若执行中发现需要修改 OAuth API、登录语义、Redis 降级策略或前端调用，立即停止并回到规划阶段。

## 进度记录

- [x] 已完成只读分析，确认验证码服务职责混杂且调用点集中。
- [x] 已完成缓存模块拆分，`captcha_service.py` 保留服务编排和兼容导出。
- [x] 已补充验证码服务目标测试，覆盖大小写不敏感、默认删除、保留验证码和过期删除。

## 验证结果

- `cd fastapi && uv run ruff check app/services/captcha_service.py app/services/captcha_cache.py tests/test_captcha_service.py`：通过。
- `cd fastapi && uv run pytest tests/test_captcha_service.py tests/test_captcha.py tests/test_oauth.py -q`：26 passed，3 warnings。
- `cd fastapi && make quality`：557 passed，5 warnings，覆盖率 87.42%。
- `python3 scripts/validate_docs.py . --profile generic`：通过。
- `python3 -m py_compile scripts/validate_docs.py`：通过。
- `git diff --check`：通过。

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只拆分验证码缓存实现，不修改 OAuth API、登录验证码语义、验证码图片生成或前端调用。
- 安全检查未发现新增 secret、硬编码凭据、mock 假成功或新增静默 fallback；Redis 缺包仍显式抛出运行时错误。
- 复杂度检查通过，`captcha_service.py` 已从 277 行降至 160 行，新增 `captcha_cache.py` 为 122 行，目标测试文件为 89 行。
- Document-refresh: not-needed，原因：本轮只调整内部模块组织，不改变用户可见 API、数据库结构或产品文档事实。
- 剩余风险：`get_captcha_service()` 的全局单例工厂仍保留在 `captcha_service.py`，后续如继续治理认证边界可单独评估是否拆出工厂模块。
