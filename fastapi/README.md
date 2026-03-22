# DV-Admin FastAPI Backend

基于 FastAPI + Tortoise ORM 的异步后端服务，兼容原有 Django 前端 API 接口。

## 技术栈

- **框架**: FastAPI (异步)
- **ORM**: Tortoise ORM (异步友好)
- **认证**: JWT (python-jose + passlib)
- **数据库**: SQLite (默认) / MySQL (可选)
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
│   │   └── deps.py       # 依赖注入
│   ├── core/             # 核心配置
│   ├── db/               # 数据库模型
│   ├── schemas/          # Pydantic 模型
│   ├── utils/            # 工具函数
│   └── main.py           # 应用入口
├── scripts/              # 脚本文件
│   └── dev.sh            # 开发环境启动脚本
├── tests/                # 测试
├── uploads/              # 上传文件目录
├── pyproject.toml        # 依赖管理 (uv)
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
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
docker-compose up -d
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
- [x] 权限检查
- [x] 角色检查

### 系统管理

- [x] 用户管理（CRUD、分页、搜索）
- [x] 角色管理（CRUD、权限分配）
- [x] 部门管理（树形结构）
- [x] 菜单/权限管理（树形结构）
- [x] 字典管理（类型+字典项）

### 个人中心

- [x] 个人信息查询/修改
- [x] 密码修改
- [x] 头像上传

### 文件管理

- [x] 文件上传
- [x] 文件删除

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
| `SECRET_KEY` | JWT 密钥 | `your-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间（分钟） | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌过期时间（天） | `7` |

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

## 测试

```bash
# 运行测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=app --cov-report=html
```

## 部署

### Docker 部署

```bash
cd docker
docker-compose up -d
```

### 生产环境配置

1. 修改 `.env` 文件中的配置
2. 设置 `APP_ENV=production`
3. 使用强密码的 `SECRET_KEY`
4. 配置正确的数据库和 Redis 连接

## 与 Django 版本对比

| 特性 | Django + DRF | FastAPI |
|------|-------------|---------|
| 性能 | 同步 | 异步 |
| 自动文档 | 需配置 | 自动生成 |
| 类型检查 | 运行时 | 编译时 |
| 依赖注入 | 有限 | 强大 |
| 学习曲线 | 平缓 | 中等 |

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
