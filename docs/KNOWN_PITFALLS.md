---
ai_summary:
  purpose: "沉淀 DV-Admin 中已验证的命名、权限、迁移、联调和环境陷阱。"
  read_when:
    - "开始 bug 排查前"
    - "修改鉴权、路由、缓存、迁移或联调流程前"
  source_of_truth:
    - "backend/drf_admin/settings.py"
    - "backend/drf_admin/utils/middleware.py"
    - "backend/drf_admin/utils/permissions.py"
    - "frontend/src/store/modules/permission-store.ts"
    - "frontend/src/store/modules/dict-store.ts"
    - "frontend/vite.config.ts"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "git ls-files backend/drf_admin/settings.py frontend/vite.config.ts"
  stale_when:
    - "已记录陷阱被修复或实现路径迁移"
    - "权限、命名转换、缓存或启动流程变化"
---

# DV-Admin 已知陷阱和常见错误

> 本文档只记录已复现、可验证的项目陷阱和排查路径。

## Purpose

沉淀已复现、可验证的工程陷阱，避免团队和代理重复踩坑。

## Source of truth

- `backend/drf_admin/settings.py`
- `backend/drf_admin/utils/middleware.py`
- `backend/drf_admin/utils/permissions.py`
- `frontend/src/store/modules/permission-store.ts`
- `frontend/src/store/modules/dict-store.ts`
- `frontend/vite.config.ts`

## Key facts

- 命名转换、权限白名单、双后端契约差异是高频误读点。
- 每条陷阱都应能映射到代码路径、配置项或可执行命令。
- 新陷阱需要先有复现证据再进入本文档。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- full: `pnpm --dir frontend run quality`

## Stale when

- 陷阱对应代码被删除、替换或彻底修复。
- 新增高频陷阱但未回写本文档。

---

## 命名转换陷阱

### 陷阱 1：手动转换命名格式

**问题描述：**
开发者在前端或后端手动转换命名格式（camelCase ↔ snake_case），导致数据不一致。

**错误示例：**
```typescript
// 前端错误：手动转换为 snake_case
const data = {
  user_name: 'admin',  // 错误！应该用 userName
  dept_id: 1           // 错误！应该用 deptId
}
```

```python
# 后端错误：手动转换为 camelCase
return Response({
    'userName': user.username,  # 错误！应该用 user_name
    'deptId': user.dept_id      # 错误！应该用 dept_id
})
```

**正确做法：**
- 前端始终使用 camelCase
- 后端始终使用 snake_case
- 让中间件自动处理转换

**相关配置：**
- Django: `djangorestframework_camel_case.middleware.CamelCaseMiddleWare`
- FastAPI: 响应格式统一为 `{code, message, data}`

---

### 陷阱 2：日志中的命名格式

**问题描述：**
查看后端日志时，发现字段名是 snake_case，误以为是前端传错了。

**解释：**
这是正常现象。中间件在日志记录之后才进行转换，日志中看到的是原始格式。

**验证方法：**
检查前端实际发送的请求（浏览器开发者工具 Network 面板）。

---

## 数据库迁移陷阱

### 陷阱 3：迁移文件冲突

**问题描述：**
执行 `migrate` 时报错，提示迁移文件冲突或找不到迁移文件。

**解决方案：**
```bash
# 删除所有迁移文件
find ./ -type d -name "migrations"|grep -v "venv" |xargs rm -rf

# 重新创建迁移
uv run python manage.py makemigrations oauth system --env dev

# 执行迁移
uv run python manage.py migrate --env dev
```

**预防措施：**
- 提交代码前确保迁移文件已包含
- 多人协作时，先 pull 再创建新迁移

---

### 陷阱 4：SQLite 到 MySQL 迁移

**问题描述：**
开发环境使用 SQLite，生产环境使用 MySQL，迁移时出现数据类型不兼容。

**常见问题：**
- SQLite 的 `BOOLEAN` 在 MySQL 中是 `TINYINT(1)`
- SQLite 的 `JSON` 字段处理方式不同
- 自增主键起始值不同

**解决方案：**
1. 使用 Django 的 `dumpdata` 和 `loaddata` 导出导入数据
2. 检查 SQL 兼容性
3. 在 MySQL 环境下重新运行测试
4. 如果通过 MCP 直连本地 SQLite 开发库排查问题，记得它只反映开发环境数据，不应直接据此判断生产 MySQL 的查询、锁或字段行为

