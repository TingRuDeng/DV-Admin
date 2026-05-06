# DV-Admin 数据库模型文档

> 本文档记录数据库模型结构。代码是真理之源，此文档仅供参考。

## 目的

汇总 Django/FastAPI 两套实现下的核心数据模型、命名差异和迁移约束，降低接口与模型联动修改时的误判风险。

## 适合读者

- 进行模型变更、迁移或数据排查的后端开发者
- 需要核对字段与索引事实的 AI 代理与审查者

## 一分钟摘要

- 开发环境默认可使用 SQLite，生产推荐 MySQL；两者行为不能简单等同。
- Django 与 FastAPI 模型存在局部命名差异（如字典相关表），属于已知兼容成本。
- 文档列出核心模型与关系，但不是 ORM 字段的逐行替代。
- 迁移命令以对应后端工程内实际命令为准。

```yaml
ai_summary:
  authority: "核心数据模型、关系与迁移约束说明"
  scope: "Django/FastAPI 核心模型、命名差异、索引与迁移入口"
  read_when:
    - "修改模型或序列化 schema 前"
    - "排查字段不一致或迁移冲突时"
  verify_with:
    - "backend/drf_admin/apps/system/models.py"
    - "backend/drf_admin/apps/oauth/models.py"
    - "fastapi/app/db/models/system.py"
    - "fastapi/app/db/models/oauth.py"
    - "backend/dev.sh"
    - "fastapi/scripts/dev.sh"
  stale_when:
    - "模型字段或表名变化"
    - "迁移策略变化"
    - "开发/生产数据库策略变化"
```

## 权威边界

- 本文件是模型概览与差异说明，不替代 ORM 源码与迁移文件。
- 与模型代码冲突时以模型定义和迁移历史为准。

## 如何验证

- Django 模型：`backend/drf_admin/apps/system/models.py`、`backend/drf_admin/apps/oauth/models.py`。
- FastAPI 模型：`fastapi/app/db/models/system.py`、`fastapi/app/db/models/oauth.py`。
- 迁移入口：Django `manage.py makemigrations/migrate`，FastAPI `uvicorn + generate_schemas` 与生产迁移流程。

---

## 数据库配置

**支持的数据库：**
- SQLite（开发环境默认）
- MySQL 8.0+（生产环境推荐）

**开发环境说明：**
- 当前仓库本地 Django 开发库默认文件为 [backend/drf_admin/db.sqlite3](/Users/dengtingru/Desktop/code/DV-Admin/backend/drf_admin/db.sqlite3)
- 代理/调试场景下可通过 SQLite MCP 直接连接该文件查看本地数据
- 这类 MCP 访问仅代表本地开发环境，不代表生产数据库类型、数据规模或 SQL 行为

**ORM：**
- Django：Django ORM
- FastAPI：Tortoise ORM

---

## 核心模型

### 用户模型 (Users)

**表名：** `system_users`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| username | varchar(150) | 用户名 | Unique, Not Null |
| password | varchar(128) | 密码（加密） | Not Null |
| name | varchar(20) | 真实姓名 | |
| mobile | varchar(11) | 手机号 | Unique |
| email | varchar(254) | 邮箱 | |
| image | varchar(100) | 头像路径 | Default: 'avatar/default.png' |
| gender | int | 性别 | 0:保密, 1:男, 2:女 |
| is_active | int | 是否激活 | 0:禁用, 1:启用 |
| is_staff | boolean | 是否员工 | |
| is_superuser | boolean | 是否超级管理员 | |
| dept_id | int | 部门ID | FK → Departments |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `username` (Unique)
- `mobile` (Unique)
- `is_active`

**关系：**
- `roles`: Many-to-Many → Roles (through: `system_users_to_system_roles`)
- `dept`: Foreign Key → Departments

---

### 角色模型 (Roles)

**表名：** `system_roles`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| name | varchar(32) | 角色名称 | Unique, Not Null |
| code | varchar(32) | 角色编码 | |
| status | int | 状态 | 0:禁用, 1:启用 |
| sort | int | 排序 | Default: 0 |
| is_default | int | 是否默认角色 | 0:否, 1:是 |
| desc | varchar(50) | 描述 | |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `name` (Unique)
- `code`
- `status`
- `is_default`

