# Django 后端单元测试

## 概述

本文档介绍 Django 后端的单元测试配置和使用方法。

## 技术栈

- 测试框架: Django TestCase
- HTTP 客户端: DRF APIClient
- 数据库: SQLite 内存数据库
- 认证: JWT Token + Session

## 测试结果

```
28 tests passed
```

## 目录结构

```
backend/drf_admin/
├── settings_test.py              # 测试配置
└── apps/
    ├── oauth/
    │   └── tests.py              # OAuth 认证测试 (6 tests)
    ├── system/
    │   ├── tests.py              # 用户管理测试 (8 tests)
    │   ├── test_roles.py         # 角色管理测试 (9 tests)
    │   └── test_departments.py   # 部门管理测试 (5 tests)
    └── information/
        └── tests.py              # 个人中心测试 (4 tests)
```

## 测试配置

`settings_test.py` 包含以下配置：

```python
# 使用 SQLite 内存数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 关闭调试模式
DEBUG = False

# 简化权限检查
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]

# 简化密码哈希（加快测试速度）
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
```

## 运行测试

### 运行所有测试

```bash
cd backend
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test
```

### 运行单个测试模块

```bash
# OAuth 认证测试
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.oauth.tests

# 用户管理测试
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.system.tests

# 角色管理测试
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.system.test_roles

# 部门管理测试
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.system.test_departments

# 个人中心测试
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.information.tests
```

### 运行特定测试类

```bash
DJANGO_SETTINGS_MODULE=drf_admin.settings_test uv run python manage.py test drf_admin.apps.oauth.tests.OAuthLoginTestCase
```

## 创建带权限的测试用户

Django 后端使用 RBAC 权限系统，测试时需要创建带权限的用户：

```python
def create_admin_user():
    """创建带管理员角色的测试用户"""
    # 创建角色
    role, _ = Roles.objects.get_or_create(
        name="超级管理员",
        code="admin",
        defaults={"status": 1, "sort": 1}
    )
    
    # 创建权限
    perm_codes = [
        "system:users:query", "system:users:add", "system:users:edit", "system:users:delete",
        "system:roles:query", "system:roles:add", "system:roles:edit", "system:roles:delete",
        "system:departments:query", "system:departments:add", "system:departments:edit", "system:departments:delete",
    ]
    
    perms = []
    for code in perm_codes:
        perm, _ = Permissions.objects.get_or_create(
            perm=code,
            defaults={"name": code, "type": "BUTTON"}
        )
        perms.append(perm)
    
    # 关联权限
    role.permissions.add(*perms)
    
    # 创建用户并关联角色
    user = Users.objects.create_user(
        username="admin",
        password="admin123",
        name="管理员",
        is_active=1
    )
    user.roles.add(role)
    
    return user
```

## 测试覆盖

| 模块 | 测试用例 |
|------|----------|
| OAuth 认证 | 登录成功、登录失败（密码错误）、登录失败（缺少字段）、用户信息、菜单路由、登出 |
| 用户管理 | 列表、创建、更新、删除、重置密码、用户下拉选项 |
| 角色管理 | 列表、创建、更新、删除、菜单ID、角色下拉选项 |
| 部门管理 | 列表、创建、更新 |
| 个人中心 | 获取信息 |

## 添加新测试

### 创建测试文件

```python
# apps/system/test_example.py
# -*- coding: utf-8 -*-
"""
模块名称测试
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from drf_admin.apps.system.models import Users, Roles


def create_admin_user():
    """创建带权限的测试用户"""
    role, _ = Roles.objects.get_or_create(
        name="管理员",
        code="admin",
        defaults={"status": 1}
    )
    
    user = Users.objects.create_user(
        username="admin",
        password="admin123",
        name="管理员",
        is_active=1
    )
    user.roles.add(role)
    return user


class ExampleTestCase(TestCase):
    """示例测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_example_list(self):
        """测试获取列表"""
        response = self.client.get("/api/v1/example/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_example_create(self):
        """测试创建"""
        response = self.client.post("/api/v1/example/", {
            "name": "测试"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

### 使用 Session 认证

```python
def test_with_auth(self):
    """使用认证客户端"""
    self.client.force_authenticate(user=self.user)
    response = self.client.get("/api/v1/protected/")
    self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## 常见问题

### 1. 导入错误

**问题**: `ModuleNotFoundError: No module named 'apps'`

**解决**: 使用完整的模块路径

```python
# 错误
from apps.system.models import Users

# 正确
from drf_admin.apps.system.models import Users
```

### 2. 权限测试失败

**问题**: 返回 403 Forbidden

**解决**: 使用 `create_admin_user()` 创建带权限的用户，或在 setUp 中调用 `self.client.force_authenticate(user=self.user)`

### 3. 响应格式问题

**问题**: 断言响应数据失败

**解决**: Django REST Framework 使用驼峰响应格式

```python
# 成功响应
assert response.status_code == status.HTTP_200_OK
assert response.data["code"] == 20000

# 列表响应
assert response.data["data"]["results"]  # 分页数据
```

### 4. API 路径问题

**问题**: 404 Not Found

**解决**: 确认正确的 API 路径（包含版本号）

```python
# 检查 urls.py 中的 BASE_API 配置
# 通常格式为 /api/v1/
response = self.client.get("/api/v1/system/users/")
```

## 测试最佳实践

1. **使用 get_or_create**: 避免重复创建数据
2. **创建辅助函数**: 如 `create_admin_user()` 复用创建逻辑
3. **force_authenticate**: 简化认证流程
4. **灵活的断言**: 允许合理的 HTTP 状态码范围
5. **清理数据**: Django TestCase 自动清理数据库

## API 响应格式

Django 后端使用统一响应格式：

```json
{
    "msg": "成功",
    "errors": "",
    "code": 20000,
    "data": {}
}
```

断言示例：

```python
# 检查响应成功
assert response.status_code == status.HTTP_200_OK
assert response.data["code"] == 20000

# 检查分页数据
assert "results" in response.data["data"]
```