---

### 陷阱 4.1：FastAPI 迁移基线被自动建表掩盖

**问题描述：**
开发环境通过 `generate_schemas()` 能正常启动，但模型变更没有对应版本化迁移，部署到既有数据库后出现字段、索引或约束漂移。

**已验证事实：**
- FastAPI 使用 Tortoise ORM 1.1.7 内置迁移能力，迁移配置位于 `app.db.migration_config.TORTOISE_ORM`
- `app/db/migrations/0001_initial.py` 是当前 schema 基线
- 新增非空列时，仅设置 ORM `default` 不一定会生成数据库默认值；已有数据的 SQLite 升级会报 `Cannot add a NOT NULL column with default value NULL`
- 当前 MySQL 8 迁移目标不接受 JSON 列的普通数据库默认值；JSON 非空列应先按可空列新增、回填既有行，再收紧为非空，并仅在 ORM 层保留 `default`
- Tortoise ORM 1.1.7 在 SQLite 上通过重建表执行 `AlterField`，重建后不会自动恢复已有普通索引；迁移必须显式恢复并由增量校验确认索引仍存在
- Tortoise 迁移写入器要求 `Meta.indexes` 使用 `Index` 对象；元组写法不能可靠生成迁移
- SQLite 原子迁移按 ASCII 分号拆分 SQL；字段 description 中不能包含 ASCII `;`，中文说明应使用全角 `；`

**解决方案：**
1. 模型变更同时生成并提交迁移，运行 `make -C fastapi migration-check`
2. 新增非空列必须用带既有数据的增量测试验证；非 JSON 字段确需数据库默认值时显式设置 `db_default`，JSON 字段使用“可空新增 → 回填 → 收紧非空”迁移
3. 全新数据库直接执行 `migrate`
4. 既有库接管前先备份并核对 schema，确认一致后仅执行一次 `migrate --fake`
5. CI 同时保留 SQLite 全路径校验，以及 MySQL 8 空库与增量迁移 smoke
6. 部署使用一次性迁移容器或单例 Job，成功后再启动 API；禁止每个 Uvicorn Worker 自行迁移

---

## 认证授权陷阱

### 陷阱 5：Token 过期处理

**问题描述：**
前端收到 401 错误后，没有正确刷新 Token，导致用户被强制登出。

**正确处理流程：**
1. 收到 401 错误
2. 检查是否有 Refresh Token
3. 使用 Refresh Token 获取新的 Access Token
4. 保存后端轮换返回的新 Refresh Token；旧令牌不能再次使用
5. 原请求只重试一次
6. 如果刷新失败或重试后仍返回 `40001`，跳转登录页

FastAPI 多实例部署必须保持 Redis 可用，才能跨进程原子消费 Refresh Token；Redis 未初始化时的内存降级只用于非生产单进程。生产环境 Redis 未初始化或命令执行失败时，刷新流程都失败关闭，不签发新令牌。

**相关代码：**
- 前端：`frontend/src/composables/auth/useTokenRefresh.ts`
- 后端：`backend/drf_admin/apps/oauth/views/oauth.py`

---

### 陷阱 6：权限验证顺序

**问题描述：**
新增 API 后，前端调用返回 403，但用户明明有权限。

**可能原因：**
1. API 路径未添加到权限白名单（如果不需要权限）
2. 权限标识未正确配置
3. 用户角色未关联权限

**检查步骤：**
```python
# 1. 检查权限白名单
# backend/drf_admin/settings.py
WHITE_LIST = [
    '/api/v1/oauth/login/',
    # ...
]

# 2. 检查权限标识
# 数据库中 system_permissions 表的 perm 字段

# 3. 检查角色-权限关联
# 数据库中 system_roles_to_system_permissions 表
```

---

### 陷阱 6.1：只给列表加数据范围过滤

**问题描述：**
用户列表看起来已经隔离，但详情、下拉选项、密码重置、批量删除或统计接口仍直接使用全表查询，导致越权探测、写入或聚合泄露。

**正确做法：**
- 数据范围必须覆盖同一资源的所有对象级读写、聚合及导入导出路径，不能只覆盖分页列表
- 范围外 ID 与真实不存在 ID 统一返回 404，避免泄露对象是否存在
- 批量操作先确认所有目标都存在且可见，再执行一次写入；禁止部分成功
- 创建用户或变更部门时校验目标部门范围，不能只校验被修改用户当前是否可见