**关系：**
- `permissions`: Many-to-Many → Permissions
- `users`: Many-to-Many → Users

---

### 权限模型 (Permissions)

**表名：** `system_permissions`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| name | varchar(30) | 名称 | Not Null |
| type | varchar(8) | 权限类型 | CATALOG/MENU/BUTTON/EXTLINK |
| route_name | varchar(30) | 路由名 | |
| route_path | varchar(200) | 路由路径 | |
| component | varchar(200) | 组件路径 | |
| sort | int | 排序 | Default: 0 |
| visible | int | 是否可见 | 0:否, 1:是 |
| icon | varchar(30) | 图标 | |
| redirect | varchar(200) | 重定向 | |
| perm | varchar(200) | 权限标识 | |
| keep_alive | boolean | 是否缓存 | |
| always_show | boolean | 是否一直显示 | |
| params | json | 参数 | Default: [] |
| desc | varchar(30) | 描述 | |
| parent_id | int | 父菜单ID | FK → Permissions |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `type`
- `route_name`
- `visible`
- `(parent_id, sort)`

**关系：**
- `parent`: Self-Reference (树形结构)
- `children`: Self-Reference (反向)
- `roles`: Many-to-Many → Roles

---

### 部门模型 (Departments)

**表名：** `system_departments`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| name | varchar(32) | 部门名称 | Not Null |
| status | int | 状态 | 0:禁用, 1:启用 |
| sort | int | 排序 | Default: 0 |
| parent_id | int | 父部门ID | FK → Departments |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `status`
- `(parent_id, sort)`

**关系：**
- `parent`: Self-Reference (树形结构)
- `children`: Self-Reference (反向)
- `users`: One-to-Many → Users

---

### 字典类型模型 (Dicts / DictData)

**Django 表名：** `system_dicts`
**FastAPI 表名：** `system_dict_data`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| name | varchar(32/50) | 字典名称 | Unique |
| dict_code / code | varchar(32/50) | 字典编码 | Unique |
| status | int | 状态 | 0:禁用, 1:启用 |
| remark / desc | varchar(50/100) | 备注/描述 | |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `name` (Unique)
- `dict_code` / `code` (Unique)
- `status`

---

### 字典项模型 (DictItems)

**表名：** `system_dict_items`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| label | varchar(32/50) | 标签 | Not Null |
| value | varchar(32/50) | 值 | Not Null |
| sort | int | 排序 | Default: 0 |
| status | int | 状态 | 0:禁用, 1:启用 |
| tag_type | varchar(32) | 标签类型 | |
| is_default | boolean | 是否默认 | FastAPI only |
| remark | varchar(100) | 备注 | FastAPI only |
| dict_id / dict_data_id | int | 字典ID | FK → Dicts/DictData |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `status`
- `(dict_id, sort)` / `(dict_data_id, sort)`
- `(dict_id, status)` / `(dict_data_id, status)`

---

### 通知公告模型 (Notices)

**表名：** `system_notices`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| title | varchar(200) | 标题 | Not Null |
| content | text | 内容 | Not Null |
| type | int | 类型 | |
| level | varchar(10) | 级别 | Default: 'L' |
| target_type | int | 目标类型 | 1:全体, 2:指定 |
| target_user_ids | json | 目标用户ID列表 | Default: [] |
| publisher_id | int | 发布人ID | |
| publisher_name | varchar(50) | 发布人名称 | |
| publish_status | int | 发布状态 | 0:未发布, 1:已发布, -1:已撤回 |
| publish_time | datetime | 发布时间 | |
| revoke_time | datetime | 撤回时间 | |
| created_at | datetime | 创建时间 | |
| updated_at | datetime | 更新时间 | |

**索引：**
- `publish_status`
- `publisher_id`
- `(publish_status, publish_time)`

---

### 通知已读记录 (NoticeReads)

**表名：** `system_notice_reads`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| notice_id | int | 通知ID | FK → Notices |
| user_id | int | 用户ID | Not Null |
| read_time | datetime | 已读时间 | Auto |
| created_at | datetime | 创建时间 | |

**约束：**
- `UNIQUE(notice_id, user_id)`

**索引：**
- `user_id`

---

### 操作日志模型 (OperationLog)

