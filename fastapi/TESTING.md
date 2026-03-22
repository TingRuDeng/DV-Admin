# FastAPI 后端单元测试

## 概述

本文档介绍 FastAPI 后端的单元测试配置和使用方法。

## 技术栈

- 测试框架: pytest
- HTTP 客户端: httpx
- 数据库: SQLite 内存数据库 (Tortoise ORM)
- 认证: JWT Token

## 测试结果

```
475 tests passed
覆盖率: 80.12%
```

## 目录结构

```
fastapi/
├── tests/
│   ├── conftest.py              # 测试配置和 fixtures
│   ├── test_oauth.py            # OAuth 认证测试
│   ├── test_users.py            # 用户管理测试
│   ├── test_roles.py            # 角色管理测试
│   ├── test_menus.py            # 菜单管理测试
│   ├── test_depts.py            # 部门管理测试
│   ├── test_dicts.py            # 字典管理测试
│   ├── test_dict_items.py       # 字典项测试
│   ├── test_notices.py          # 通知公告测试
│   ├── test_profile.py          # 个人中心测试
│   ├── test_files.py            # 文件上传测试
│   ├── test_captcha.py          # 验证码测试
│   ├── test_health.py           # 健康检查测试
│   ├── test_cache.py            # 缓存服务测试
│   ├── test_redis.py            # Redis 连接测试
│   ├── test_token_blacklist.py  # Token 黑名单测试
│   ├── test_security.py         # 安全模块测试
│   ├── test_security_validator.py # 安全验证器测试
│   ├── test_config.py           # 配置测试
│   ├── test_exceptions.py       # 异常测试
│   ├── test_user_service.py     # 用户服务测试
│   ├── test_role_service.py     # 角色服务测试
│   ├── test_dict_service.py     # 字典服务测试
│   ├── test_log_service.py      # 日志服务测试
│   └── test_notice_service.py   # 通知服务测试
```

## 测试 Fixture

| Fixture | 说明 |
|---------|------|
| `client` | TestClient 实例 |
| `test_user` | 普通测试用户 |
| `test_user_with_role` | 带角色的测试用户 |
| `test_role` | 测试角色 |
| `test_permissions` | 测试权限/菜单 |
| `test_dept` | 测试部门 |
| `auth_headers` | 认证请求头 |
| `auth_client` | 带认证的客户端 |

### Fixture 详情

#### test_user_with_role

创建带完整权限的测试用户：

```python
# 包含的权限
- system:users:query, add, edit, delete
- system:roles:query, add, edit, delete
- system:menus:query, add, edit, delete
- system:departments:query, add, edit, delete
- system:dicts:query, add, edit, delete
- system:notices:query, add, edit, delete, publish, revoke
- system:files:query
- system:logs:query, delete
```

## 运行测试

### 运行所有测试

```bash
cd fastapi
uv run pytest tests/ -v
```

### 运行单个测试文件

```bash
uv run pytest tests/test_oauth.py -v
```

### 运行单个测试用例

```bash
uv run pytest tests/test_oauth.py::TestOAuthLogin::test_login_success -v
```

### 显示详细输出

```bash
uv run pytest tests/ -v -s
```

### 生成覆盖率报告

