# 审查问题分批整改

## 目标与边界

按用户批准的计划处理 11 项审查问题。共享行为同步 Django、FastAPI 和前端，按子项拆分提交与 PR。
允许富文本外链和图片；暂缓 iframe 隔离、普通附件深度扫描、私有文件服务和批量旧密码升级。
不修改真实凭据、生产数据或来源不明的文件。

## 执行清单

- [x] 令牌撤销失败关闭、前端 503 处理、真实就绪探针（原 #1、#5）
- [x] 账号/IP 限速、短时冷却、Retry-After（原 #3）
- [x] 15-128 字符长口令、兼容哈希、统一密码策略端点（原 #6）
- [ ] 角色授权、数据范围及受影响用户边界（原 #2）
- [ ] 冻结锁文件构建生产镜像、产物测试（原 #11）
- [ ] 持久媒体卷、Nginx 只读挂载与迁移说明（原 #4）
- [ ] 双后端头像真实格式、解码及资源预算（原 #7）
- [ ] 实际注册路由完整性守卫（原 #10）
- [ ] 认证有效期文档事实修正（原 #13）
- [ ] 万级数据基线、数据范围子查询、分块导入查询（原 #12）

## 验证与审查

每项先记录失败测试，再修复并运行相关质量门禁。真实 Redis、独立实例、实际 Nginx/镜像与双后端浏览器验证分别记录，未运行不视为通过。
文档/API/模型契约校验和 `git diff --check` 随批次执行。提交、推送、PR、远端 CI 和部署是不同验收层次。

### 第一项：令牌撤销与就绪检查

