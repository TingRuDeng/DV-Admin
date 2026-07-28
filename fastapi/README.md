# DV-Admin FastAPI Backend

基于 FastAPI + Tortoise ORM 的异步后端服务。`fastapi/` 是项目的 FastAPI 后端实现，对应的替代实现见 `backend/`（Django）。两者面向同一套前端和业务域，日常开发/部署通常二选一，并保持共享 API 契约兼容。

## 技术栈

- **框架**: FastAPI (异步)
- **ORM**: Tortoise ORM (异步友好)
- **认证**: JWT (python-jose + passlib)
- **数据库**: SQLite (默认) / MySQL (可选)
- **缓存**: Redis (可选，支持内存缓存降级)
- **部署**: Docker
- **依赖管理**: uv

## 项目结构

```
fastapi/
├── app/
│   ├── api/              # API 路由
│   │   ├── v1/
│   │   │   ├── system/   # 系统管理模块
│   │   │   ├── oauth/    # 认证模块
│   │   │   ├── information/  # 个人中心模块
│   │   │   └── files/    # 文件管理模块
│   │   ├── deps.py       # 依赖注入
│   │   └── health.py     # 健康检查端点
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   ├── security.py   # 安全模块
│   │   ├── security_validator.py  # 安全验证器
│   │   ├── cache.py      # 缓存服务
│   │   ├── redis.py      # Redis 连接管理
│   │   └── exceptions.py # 异常定义
│   ├── db/               # 数据库模型、迁移配置与版本化迁移
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 业务服务层
│   │   ├── captcha_service.py      # 验证码服务
│   │   ├── token_blacklist.py      # Token 黑名单
│   │   └── system/       # 系统模块服务
│   ├── middleware/       # 中间件
│   │   ├── logging_middleware.py   # 请求日志
│   │   └── slow_query_middleware.py # 慢查询监控
│   ├── utils/            # 工具函数
│   │   └── logger.py     # 结构化日志
│   └── main.py           # 应用入口
├── scripts/              # 脚本文件
│   └── dev.sh            # 开发环境启动脚本
├── tests/                # 测试（490+ 测试用例）
├── uploads/              # 上传文件目录
├── pyproject.toml        # 依赖管理 (uv)
├── .env.example          # 环境变量示例
├── README.md             # 项目说明
└── TESTING.md            # 测试文档
```

## 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 创建虚拟环境并安装依赖

```bash
cd fastapi

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux

# 安装依赖
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

### 4. 运行开发服务器

```bash
# 方式一：使用启动脚本（推荐）
./scripts/dev.sh

# 方式二：使用 uv run
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8769

# 方式三：使用 Python
uv run python app/main.py
```

### 5. 使用 Docker 运行

```bash
cd docker
export DATABASE_URL='mysql://root:<strong-password>@db:3306/dv_admin'
export MYSQL_ROOT_PASSWORD='<strong-password>'
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DEFAULT_PASSWORD='<strong-initial-password>'
docker compose up -d
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8769/api/swagger/
- **ReDoc**: http://localhost:8769/api/redoc/

## 主要功能

### 认证授权

- [x] JWT Token 认证
- [x] 登录/登出
- [x] Token 刷新
- [x] Token 黑名单（Redis 支持）
- [x] 权限检查
- [x] 角色检查
- [x] 验证码验证

### 系统管理

- [x] 用户管理（CRUD、分页、搜索、导入导出）
- [x] 角色管理（CRUD、权限分配）
- [x] 部门管理（树形结构）
- [x] 菜单/权限管理（树形结构）
- [x] 字典管理（类型+字典项）
- [x] 操作日志（访问统计、趋势分析）

### 个人中心

- [x] 个人信息查询/修改
- [x] 密码修改
- [x] 头像上传

### 文件管理

- [x] 文件上传
- [x] 文件删除

### 运维监控

- [x] 健康检查端点（/health, /health/ready, /health/live）
- [x] 请求日志中间件
- [x] 慢查询监控
- [x] 结构化 JSON 日志

## API 兼容性

FastAPI 后端保持与原有 Django 前端 API 接口完全兼容：

- **URL 路径**: 与 Django 版本保持一致
- **请求参数**: 支持相同的查询参数和请求体
- **响应格式**: 统一的 `{code, message, data}` 格式
- **分页格式**: 与 Django 版本保持一致

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_ENV` | 应用环境 | `development` |
| `DATABASE_URL` | 数据库连接 URL | `sqlite://./dv_admin.db` |
| `REDIS_URL` | Redis 连接 URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT 密钥（生产环境必填） | 开发环境自动生成 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间（分钟） | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌过期时间（天） | `7` |
| `DEFAULT_PASSWORD` | 新增、导入和重置用户时使用的默认密码 | `Admin@123456` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FORMAT` | 日志格式（json/text） | `json` |
| `SLOW_QUERY_THRESHOLD_MS` | 慢查询阈值（毫秒） | `1000` |
| `CACHE_TTL` | 缓存过期时间（秒） | `300` |
| `MAX_UPLOAD_SIZE` | 通用上传和用户 Excel 导入的文件上限（字节） | `10485760` |

### 安全配置

生产环境必须设置以下配置：

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_urlsafe(64))"

# .env 配置
APP_ENV=production
# 必须粘贴上面命令生成的随机值，不要使用示例占位文本
SECRET_KEY=<paste-generated-random-value-here>
DEBUG=false
DEFAULT_PASSWORD=YourStrongPassword@123
```