**相关代码：**
- Django：`drf_admin/apps/system/services/data_scope.py`、`views/users.py`、`views/logs.py`
- FastAPI：`app/services/system/data_scope.py`、`user_services/`、`log_service.py`

---

### 陷阱 6.2：角色权限变化后仍命中旧权限缓存

**问题描述：**
管理员已经为角色授权或撤权，重新登录后动态菜单已经变化，但关联用户访问接口时仍沿用变更前的权限，造成错误的 403 或撤权后仍返回 200。

**原因：**
权限判断缓存以用户为单位，而授权入口修改的是角色与权限的多对多关系。若 Django 没有加载对应 signal，或 FastAPI 只更新角色关系而未清理关联用户缓存，数据库与运行时权限会短暂或持续不一致。

**正确做法：**
1. Django 的 `SystemConfig.ready()` 必须加载 `apps/system/signals.py`，由 `m2m_changed` 清理关联用户权限缓存。
2. FastAPI 的角色授权服务必须清理所有关联用户的权限与菜单缓存。
3. 权限闭环测试必须使用新登录会话，并同时验证动态菜单、按钮和受保护 API；不能只断言数据库关系已更新。

**相关代码：**
- Django：`backend/drf_admin/apps/system/apps.py`、`backend/drf_admin/apps/system/signals.py`
- FastAPI：`fastapi/app/services/system/role_service.py`
- 双后端浏览器闭环：`frontend/e2e/real-backend-smoke.spec.ts`

---

### 陷阱 6.3：菜单改名或删除后仍返回旧路由与权限

**问题描述：**
管理员修改菜单标题后，用户重新登录仍看到旧标题；删除菜单或其按钮权限后，动态路由虽然可能消失，但受保护 API 仍可能返回 200。

**原因：**
菜单更新和权限对象删除并不等同于角色授权接口变更。Django 级联删除角色-权限中间表时不会可靠触发 `m2m_changed`；FastAPI 若只在 `RoleService` 清缓存，`MenuService` 更新或删除已授权对象时会保留旧的用户菜单和权限缓存。

**正确做法：**
1. Django 在权限对象删除前查询关联角色用户，并清除这些用户的权限缓存。
2. FastAPI 在已授权菜单或按钮更新、删除前确定受影响用户，写入成功后同时清除权限和动态菜单缓存。
3. 菜单写入闭环使用新登录会话验证改名后的侧栏标题，并在删除菜单及子按钮后同时验证路由消失和受保护 API 返回 403。

**相关代码：**
- Django：`backend/drf_admin/apps/system/signals.py`
- FastAPI：`fastapi/app/services/system/access_cache.py`、`fastapi/app/services/system/menu_service.py`
- 双后端浏览器闭环：`frontend/e2e/real-backend-smoke.spec.ts`

---

## 前端开发陷阱

### 陷阱 7：动态路由缓存

**问题描述：**
修改后端菜单配置后，前端路由没有更新，仍然显示旧菜单。

**原因：**
前端缓存了路由数据，没有重新获取。

**解决方案：**
1. 清除浏览器 localStorage
2. 重新登录
3. 或者在代码中添加路由刷新逻辑

**相关代码：**
- `frontend/src/store/modules/permission-store.ts`

---

### 陷阱 8：字典缓存不同步

**问题描述：**
修改字典数据后，前端显示的字典标签没有更新。

**原因：**
前端字典缓存未清除。

**解决方案：**
1. 手动刷新页面
2. 使用 WebSocket 实时同步（已实现）
3. 调用 `useDictStoreHook().clearDictCache()`

**相关代码：**
- `frontend/src/store/modules/dict-store.ts`
- `frontend/src/composables/websocket/useDictSync.ts`

---

### 陷阱 9：组件自动导入

**问题描述：**
创建了新组件但无法使用，提示组件未定义。

**原因：**
Vite 的组件自动导入配置问题。

**解决方案：**
1. 检查组件是否在 `src/components/` 目录下
2. 检查组件命名是否符合规范（PascalCase）
3. 重启开发服务器

**配置文件：**
- `frontend/vite.config.ts` 中的 `Components` 配置

---

## 后端开发陷阱

### 陷阱 10：Django 和 FastAPI API 不一致