- 状态：实现和本地验证完成，独立提交待远端审查。
- 分支：`codex/audit-auth-readiness`。
- 开始时工作区仅有未跟踪 `.pnpm-store/`，保留不动。
- RED：15 条生产撤销/就绪用例失败；前端刷新 503 触发错误退出；Django 生产 Redis 缺失仍报告就绪；已有但失效的数据库连接被误判健康。
- 真实 Redis 测试额外暴露未消费 refresh 可绕过用户级撤销；修复刷新链保留首次登录时间，并检查用户撤销标记。
- `make -C fastapi quality`：778 passed、1 skipped，覆盖率 88.07%，Ruff/isort/mypy 和 SQLite 迁移门禁通过。
- 新增独立进程测试 `tests/test_production_auth_http.py`：1 passed；两个真实生产模式 Uvicorn 进程验证撤销、并发刷新、Redis 启动故障及运行中故障恢复；Redis 离线时生产迁移成功。
- Django Ruff 和全量 pytest：259 passed、1 skipped、17 subtests passed；随后加强数据库探针，健康及配置定向测试 17 passed。
- 前端 `quality`：98 files、306 tests passed；`build` 通过。
- 双后端真实浏览器套件各 6 个流程通过（FastAPI pytest 1 passed；Django HTTP/浏览器 pytest 2 passed）。Chromium 在沙箱内启动被 macOS 拒绝，经许可在隔离的沙箱外测试环境重跑通过。
- 实际 Nginx 配置探针转发测试：1 passed，保留 upstream 503；不是生产镜像或真实部署验收。
- API、文档、模型契约校验与 `git diff --check` 通过。
- Review：修改限于本子项；开发 Redis 回退回归已由真实 HTTP 测试暴露并修正。保留退出仅撤销当前 access token 的既有范围；完整会话级退出并非本项交付。
- 待后续批次：实际生产镜像构建/迁移/探针与媒体持久化验收；远端 CI 结果单独记录。
- 提交 `370461d`，PR [#365](https://github.com/TingRuDeng/DV-Admin/pull/365)，五个远端质量/真实浏览器门禁均通过；尚未合并。

### 第二项：登录防刷

- 分支：`codex/audit-login-throttling`，基于第一项独立叠加，未混入密码/角色整改。
- RED：Django 与 FastAPI 两个入口连续 5 次失败仍非 429；固定窗口跨边界遗漏近期失败；未受信转发头可伪造日志 IP。
- 实现：两端打包字节一致的 Redis Lua 滑动窗口策略，Redis 服务端计时、账号 5 次/5 分钟后冷却 5 分钟、IP 60 次/分钟；429 保留 Retry-After，Redis 故障 503。所有环境的登录保护均无内存后备。
- 受信代理 IP/CIDR 显式配置，默认忽略转发头；项目 Uvicorn 启动入口禁用框架代理头预解析，日志与登录使用同一边界。
- 真实 Redis 定向测试 17 passed：窗口交界、到期、成功只清账号失败、拒绝不延长冷却、多连接并发、存储故障、代理链；两个生产 Uvicorn 进程的 65 次并发登录仅 60 次进入认证，伪造转发 IP 无效。
- FastAPI `UV_CACHE_DIR=/private/tmp/dv-admin-uv-cache make quality`：796 passed、1 skipped，覆盖率 88.43%，Ruff/isort/mypy/迁移通过。指定临时 uv 缓存是为避开本机沙箱拒绝读取默认缓存目录，不改变依赖锁。
- Django Ruff 通过；全量 pytest 264 passed、1 skipped。前端 quality 98 files/306 tests 与 build 通过。
- 双后端真实浏览器各 6 个流程通过；其后滑动窗口加强由真实 HTTP 和 Redis 定向用例验证，批次结束再次验收浏览器。曾同时运行浏览器导致共用 test-results 下 trace 冲突，Django 串行重跑通过；今后在同一工作区串行运行浏览器套件。
- API、文档、模型契约及 `git diff --check` 通过；429/503 纳入共享错误码目录。
- Review：未增加绕过限速的配置或测试开关；测试使用临时真实 Redis，只替换连接来源。剩余风险为共享出口整体限速和持续恶意触发短时冷却；不等价于 MFA 或完整 DDoS 防护。
- 提交 `ca00828`，PR [#366](https://github.com/TingRuDeng/DV-Admin/pull/366) 以第一项分支为基线，五个远端门禁均通过，尚未合并。

### 第三项：统一密码策略

- 分支：`codex/audit-password-policy`，基于第二项独立叠加。
- RED：FastAPI 8 条、Django 2 条密码用例暴露旧长度、自动裁剪和 bcrypt 长口令截断；新增策略端点返回 404；参数错误响应回显密码；前端缺少 Unicode 码点长度校验。
- 实现：两端相同策略和固定提交的 SecLists 10k 清单，附 MIT 许可证、来源元数据和 SHA-256；默认 15-128 字符、空格/中文/长口令、无组合要求。新建/导入/重置/个人改密/兼容入口校验，旧密码登录不追溯。
- FastAPI 新写入 PBKDF2-SHA256 600,000 轮，异步入口线程池计算，保留旧哈希验证；新策略端点及字段契约已登记。前端加载策略失败时阻止进入改密流程，登录不裁剪密码，重置成功不回显明文。
- 修正 FastAPI RequestValidationError 处理器注册，使用已有脱敏响应包裹，避免密码校验失败反射输入。
- 预检仅输出合规状态：`backend/.env.dev` 初始密码不合规；`fastapi/.env` 初始密码不合规且最小长度仍为 8；`backend/.env.test` 合规。未修改这些真实文件。升级前由配置维护者更新初始密码和长度配置；测试使用隔离环境覆盖，不代表实际配置已完成升级。
- FastAPI 完整 quality：814 passed/1 skipped、覆盖率 88.59%，Ruff/isort/mypy 147 文件及 SQLite 迁移全部通过；为不触碰旧本地配置，命令显式使用测试用 `PASSWORD_MIN_LENGTH/DEFAULT_PASSWORD` 和临时 uv 缓存覆盖。Django Ruff/全量 270 passed/1 skipped；根 unittest 24 passed。
- 前端 quality 99 files/308 tests 与 build 通过；两套真实浏览器各 6 流程通过（FastAPI pytest 1 passed，Django HTTP/浏览器 2 passed），包含密码掩码、无明文提示和新密码登录。
- 浏览器首次在用户禁用步骤暴露既有抽屉异步回填竞态；测试改为等待昵称回填后操作默认开关，重跑通过。未混入抽屉业务重构，加载期间仍可编辑属于后续 UX 风险。
- API、文档、模型契约、py_compile 和 diff 检查通过。Review：无数据库迁移，无旧密码改写；参数校验错误包裹修复仍保留原 HTTP 422，敏感输入不进入响应。

## 剩余风险

旧弱密码不追溯修改；共享初始密码仍需受控分发；媒体 URL 保持公开；普通附件深度检查和 iframe 隔离未纳入本轮。