## 开发指南

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 异步函数使用 `async/await`

### 添加新 API

1. 在 `app/schemas/` 下定义 Pydantic 模型
2. 在 `app/api/v1/` 下创建路由文件
3. 在 `app/api/v1/__init__.py` 中注册路由

### 缓存使用

```python
from app.core.cache import cache, CacheKeys

# 获取或设置缓存
data = await cache.get_or_set(
    CacheKeys.dict_code("status"),
    lambda: get_dict_data("status"),
    ttl=600  # 10分钟
)

# 删除缓存
await cache.delete(CacheKeys.dict_code("status"))
```

## 测试

```bash
# 运行聚合质量检查 (ruff + mypy + migration-check + pytest + coverage)
make quality

# 单独校验 SQLite 空库、0001→最新版本增量升级、既有库接管和模型漂移
make migration-check

# 运行特定测试
uv run pytest tests/test_oauth.py -v

# 运行测试并生成覆盖率报告
uv run pytest --cov=app --cov-report=html
```

测试覆盖率: **80%+**

## 数据库迁移

```bash
# 生成模型变更迁移
uv run python -m tortoise \
  -c app.db.migration_config.TORTOISE_ORM \
  makemigrations models

# 执行迁移
uv run python -m tortoise \
  -c app.db.migration_config.TORTOISE_ORM \
  migrate
```

全新数据库直接执行 `migrate`。既有 FastAPI 数据库首次接管 `0001_initial` 基线前，必须先备份并核对 schema；确认一致后仅执行一次 `migrate --fake`。开发启动中的自动建表只用于本地开发，不能替代生产迁移。

合并前的迁移门禁会在 SQLite 上验证空库安装和带既有操作日志数据的
`0001_initial → 0002_auto_20260725_2230` 增量升级；CI 还会在两个隔离的
MySQL 8 数据库上分别执行空库与增量升级验证。

## 部署

### Docker 部署

```bash
cd docker
export DATABASE_URL='mysql://root:<strong-password>@db:3306/dv_admin'
export MYSQL_ROOT_PASSWORD='<strong-password>'
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DEFAULT_PASSWORD='<strong-initial-password>'
docker compose up -d
```

Compose 会先运行一次性 `migrate` 服务；只有迁移成功后 API 才启动。不要把
迁移命令放进 Uvicorn Worker 的启动入口，否则多副本会并发修改 schema。生产
Compose 不提供弱凭据默认值，也不挂载宿主源码或启用 `--reload`；缺少上述必填
环境变量时会在解析 Compose 阶段失败。

独立镜像或其他编排平台必须在发布 API 前运行单例迁移 Job，例如：

```bash
python -m tortoise \
  -c app.db.migration_config.TORTOISE_ORM \
  migrate
```

迁移失败时必须阻断 API rollout，并继续保留旧版本 API；镜像回滚不会自动恢复
数据库 schema。

### 生产环境配置

1. 修改 `.env` 文件中的配置
2. 设置 `APP_ENV=production`
3. 使用强密码的 `SECRET_KEY`（必须设置）
4. 显式配置安全的 `DEFAULT_PASSWORD`
5. 配置正确的数据库和 Redis 连接
6. 通过单例迁移 Job 执行待应用的 Tortoise ORM 迁移，成功后再发布 API
7. 配置日志文件路径

FastAPI 当前以 `use_tz=false` 保存本地时间；非 Docker 部署必须保证进程系统时区
为 `Asia/Shanghai`，否则跨午夜的通知和访问趋势日期会与 Django 口径偏移。

### 健康检查

```bash
# 基本健康检查
curl http://localhost:8769/health

# 就绪检查（含数据库、Redis）
curl http://localhost:8769/health/ready

# 存活检查
curl http://localhost:8769/health/live
```

## 性能优化

### 数据库索引

已为常用查询字段添加索引：
- 用户表: username, mobile, email, is_active
- 角色表: code, status
- 权限表: type, route_name, visible
- 日志表: user_id, status, created_at

### 缓存策略

| 数据类型 | 缓存时间 | 缓存清除时机 |
|---------|---------|-------------|
| 字典项 | 10分钟 | 字典/字典项增删改 |
| 角色选项 | 10分钟 | 角色增删改 |
| 用户权限 | 10分钟 | 用户角色变更 |

## 与 Django 版本对比

| 特性 | Django + DRF | FastAPI |
|------|-------------|---------|
| 性能 | 同步 | 异步 |
| 自动文档 | 需配置 | 自动生成 |
| 类型检查 | 运行时 | 编译时 |
| 依赖注入 | 有限 | 强大 |
| 测试覆盖率 | - | 80%+ |
| 缓存支持 | 需配置 | 内置 |
| 监控日志 | 需配置 | 内置 |

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