**表名：** `system_operation_log`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 主键 | PK, Auto |
| user_id | int | 用户ID | |
| username | varchar(150) | 用户名 | |
| name | varchar(50) | 用户姓名 | |
| operation | varchar(100) | 操作描述 | |
| method | varchar(10) | 请求方法 | |
| path | varchar(500) | 请求路径 | |
| query_params | text | 查询参数 | |
| request_body | text | 请求体 | |
| response_status | int | 响应状态码 | |
| response_body | text | 响应体 | |
| ip | varchar(50) | IP地址 | |
| browser | varchar(100) | 浏览器 | |
| os | varchar(100) | 操作系统 | |
| execution_time | int | 执行时间(毫秒) | |
| status | int | 状态 | 0:失败, 1:成功 |
| error_msg | text | 错误信息 | |
| created_at | datetime | 创建时间 | |

**索引：**
- `user_id`
- `username`
- `status`
- `method`
- `(user_id, created_at)`
- `(status, created_at)`

---

## 关系表

### 用户-角色关联表

**表名：** `system_users_to_system_roles`

| 字段 | 类型 | 说明 |
|------|------|------|
| users_id | int | 用户ID |
| roles_id | int | 角色ID |

---

### 角色-权限关联表

**Django 表名：** `system_roles_to_system_permissions`
**FastAPI 表名：** `system_roles_permissions`

| 字段 | 类型 | 说明 |
|------|------|------|
| roles_id / role_id | int | 角色ID |
| permissions_id / permission_id | int | 权限ID |

---

## 模型差异说明

Django 和 FastAPI 后端在模型定义上存在一些差异：

| 差异项 | Django | FastAPI |
|-------|--------|---------|
| 字典类型表名 | `system_dicts` | `system_dict_data` |
| 字典编码字段 | `dict_code` | `code` |
| 字典备注字段 | `remark` | `desc` |
| 角色-权限关联表 | `system_roles_to_system_permissions` | `system_roles_permissions` |
| 字典项默认值字段 | 无 | `is_default` |
| 字典项备注字段 | 无 | `remark` |

**注意：** 迁移数据时需要处理这些差异。

---

## ER 图

```
┌──────────────┐
│   Users      │
│──────────────│
│ id           │──────┐
│ username     │      │
│ password     │      │
│ name         │      │
│ mobile       │      │
│ email        │      │
│ dept_id      │──┐   │
└──────────────┘  │   │
                  │   │
┌──────────────┐  │   │   ┌──────────────────────┐
│ Departments  │  │   │   │ users_to_roles       │
│──────────────│  │   │   │──────────────────────│
│ id           │◄─┘   │   │ users_id             │◄──┘
│ name         │      │   │ roles_id             │◄──────┐
│ parent_id    │      │   └──────────────────────┘       │
└──────────────┘      │                                  │
                      │   ┌──────────────────────┐       │
                      │   │ roles_to_permissions │       │
                      │   │──────────────────────│       │
                      │   │ roles_id             │◄──────┤
                      │   │ permissions_id       │◄──┐   │
                      │   └──────────────────────┘   │   │
                      │                              │   │
                      │   ┌──────────────┐           │   │
                      │   │ Permissions  │           │   │
                      │   │──────────────│           │   │
                      │   │ id           │◄──────────┘   │
                      │   │ name         │               │
                      │   │ type         │               │
                      │   │ route_path   │               │
                      │   │ perm         │               │
                      │   │ parent_id    │               │
                      │   └──────────────┘               │
                      │                                  │
                      │   ┌──────────────┐               │
                      └───│    Roles     │◄──────────────┘
                          │──────────────│
                          │ id           │
                          │ name         │
                          │ code         │
                          │ status       │
                          └──────────────┘
```

---

## 迁移命令

### Django

```bash
# 创建迁移文件
uv run python manage.py makemigrations oauth system --env dev

# 执行迁移
uv run python manage.py migrate --env dev

# 查看迁移状态
uv run python manage.py showmigrations --env dev
```

### FastAPI

```bash
# 开发环境：自动创建表（generate_schemas=True）
uv run uvicorn app.main:app --reload

# 生产环境：使用 Aerich 管理迁移
aerich init -t app.core.config.TORTOISE_ORM
aerich init-db
aerich migrate
aerich upgrade
```

---

**最后更新：** 2026-03-23
**维护者：** DV-Admin Team
