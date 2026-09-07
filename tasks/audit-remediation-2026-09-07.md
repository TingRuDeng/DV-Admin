# 审查问题分批整改

## 目标与边界

按用户批准的计划处理 11 项审查问题。共享行为同步 Django、FastAPI 和前端，按子项拆分提交与 PR。
允许富文本外链和图片；暂缓 iframe 隔离、普通附件深度扫描、私有文件服务和批量旧密码升级。
不修改真实凭据、生产数据或来源不明的文件。

## 执行清单

- [x] 令牌撤销失败关闭、前端 503 处理、真实就绪探针（原 #1、#5）
- [x] 账号/IP 限速、短时冷却、Retry-After（原 #3）
- [x] 15-128 字符长口令、兼容哈希、统一密码策略端点（原 #6）
- [x] 角色授权、数据范围及受影响用户边界（原 #2）
- [x] 冻结锁文件构建生产镜像、产物测试（原 #11）
- [x] 持久媒体卷、Nginx 只读挂载与迁移说明（原 #4）
- [x] 双后端头像真实格式、解码及资源预算（原 #7）
- [x] 实际注册路由完整性守卫（原 #10）
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
- 提交 `7b2b641`，PR [#367](https://github.com/TingRuDeng/DV-Admin/pull/367)。首次 CI 揭示 `.env.example` 仍有 20 字符上限，且个人中心 Mock 未登记新策略接口；已以 `d37315b` 修正示例为 128、新增长度样例守卫和 Mock 长口令流程，19 条密码测试及独立端口真实 Chromium 用例通过，远端复验中。

### 第四项：角色授权边界

- 分支：`codex/audit-role-boundaries`，基于第三项；未混入部署/文件/性能整改。
- RED：FastAPI 6 条、Django 5 类行为失败，复现自授权、授予未持有权限、目标部门子树越界、修改范围外用户角色及改名绕过系统角色删除保护。
- 两端共享纯判定规则并各自执行事务内数据库重读；服务调用、兼容 PATCH、默认分配、导入、批删均覆盖。权限比较不使用排序或范围枚举等级；角色维护检查所有关联用户。
- 停用角色从有效权限/数据范围排除；API 和敏感字段权限使用数据库新鲜权限，展示缓存不承担安全裁决。默认角色涉及未来全局用户，仅超管维护。
- FastAPI quality：831 passed/1 skipped，覆盖率 88.75%，mypy 149 文件、Ruff/isort/SQLite 迁移通过；Django 全量 282 passed/1 skipped。两端分别有 16/12 条委派边界测试，覆盖多角色并集、默认角色、导入逐行结果和关联写入失败回滚。
- 真实浏览器两端各 6 流程通过（FastAPI pytest 1 passed；Django HTTP/浏览器 2 passed）。首次失败暴露普通管理员不能授予新建但尚未持有的菜单，测试明确断言 403 后改用独立超管完成初始化，不提升原普通管理员身份；其余受限授权流程保持原样。菜单编辑同样等待异步回填再输入。
- 前端 quality 99 files/308 tests、build 通过；根规则代数/字节一致性 5 tests、原根 unittest 24 tests、文档/API/模型/动态路由/迁移目录校验及 diff 检查通过。文档校验曾与 Playwright 清理 test-results 竞态，串行重跑通过，未修改 canonical validator。
- Review：最终授权不依赖展示缓存；系统 ROOT 身份标识不可被普通管理员授予。SQLite 不证明 MySQL 并发锁行为，不能据此宣称生产并发验收已完成。菜单对象本身的全局治理仍是明确边界。
- 第三项 PR #367 修正后五个远端门禁全部通过，未合并。

### 第五项：生产镜像锁定

- 分支：`codex/audit-production-images`，基于第四项；第四项提交 `01e5bd8` / PR #368 五个远端门禁全部通过，未合并。
- RED：新增镜像契约测试因缺少版本目录失败；实际 ARM64 构建暴露 asyncmy 需要 builder 编译器；实际 Django 镜像发现 `pro` 环境名未纳入 Redis 就绪检查，新增失败测试后修复。
- 两端 Python 3.11/uv 摘要固定，CI 同为 uv 0.8.13；完整 wheel 构建元数据、包数据、锁文件冻结，非开发/非 editable、UID/GID 10001。Django uv.lock 仅改项目安装类型，没有依赖升级。
- 实际镜像验证：两端 wheel/许可证资源、非 root/无开发工具、Redis 离线迁移、默认多 Worker 启动、Docker readiness 命令、Redis 故障 503/liveness 200 与恢复通过。脚本只创建并清理自己的临时容器/卷/网络。
- 本机产物：FastAPI `sha256:37f9d0219347e0937bba90d497330bf476f8410997edc25f1dca8a5e7978415d`；Django `sha256:d469e988a617d32dc476da1cb902794cd4fa92156f2e627016a28ae2fe4067c2`。这是本机 ARM64 镜像 ID，不是远端发布摘要。
- FastAPI quality 832 passed/1 skipped、88.76%；Django全量 282 passed/1 skipped，随后新增生产环境名的健康测试 7 passed；根测试 30 passed，文档/API/模型/迁移目录校验及 diff 通过。
- Review：实际 Django 使用既有 WSGI 入口，不宣称已验收 ASGI/WebSocket；Debian 编译依赖尚未快照锁定，不宣称逐字节重现。生产凭据、数据库及媒体未修改；媒体卷在下一子项处理。

### 第六项：媒体持久化

- 分支：`codex/audit-media-persistence`，基于第五项 `874d6af` / PR #369；第五项七个远端门禁（含两端 Linux 实际镜像）全部通过。
- RED：媒体配置守卫发现 Django 不支持 MEDIA_ROOT 环境覆盖、镜像目录与 Nginx 不一致、无只读持久卷。
- 两端生产镜像使用 `/data/media`，非 root UID/GID 10001；新生产 Compose 以一个后端覆盖文件选择实现、单例迁移先行、API 读写、Nginx 只读。开发默认不变，现有 FastAPI Compose 同步挂载。未搬动真实文件或修改数据库标识。
- 根测试 31 passed；Django 健康/头像/媒体 URL 13 passed、Ruff 通过；文档/API/模型校验通过。新增实际产物脚本经生产 Nginx 上传头像、检查只读卷、替换 API 容器后比较内容，并检查 503 透传。
- 本机 Docker 在本项验证中所有新容器均停于 Created（连仅输出 Python 版本的容器也无法启动，沙箱外同样失败）；已终止本次客户端并删除自身测试容器，没有重启 Docker/现有开发服务。本机实际媒体验收未完成，交由新增独立 Linux CI 产物门禁复验，结果另记，不以静态绿灯替代。
- Review：目录外链接不得迁入公开媒体卷；旧文件迁移和权限修复由维护者在维护窗口按 MEDIA_DEPLOYMENT.md 执行；不可直接互换两端数据库。只读 Nginx 配置在测试中用 docker cp 载入，媒体仍真实只读卷，避免宿主 Desktop 文件共享依赖。
- 提交 `8d2cbc9` / PR #370，七个远端门禁全部通过。Linux 实际生产镜像验证两端真实 Nginx 上传、只读卷、503 透传与 API 重建后相同内容仍可读；两套真实浏览器也通过。本机 Docker 阻塞仍是独立环境问题，不代表生产部署已执行。

### 第七项：头像真实内容校验

- 分支：`codex/audit-avatar-validation`，基于媒体子项。RED：FastAPI 六种非法头像返回成功；Django 放过扩展名伪装、尺寸、帧数、累计像素、超大小，并在保存失败时留下文件/新头像标识。
- 两端相同 Pillow 校验器：2 MiB/4096 单边/100 帧/3200 万累计像素，verify 后逐帧 load，先验证再持久化；FastAPI 在线程池解码。保存失败时文件清理与数据库事务回滚，不改原头像。
- 保留原格式兼容面及普通附件规则；FastAPI Pillow 从传递依赖改为显式依赖，锁文件仅补依赖声明，无版本升级。旧测试中的伪 PNG 和截断 GIF 替换为真实可解码样本，不降低校验。
- FastAPI quality 846 passed/1 skipped，覆盖率 89.06%、mypy 150 文件；Django Ruff/全量 285 passed/1 skipped；前端 quality 99 files/308 tests、build 通过。首次前端格式检查发现新长 GIF 常量需换行，Prettier 修正后通过。
- 真实浏览器两端各六流程通过（FastAPI pytest 1 passed/50.17s；Django HTTP/浏览器 2 passed/42.64s），头像上传后检查实际图片宽度。边界测试覆盖合法六种常见格式、100 帧、4096 单边、3200 万像素、2 MiB 和事务后置失败。
- 根测试 31 passed；文档/API/模型/组件路由/迁移目录与 diff 检查通过。Review：不做图片重编码、不删除元数据/附加内容、不扫描普通附件病毒、不更改公开媒体访问策略；未声称全面上传安全治理完成。

### 第八项：实际路由完整性

- 分支：`codex/audit-runtime-route-inventory`，基于第七项 `71ccc11` / PR #371；第七项七个远端门禁全部通过，未合并。
- RED：两端递归枚举实际注册路由，各发现 31 个尚未登记的入口；逐个审查后把业务入口登记为共享、后端独占或兼容，框架文档入口明确排除，没有自动接受快照。
- Django URLResolver/DRF actions 与 FastAPI routes/Mount 分别在自己的测试环境枚举；规范化后 Django 88、FastAPI 87 个业务 method/path。根校验器只检查纯目录自洽和测试入口，不导入框架。
- 新增子模块未登记路由、删除登记路由、方法变化及单独 HEAD/OPTIONS 均有失败守卫；仅排除明确健康/文档路径和伴随业务方法生成的 HEAD/OPTIONS。
- FastAPI 完整 quality：848 passed/1 skipped，覆盖率 89.06%，mypy 150 文件、Ruff/isort/迁移通过；Django Ruff/全量 287 passed/1 skipped；根 unittest 35 passed。文档/API/模型契约与 diff 检查通过。
- Review：登记不等于新增共享能力，也不代表所有补充路由已经具备字段/行为契约；保留既有静态证据检查作为快速校验。没有业务行为修改，第三批结束再运行前端全量门禁。

## 剩余风险

旧弱密码不追溯修改；共享初始密码仍需受控分发；媒体 URL 保持公开；普通附件深度检查和 iframe 隔离未纳入本轮。
