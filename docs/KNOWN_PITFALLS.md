# DV-Admin 已知陷阱和常见错误

> 本文档记录项目中已知的陷阱、常见错误及其解决方案。**遇到问题时请先查阅此文档。**

## 目的

沉淀已复现、可验证的工程陷阱，避免团队和代理重复踩坑。

## 适合读者

- 进行问题排查和回归验证的开发者
- 执行改动前需要风险预检的 AI 代理

## 一分钟摘要

- 命名转换、权限白名单、双后端契约差异是高频误读点。
- 本文档只记录有证据的坑点，不记录纯推测建议。
- 遇到文档与代码冲突时优先信任代码并回写本文档。

```yaml
ai_summary:
  authority: "已验证陷阱与排查路径"
  scope: "命名转换、迁移、认证权限、前后端联调、环境与部署常见误区"
  read_when:
    - "开始 bug 排查前"
    - "修改鉴权、路由、缓存、迁移相关逻辑前"
  verify_with:
    - "backend/drf_admin/settings.py"
    - "backend/drf_admin/utils/middleware.py"
    - "backend/drf_admin/utils/permissions.py"
    - "frontend/src/store/modules/permission-store.ts"
    - "frontend/src/store/modules/dict-store.ts"
    - "frontend/vite.config.ts"
  stale_when:
    - "中间件、权限、缓存或启动流程变化"
    - "已记录陷阱被彻底消除且验证通过"
```

## 权威边界

- 本文件负责“已知问题与排查手册”，不替代架构设计或接口清单。
- 新陷阱需要给出可追踪证据后再纳入。

## 如何验证

- 每条陷阱至少可映射到对应代码路径、配置项或可执行命令。
- 排查步骤可在本地通过命令或最小复现路径复核。

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

## 认证授权陷阱

### 陷阱 5：Token 过期处理

**问题描述：**
前端收到 401 错误后，没有正确刷新 Token，导致用户被强制登出。

**正确处理流程：**
1. 收到 401 错误
2. 检查是否有 Refresh Token
3. 使用 Refresh Token 获取新的 Access Token
4. 重试原请求
5. 如果刷新失败，跳转登录页

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

### 陷阱 19：Playwright 默认端口与 Vite 开发端口不一致

**问题描述：**
执行 `pnpm run test:e2e` 时，E2E 用例访问的地址与本地前端实际端口不一致，导致登录页超时或页面元素找不到。

**已验证事实：**
- 前端开发端口来自 `frontend/.env.development` 的 `VITE_APP_PORT=9527`
- Playwright 配置当前使用 `http://localhost:5173`（`frontend/playwright.config.ts`）

**解决方案：**
1. 运行 E2E 前先统一端口策略（修改 Playwright 配置或启动端口）
2. 将端口约定同步到团队文档，避免环境漂移
3. CI 与本地保持同一端口配置

---

## 部署陷阱

### 陷阱 20：静态文件 404

**问题描述：**
部署后访问静态文件（CSS、JS、图片）返回 404。

**解决方案：**
1. 执行前端构建：`pnpm run build`
2. 将 `dist/` 目录部署到 Nginx
3. 配置 Nginx 静态文件路径

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

**最后更新：** 2026-04-09
**维护者：** DV-Admin Team

**贡献指南：** 发现新陷阱时，请及时更新此文档。
