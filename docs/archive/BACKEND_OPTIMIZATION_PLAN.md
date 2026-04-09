# Django 后端架构优化方案

> ⚠️ **已归档**
>
> 本文档已于 2026-04-09 归档，内容可能已过时。
> 当前权威文档请参考 `/AGENTS.md` 和 `/docs/README.md`。
>
> **归档原因**：已实施完成

> **状态**：~~草案 (Draft)~~ **已实施完成**
> **目标**：解决代码审查中发现的安全、性能、正确性及可维护性问题，提升系统稳健性。

---

## 1. 分页架构重构 (Pagination Refactoring)

### 现状问题
- 分页字段转换（`results` -> `list`, `count` -> `total`）在 `ResponseMiddleware` 中通过模糊匹配实现。
- 存在误伤非分页接口的风险。

### 优化方案
将分页响应逻辑下沉到 `GlobalPagination` 类中，利用 DRF 原生钩子实现。

**代码变更点：** `backend/drf_admin/utils/pagination.py`
- 重写 `get_paginated_response` 方法。
- 返回预定义的 `list` 和 `total` 字段。

---

## 2. 响应中间件简化 (Middleware Simplification)

### 现状问题
- 承担了过多的数据转换逻辑。
- 成功/失败信息硬编码为中文，不利于国际化。

### 优化方案
- 移除分页转换代码。
- 使用 `django.utils.translation.gettext_lazy` ( _ ) 封装提示信息。
- 增强对 `Response` 对象的判断，确保只处理应用层 JSON 响应。

**代码变更点：** `backend/drf_admin/utils/middleware.py`

---

## 3. 安全日志脱敏增强 (Robust Log Masking)

### 现状问题
- 脱敏逻辑依赖固定字段路径（如 `response.data['data']['accessToken']`）。
- 无法应对非标准结构的 Token 返回。

### 优化方案
- 实现递归脱敏函数 `mask_sensitive_data(data)`。
- 对所有包含 `password`, `token`, `secret`, `key` (忽略大小写) 的键进行模糊匹配脱敏。
- 设置响应体记录长度上限，防止大数据量请求撑爆磁盘。

**代码变更点：** `backend/drf_admin/utils/middleware.py`

---

## 4. 性能优化 (Performance: N+1 Queries)

### 现状问题
- `UserInfoView` 和 `RoutesAPIView` 获取用户信息时未进行预查询，导致 `get_user_info()` 和 `get_menus()` 产生多次数据库 IO。

### 优化方案
- 在相关视图获取 `request.user` 对应的完整对象时，使用 `select_related('dept')` 和 `prefetch_related('roles__permissions')`。

**代码变更点：** `backend/drf_admin/apps/oauth/views/oauth.py`

### 代码审查补充 (2026-03-24)
- 当前分支新增的 `prefetch_related('roles__permissions')` 还不能证明真正消除了重复查询。
- 根因是下游模型方法仍然在重新创建 queryset：
  - `Users._get_user_permissions()` 使用 `self.roles.values_list('permissions__perm', flat=True)`
  - `Users.get_user_info()` 使用 `self.roles.values_list('name', flat=True)`
  - `Users.get_menus()` 使用 `Permissions.objects.filter(roles__in=self.roles.all())`
- 这些调用会绕开预取对象图，导致“视图层做了预取，但模型层仍可能继续发起新查询”的情况。

### 修正建议
1. 将 `get_user_info()` / `get_menus()` 改成优先消费已预取的 `roles` 与 `role.permissions` 对象，而不是继续使用 `values_list(...)` 或新的 `Permissions.objects.filter(...)`。
2. 如果需要保留 queryset 方案，则补充查询次数测试，证明该优化确实减少了 SQL 次数，而不是仅增加了代码复杂度。
3. 在合并前至少补一条针对 `UserInfoView` 或 `RoutesAPIView` 的 query-count 回归测试，避免“计划写了优化，实际没有收益”的情况再次发生。

---

## 5. 工程化与代码质量 (Engineering Quality)

### 优化方案
- **类型注解**：为 `utils` 下的所有核心工具函数添加 Type Hints。
- **异常处理**：在 `exception_handler` 中针对 Redis 连通性异常增加降级逻辑的显式日志记录。
- **配置分离**：将白名单等硬编码逻辑进一步抽象到配置项。

---

## 6. 实施路线图

1. **Phase 1**: 重构分页与响应中间件（核心链路）。
2. **Phase 2**: 增强日志脱敏逻辑（安全加固）。
3. **Phase 3**: 视图查询性能调优（性能提升）。
4. **Phase 4**: 类型提示补齐与文档更新。

---

## 7. 当前收口状态 (2026-03-24)

### 已落地决策：分页格式唯一责任层
- 采用方案：`GlobalPagination` 直接产出最终分页格式（`code/msg/errors/data.list/data.total`）。
- `ResponseMiddleware` 成功路径不再做全局 `results -> list` / `count -> total` 转换。
- `ResponseMiddleware` 遇到已标准化响应时直接透传，避免二次包装。

### 本次收口文件
- `backend/drf_admin/apps/oauth/views/oauth.py`
- `backend/drf_admin/apps/system/models.py`
- `backend/drf_admin/utils/middleware.py`
- `backend/drf_admin/utils/pagination.py`

### 测试补齐范围
- 分页接口返回 `data.list` / `data.total`
- 非分页 `results` 接口不被误改
- `RoutesAPIView` 的无效用户/禁用用户场景
- 登出接口避免手工 `{code,msg}` 导致的二次包装

### 环境稳定性修复
- Django 日志目录初始化改为幂等创建（`os.makedirs(..., exist_ok=True)`），避免测试阶段 `FileExistsError`。

---

**最后更新：** 2026-03-24
**负责人：** opencode agent