**问题描述：**
修改了 Django 后端的 API，但 FastAPI 后端没有同步修改，导致前端调用 FastAPI 时出错。

**预防措施：**
1. 修改 API 时，同时修改两个后端
2. 使用统一的 API 文档作为参考
3. 编写集成测试覆盖两个后端

**检查清单：**
- [ ] URL 路径一致
- [ ] 请求参数一致
- [ ] 响应格式一致
- [ ] 错误处理一致

---

### 陷阱 11：Redis 连接失败

**问题描述：**
启动后端时报 Redis 连接错误。

**解决方案：**
1. 检查 Redis 服务是否启动：`redis-cli ping`
2. 检查配置文件中的 Redis 地址
3. 如果不需要 Redis，系统会自动降级到内存缓存

**降级行为：**
- Django: 使用 `LocMemCache`
- FastAPI: 使用内存缓存
- WebSocket: 使用 `InMemoryChannelLayer`

---

### 陷阱 12：CORS 跨域问题

**问题描述：**
前端调用后端 API 时出现 CORS 错误。

**解决方案：**

**Django 配置：**
```python
# backend/drf_admin/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:9527',
    'http://127.0.0.1:9527',
]
CORS_ALLOW_CREDENTIALS = True
```

**FastAPI 配置：**
```python
# fastapi/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**前端代理配置：**
```typescript
// frontend/vite.config.ts
server: {
  proxy: {
    '/dev-api': {
      target: 'http://localhost:8769',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/dev-api/, ''),
    },
  },
}
```

---

## 环境配置陷阱

### 陷阱 13：环境变量未加载

**问题描述：**
配置了 `.env` 文件，但后端启动时没有读取到配置。

**解决方案：**

**Django：**
```bash
# 使用 --env 参数指定环境
uv run python manage.py runserver --env dev
```

**FastAPI：**
```bash
# 确保 .env 文件在 fastapi/ 目录下
cd fastapi
cp .env.example .env
```

---

### 陷阱 14：Python 版本不兼容

**问题描述：**
使用 Python 3.9 或更低版本运行项目时出错。

**要求：**
- Django 后端：Python >= 3.11
- FastAPI 后端：Python >= 3.10

**解决方案：**
使用 pyenv 管理多个 Python 版本：
```bash
pyenv install 3.11.0
pyenv local 3.11.0
```

---

### 陷阱 15：Windows 路径长度限制

**问题描述：**
在 Windows 上安装依赖时，提示路径过长错误。

**解决方案：**
1. 打开注册表编辑器
2. 导航到 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. 将 `LongPathsEnabled` 设置为 `1`
4. 重启电脑

---

## 性能陷阱

### 陷阱 16：大文件上传超时

**问题描述：**
上传大文件时，请求超时。

**解决方案：**
1. 调整前端超时配置
2. 调整后端请求体大小限制
3. 使用分片上传

**配置（已验证）：**
```python
# FastAPI: fastapi/app/core/config.py
max_upload_size: int = Field(default=10 * 1024 * 1024, alias="MAX_UPLOAD_SIZE")  # 10MB
```

```typescript
// 前端: frontend/src/utils/request.ts
timeout: 50000,  // 50秒
```

---

## 测试陷阱

### 陷阱 17：测试数据库未隔离

**问题描述：**
运行测试时，修改了开发数据库的数据。

**解决方案：**
Django 测试框架会自动使用测试数据库，确保：
1. 测试配置正确
2. 不要在测试中手动连接生产数据库

---

### 陷阱 18：异步测试未正确处理

**问题描述：**
FastAPI 异步测试报错。

**解决方案：**
```python
# 使用 pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

---

### 陷阱 19：不要硬编码 Playwright 默认端口

**问题描述：**
执行 `pnpm run test:e2e` 时，如果测试配置或脚本硬编码 Vite 默认端口，E2E 用例可能访问错误地址，导致登录页超时或页面元素找不到。

**已验证事实：**
- 前端开发端口来自 `frontend/.env.development` 的 `VITE_APP_PORT=9527`
- Playwright 配置当前通过 `frontend/playwright.config.ts` 读取 `VITE_APP_PORT` 并生成 `baseURL`

**解决方案：**
1. 运行 E2E 前先确认 `frontend/.env.development` 与 `frontend/playwright.config.ts` 使用同一端口来源
2. 禁止在新脚本中硬编码 `5173` 或其他默认端口
3. CI 与本地保持同一端口配置