```bash
# 终端输出
uv run pytest --cov=app --cov-report=term-missing

# HTML 报告
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 测试覆盖

### 模块覆盖率

| 模块 | 覆盖率 | 测试用例 |
|------|--------|----------|
| app/api/v1/system/logs.py | 100% | 14 |
| app/services/system/log_service.py | 99% | 42 |
| app/services/system/dict_service.py | 96% | 45 |
| app/services/system/role_service.py | 95% | 28 |
| app/services/system/notice_service.py | 95% | 25 |
| app/core/security.py | 93% | 15 |
| app/core/cache.py | 97% | 44 |
| app/core/redis.py | 100% | 14 |
| app/services/token_blacklist.py | 100% | 22 |
| app/core/security_validator.py | 98% | 28 |

### 功能测试覆盖

| 模块 | 测试用例 |
|------|----------|
| OAuth 认证 | 登录成功、登录失败、验证码、用户信息、菜单路由、登出、Token 刷新 |
| 用户管理 | 列表、创建、更新、删除、重置密码、导入、导出 |
| 角色管理 | 列表、创建、更新、删除、权限分配 |
| 菜单管理 | 列表、详情、创建、更新、删除、权限标识、下拉选项 |
| 部门管理 | 列表、创建、更新、删除 |
| 字典管理 | 列表、详情、创建、更新 |
| 字典项 | 列表、创建、更新、删除 |
| 通知公告 | 列表、创建、更新、发布、撤销、我的公告、表单 |
| 个人中心 | 获取信息、更新信息、修改密码、修改头像 |
| 文件管理 | 上传文件、删除文件 |
| 操作日志 | 分页列表、访问统计、访问趋势、删除日志 |
| 健康检查 | 基本检查、就绪检查、存活检查 |
| 缓存服务 | 内存缓存、Redis 缓存、TTL、模式删除 |
| Token 黑名单 | 单个撤销、批量撤销、黑名单检查 |

## 添加新测试

### 创建测试文件

```python
# tests/test_example.py
# -*- coding: utf-8 -*-
"""
模块名称测试
"""
import pytest
from fastapi.testclient import TestClient


class TestExample:
    """示例测试"""

    def test_example(self, auth_client: TestClient):
        """测试示例"""
        response = auth_client.get("/api/v1/example/")
        assert response.status_code == 200
```

### 使用 Fixture

```python
def test_with_user(client: TestClient, test_user):
    """使用测试用户"""
    response = client.post("/api/v1/login/", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200


def test_with_auth(auth_client: TestClient):
    """使用认证客户端"""
    response = auth_client.get("/api/v1/protected/")
    assert response.status_code == 200
```

### 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """异步测试示例"""
    result = await some_async_function()
    assert result is not None
```

## 测试最佳实践

1. **使用唯一的测试数据**: 使用 UUID 确保测试数据唯一
2. **清理测试数据**: 每个测试后清理数据库
3. **测试独立性**: 每个测试应该独立运行
4. **清晰的测试命名**: 使用描述性的测试名称
5. **合理的断言**: 断言应该清晰表达预期行为
6. **Mock 外部依赖**: 使用 Mock 隔离外部服务

## 常见问题

### 1. 数据库连接问题

**问题**: 测试失败提示数据库连接错误

**解决**: 确保 SQLite 内存数据库配置正确

```python
# conftest.py
@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.db.models.oauth", "app.db.models.system"]},
    )
    await Tortoise.generate_schemas()
```

### 2. 权限测试失败

**问题**: 返回 403 Forbidden

**解决**: 使用 `auth_client` fixture 确保已认证

### 3. 响应格式问题

**问题**: 断言响应数据失败

**解决**: FastAPI 使用标准 JSON 响应

```python
# 成功响应
assert response.status_code == 200
data = response.json()
assert data.get("code") == 20000

# 失败响应
assert response.status_code in [200, 401]
```

### 4. Redis 连接问题

**问题**: Redis 相关测试失败

**解决**: 测试环境使用内存缓存替代

```python
# 测试时自动降级为内存缓存
from app.core.cache import cache

# 测试前确保使用内存模式
cache._use_redis = False
```

### 5. 事件循环问题

**问题**: Tortoise ORM 事件循环绑定错误

**解决**: 使用 pytest-asyncio 的 auto 模式

```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4
```

## 测试报告

运行测试后会生成以下报告：

- **终端输出**: 测试结果和覆盖率摘要
- **HTML 报告**: `htmlcov/index.html` - 详细的覆盖率报告
- **XML 报告**: `coverage.xml` - CI 集成使用
