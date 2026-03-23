# 系统管理模块

> 本模块包含用户、角色、权限、部门、字典等核心管理功能。

---

## 模块概述

**位置：** `backend/drf_admin/apps/system/`

**功能：**
- 用户管理
- 角色管理
- 权限/菜单管理
- 部门管理
- 字典管理
- 通知公告
- 操作日志

---

## 目录结构

```
system/
├── models.py         # 数据模型定义
├── views/            # 视图层
│   ├── users.py      # 用户管理
│   ├── roles.py      # 角色管理
│   ├── menus.py      # 菜单/权限管理
│   ├── departments.py # 部门管理
│   ├── dicts.py      # 字典管理
│   ├── notices.py    # 通知公告
│   └── logs.py       # 操作日志
├── serializers/      # 序列化器
│   ├── users.py
│   ├── roles.py
│   ├── permissions.py
│   ├── departments.py
│   └── dicts.py
├── filters/          # 过滤器
│   └── users.py
├── urls.py           # 路由配置
└── tests.py          # 测试
```

---

## 数据模型

### Users (用户)

**表名：** `system_users`

**关键字段：**
- `username`: 用户名（唯一）
- `mobile`: 手机号（唯一）
- `roles`: 角色（多对多）
- `dept`: 部门（外键）

**重要方法：**
- `get_menus()`: 获取用户菜单树
- `get_user_info()`: 获取用户信息
- `_get_user_permissions()`: 获取用户权限列表

### Roles (角色)

**表名：** `system_roles`

**关键字段：**
- `name`: 角色名称（唯一）
- `code`: 角色编码
- `permissions`: 权限（多对多）
- `is_default`: 是否默认角色

### Permissions (权限)

**表名：** `system_permissions`

**权限类型：**
- `CATALOG`: 根目录
- `MENU`: 菜单
- `BUTTON`: 按钮
- `EXTLINK`: 外链

**关键字段：**
- `perm`: 权限标识（格式：`模块:资源:操作`）
- `route_name`: 路由名称
- `route_path`: 路由路径
- `parent`: 父权限（自关联）

### Departments (部门)

**表名：** `system_departments`

**特点：** 树形结构，通过 `parent` 自关联

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/system/users/` | GET, POST | 用户列表/创建 |
| `/api/v1/system/users/{id}/` | GET, PUT, DELETE | 用户详情/更新/删除 |
| `/api/v1/system/roles/` | GET, POST | 角色列表/创建 |
| `/api/v1/system/menus/` | GET, POST | 菜单列表/创建 |
| `/api/v1/system/depts/` | GET, POST | 部门树/创建 |
| `/api/v1/system/dicts/` | GET, POST | 字典类型列表/创建 |
| `/api/v1/system/dict-items/` | GET, POST | 字典项列表/创建 |
| `/api/v1/system/notices/` | GET, POST | 通知列表/创建 |
| `/api/v1/system/logs/` | GET | 日志列表 |

---

## 权限控制

### 权限验证流程

1. 请求到达 `RBACPermission` 中间件
2. 检查 URL 是否在白名单
3. 获取用户权限列表
4. 匹配权限标识
5. 允许/拒绝访问

### 权限白名单

在 `backend/drf_admin/settings.py` 中配置：

```python
WHITE_LIST = [
    '/api/v1/oauth/login/',
    '/api/v1/oauth/logout/',
    '/api/v1/oauth/info/',
    '/api/v1/oauth/menus/routes/',
    '/api/v1/system/users/profile/',
    '/api/v1/system/notices/my-page/',
    '/api/v1/system/dict-items/',
]
```

---

## 修改指南

### 新增管理功能

1. 在 `models.py` 添加模型（如需要）
2. 在 `serializers/` 创建序列化器
3. 在 `views/` 创建视图
4. 在 `urls.py` 注册路由
5. 运行迁移（如修改了模型）

### 修改权限逻辑

1. 阅读 `drf_admin/utils/permissions.py`
2. 理解 RBAC 权限模型
3. 修改后测试所有权限场景
4. 更新 `docs/ARCHITECTURE.md`

---

## 常见陷阱

### 陷阱 1：修改模型后未迁移

**解决：**
```bash
uv run python manage.py makemigrations system --env dev
uv run python manage.py migrate --env dev
```

### 陷阱 2：权限标识格式错误

**正确格式：** `system:user:add`
**错误格式：** `systemUserAdd`, `system:user_add`

### 陷阱 3：菜单树结构错误

**检查：**
- `parent` 关联是否正确
- `sort` 字段是否设置
- `type` 是否正确

---

## 测试

```bash
# 运行系统模块测试
cd backend
uv run pytest drf_admin/apps/system/tests.py -v

# 运行单个测试
uv run pytest drf_admin/apps/system/test_users.py -v
```

---

**最后更新：** 2026-03-23