---

### 陷阱 20：环境变量样例与 CI 动态 env 必须同步

**问题描述：**
当代码要求某个环境变量必须显式配置时，如果只更新 `.env.example` 或 `.env.test`，但忘记同步 `.github/workflows/quality-gates.yml` 中动态生成的测试环境文件，Django CI 会在读取 settings 阶段提前失败。

**已验证事实：**
- Django `DEFAULT_PWD` 当前通过 `backend/drf_admin/settings.py` 的 `env.str("DEFAULT_PWD")` 读取，不再回退到 `123456`
- 本地测试环境使用 `backend/.env.test`
- GitHub Actions 的 Django job 会重新生成 `backend/.env.test`，必须同步写入 `DEFAULT_PWD`

**解决方案：**
1. 新增必填环境变量时，同时检查 `backend/.env.example`、`backend/.env.test` 和 `.github/workflows/quality-gates.yml`
2. 对 settings 层新增回归测试，确保默认值不会退回弱口令或已弃用配置
3. 修改环境变量后至少运行 `cd backend && uv run pytest`，确认全量测试会收集到 settings 回归测试

---

### 陷阱 20.1：npm 审计专用 POST 超时不等于漏洞门禁结果

**问题描述：**
`pnpm audit --prod --json` 访问 npm advisory bulk 接口时，可能已经完成连接和请求体
上传，却在服务端迟迟没有返回响应。普通 registry GET 正常并不能证明这个 POST 接口
可用；pnpm 自身的重试也可能耗尽项目脚本的总超时预算。

**已验证事实：**
- `scripts/validate_dependency_audit.py` 默认对审计命令设置 120 秒总超时
- 空请求体和单包请求体均可复现 audit POST 超时，因此不能归因于项目依赖树大小
- 最近一次成功报告中的 high/critical 为 0，超时本身不是漏洞发现结果

**解决方案：**
1. 默认仍让网络超时使审计失败，避免把外部服务故障静默当成安全通过
2. 确需临时解除 PR 阻塞时，使用独立的限期网络例外配置；只允许明确的超时状态码被
   当前 PR workflow 转换为带警告的放行
3. 例外必须包含生效日、到期日、责任人、原因和追踪项；到期后自动恢复阻断
4. 生产发布前重新运行实时审计，不得使用网络例外替代发布门禁

---

## 部署陷阱

### 陷阱 21：静态文件 404

**问题描述：**
部署后访问静态文件（CSS、JS、图片）返回 404；或后端头像接口成功返回
`/media/...`，但浏览器错误地从前端 Vite 端口加载，导致图片破损。

**已验证事实：**
- Django/FastAPI 的资料与头像接口可能返回绝对 URL，也可能返回 `/media/...` 相对路径
- 前端通过 `resolveStaticAssetUrl` 使用 `VITE_APP_STATIC_URL` 解析相对路径，绝对 URL 保持不变
- 双后端真实 Playwright smoke 会校验上传后的头像 `naturalWidth > 0`，不仅检查接口成功或 `src` 文本

**解决方案：**
1. 执行前端构建：`pnpm run build`
2. 将 `dist/` 目录部署到 Nginx
3. 开发环境配置 `VITE_APP_STATIC_URL` 指向当前后端；生产同源部署时为 `/media/` 配置反向代理
4. 新增头像或文件展示入口时复用 `frontend/src/utils/static-asset-url.ts`，不要直接拼接后端地址

**Nginx 配置示例：**
```nginx
server {
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /prod-api/ {
        proxy_pass http://backend:8769/;
    }

    location /media/ {
        proxy_pass http://backend:8769/media/;
    }
}
```

---

## 快速排查清单

遇到问题时，按以下顺序排查：

1. [ ] 检查服务是否正常启动
2. [ ] 检查浏览器控制台错误
3. [ ] 检查网络请求（Network 面板）
4. [ ] 检查后端日志
5. [ ] 检查数据库连接
6. [ ] 检查 Redis 连接
7. [ ] 清除浏览器缓存和 localStorage
8. [ ] 重启开发服务器
9. [ ] 查阅本文档

---

**最后更新：** 2026-08-29
**维护者：** DV-Admin Team

**贡献指南：** 发现新陷阱时，请及时更新此文档。
