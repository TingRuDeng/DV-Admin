---
ai_summary:
  purpose: "集中记录 DV-Admin 已确认技术债务、影响范围和治理边界。"
  read_when:
    - "制定迭代计划时"
    - "评估是否处理非任务范围问题时"
  source_of_truth:
    - "docs/ARCHITECTURE.md"
    - "docs/API_ENDPOINTS.md"
    - "docs/DATABASE_SCHEMA.md"
    - "frontend/src"
    - "backend/drf_admin"
    - "fastapi/app"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "git ls-files docs/ARCHITECTURE.md docs/API_ENDPOINTS.md docs/DATABASE_SCHEMA.md"
  stale_when:
    - "债务已修复但条目未回写"
    - "优先级、影响范围或治理策略变化"
---

# DV-Admin 技术债务记录

> 本文档记录已确认债务，不把规划项伪装成当前规范。

## Purpose

集中记录已确认的技术债务、影响范围与处理约束。

## Source of truth

- `docs/ARCHITECTURE.md`
- `docs/API_ENDPOINTS.md`
- `docs/DATABASE_SCHEMA.md`
- `frontend/src`
- `backend/drf_admin`
- `fastapi/app`

## Key facts

- 债务条目按优先级管理，但不是当前行为规范。
- 未进入本文档的事项默认不算已确认债务。
- 债务描述需要落到代码位置或契约层证据。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- full: `pnpm --dir frontend run quality`
- full: `make -C fastapi quality`

## Stale when

- 债务项被修复、降级或影响范围变化。
- 新技术债被确认但没有进入跟踪。

---

## 债务分类

| 级别 | 说明 | 处理优先级 |
|------|------|-----------|
| 🔴 高 | 影响功能或有安全风险 | 尽快处理 |
| 🟡 中 | 影响性能或可维护性 | 计划处理 |
| 🟢 低 | 代码质量问题 | 有空处理 |

---

## 当前技术债务

### 1. Django 和 FastAPI 模型差异

**级别：** 🟡 中

**描述：**
Django 和 FastAPI 后端在数据库模型定义上存在差异，导致数据迁移和同步困难。

**具体问题：**
- 字典类型表名不同（`system_dicts` vs `system_dict_data`）
- 关联表命名不同

**影响范围：**
- 数据迁移工具需要处理差异
- 文档需要分别说明

**计划解决方案：**
1. 统一模型定义（推荐使用 Django 的命名）
2. 继续增强数据迁移脚本的端到端 fixture 覆盖
3. 更新 FastAPI 模型

**当前治理进展：**
- FastAPI Django fixture 导入脚本已改为 fail-fast
- 已覆盖缺少 fixture、单条导入失败和 M2M 目标缺失三类失败测试
- 已新增 `scripts/model_contracts.py` 作为 Django → FastAPI 共享模型契约目录，并用 `scripts/validate_model_contracts.py` 校验导入脚本、测试和文档同步
- 权限菜单 `keepAlive/alwaysShow` 已显式映射到 FastAPI 的 `keep_alive/always_show`
- 字典主表内部字段已统一为 `dict_code/remark`，后续可继续推进表名统一

**预计工作量：** 2-3 天

---

### 2. 前端类型定义仍需持续收口

**级别：** 🟢 低

**描述：**
前端核心请求、存储、路由、标签页、设置和 WebSocket 类型边界已经分阶段收口，但示例模块和部分历史组件仍需持续治理。

**具体问题：**
- 示例模块中仍可能存在与真实后端不一致的 API 类型
- 历史通用组件的扩展字段仍需要按业务语义继续收窄
- 类型治理测试已覆盖核心路径，但没有覆盖全部演示页面

**影响范围：**
- 示例代码迁移为真实业务代码时需要二次核对
- 大范围重构历史组件时仍需依赖目标测试补强

**计划解决方案：**
1. 继续按模块补充类型治理测试
2. 删除或隔离不再使用的示例 API
3. 为仍在生产路径中的历史组件补显式输入输出类型

**预计工作量：** 持续治理

---

### 3. 测试覆盖率不足

**级别：** 🟡 中

**描述：**
项目测试覆盖率不够高，部分模块缺少测试。

**当前状态：**
- FastAPI 后端：80%+ 覆盖率
- Django 后端：已有系统模块、响应/request id/health 契约测试、关键读端点与用户写端点运行时契约抽样、RBAC 权限边界直接契约测试，但整体覆盖率仍偏低
- 前端：已补 store/router、WebSocket、API 契约、可访问性和性能 smoke，以及用户管理核心业务 E2E；跨业务完整 E2E 仍不充分

**影响范围：**
- 重构风险增加
- 回归测试困难

**计划解决方案：**
1. 补充 Django 后端测试
2. 完善前端单元测试
3. 继续基于稳定测试数据增加角色、菜单、文件等核心业务 E2E 用例

**预计工作量：** 5-7 天

---

### 4. API 文档自动化

**级别：** 🟢 低

**描述：**
API 文档目前手动维护，容易与代码不同步。

**具体问题：**
- `docs/API_ENDPOINTS.md` 需要手动更新
- 容易遗漏新增的 API
- 响应格式可能不一致

**计划解决方案：**
1. 从 OpenAPI/Swagger 自动生成文档
2. 在现有 `scripts/validate_api_contracts.py` 基础上扩展路由覆盖校验
3. 使用工具自动更新

**预计工作量：** 2-3 天

---

### 5. 数据库索引优化

**级别：** 🟢 低

**描述：**
部分查询缺少索引，大数据量时性能下降。

**具体问题：**
- 部分查询字段未添加索引
- 复合索引不够优化
- 缺少查询性能监控

**计划解决方案：**
1. 分析慢查询日志
2. 添加缺失的索引
3. 优化复合索引

**预计工作量：** 1-2 天

---

### 6. 错误处理统一

**级别：** 🟡 中

**描述：**
错误处理方式不够统一，前端需要处理多种错误格式。

**具体问题：**
- 不同后端错误格式仍有历史差异
- 错误码定义不够规范
- 错误信息国际化不完整

**计划解决方案：**
1. 先用现有契约测试持续锁住前端依赖字段
2. 单独设计错误码规范和兼容迁移方案
3. 完善错误信息国际化

**当前治理进展：**
- 前端错误边界已新增 `normalizeApiErrorEnvelope`，请求拦截器统一消费归一化后的 `{ code, message, data, raw }`
- FastAPI 参数校验明细 `data.errors[].message` 已优先展示，避免只显示泛化的“请求参数验证失败”
- 已新增 `scripts/api_error_codes.py` 作为共享错误码契约目录，并用前端、Django、FastAPI 契约测试锁定 `40000/40001/40002` 的公共语义
- FastAPI 登录失败和验证码失败已改为通用业务错误 `40000`，避免复用 Access Token 失效码 `40001` 后误触发前端 token 刷新流程

**预计工作量：** 2-3 天

---

### 7. 审计日志 UX、批量操作与导入导出状态

**级别：** 🟡 中

**描述：**
成熟产品能力中，后台操作审计、批量任务和导入导出状态反馈仍偏基础，需要业务 PRD 后再系统推进。

**具体问题：**
- 审计日志已能记录操作，但筛选、详情、失败定位体验仍有限
- 批量操作缺少统一任务状态和失败明细反馈
- 导入导出缺少统一的异步任务进度、历史记录和重试入口

**计划解决方案：**
1. 先定义审计日志与批量任务 PRD
2. 抽象统一任务状态模型
3. 补充导入导出任务列表、失败明细和重试机制

**预计工作量：** 5-8 天

---

### 8. 代码注释和文档

**级别：** 🟢 低

**描述：**
部分代码缺少注释，复杂逻辑难以理解。

**具体问题：**
- 复杂业务逻辑缺少说明
- 工具函数缺少使用示例
- 配置项缺少详细说明

**计划解决方案：**
1. 补充关键代码注释
2. 添加 docstring
3. 完善配置文档

**预计工作量：** 持续进行

---

### 9. 前端超大组件拆分

**级别：** 🟢 低

**描述：**
主要业务页面和共享组件的大文件拆分主线已完成，当前仅保留少量历史兼容层文件需要冻结边界并避免新增调用。

**具体问题：**
- `frontend/src/components/CURD/PageContent.vue` 仍是历史兼容层，文件体量较大
- `components/CURD` 目录仍包含历史 API 和类型定义，不适合作为新页面抽象基础
- 兼容层文件仍会增加后续删除窗口的回归确认成本

**2026-05-23 复核：**
- `components/CURD` 兼容层外已无业务调用点，新增调用已由 ESLint 和 Vitest 守卫阻断
- `frontend/src/types/components.d.ts` 已移除 CURD 全局组件声明，避免模板自动补全继续暴露旧抽象
- `PageContent.vue` 仍保留为历史兼容层文件；当前更适合冻结边界而不是立即删除
- `TableSelect`、TagsView、MenuSearch、TextScroll、Settings、Profile、Dashboard、字典同步 demo 和系统管理页表单抽屉拆分已合入主线

**影响范围：**
- 删除 `components/CURD` 前仍需确认是否存在外部二开引用
- 继续维护旧兼容层时需要防止新页面回流到旧抽象

**计划解决方案：**
1. 保持 `components/CURD` 只作为历史兼容层，不再新增调用点
2. 继续依赖 `curd-deprecation-governance` 和页面模式测试阻断回流
3. 等出现明确退场窗口时，再单独删除 `frontend/src/components/CURD/`

**预计工作量：** 0.5-1 天退场评估，实际删除需额外回归窗口

---

## 已解决的技术债务

### ✅ FastAPI 默认密码配置收口

**描述：** FastAPI 后端曾在 `Settings.default_password` 中保留代码默认值，且样例环境文件使用弱默认密码。

**解决方案：**
- `fastapi/app/core/config.py` 移除 `DEFAULT_PASSWORD` 代码默认值，改为必须显式配置
- `fastapi/.env.example` 使用非弱占位值 `ChangeMe!2026`
- `fastapi/app/api/v1/system/users.py` 接口说明改为强调显式配置
- 新增配置回归测试，防止未配置 `DEFAULT_PASSWORD` 时继续静默回退

---

### ✅ 2026-05 安全审查高优项收口

**描述：** 深度审查发现 AES-ECB、密码 URL 传递、生产环境文件被跟踪、双后端密码重置方法不一致和 FastAPI CORS 默认端口错误等问题。

**解决方案：**
- 密码字段加密升级为 AES-GCM，并保留旧 ECB 密文兼容解密
- 重置密码请求改为请求体传递，避免密码进入 URL query
- 删除被跟踪的 `backend/.env.pro`，并通过 `.gitignore` 阻止私有 `.env.*` 再次提交
- FastAPI 密码重置接口支持 `PUT`，对齐 Django/前端契约，同时保留 `POST` 兼容
- FastAPI 默认 CORS 来源与 `fastapi/.env.example` 对齐前端开发端口 `9527`
- 相关修复已补前端、Django 和 FastAPI 回归测试

**剩余注意事项：**
- Git 历史中已经出现过的旧 `SECRET_KEY` 仍需在真实环境轮换；如需彻底清理历史，应单独协调 `git filter-repo` 或 BFG 流程

---

### ✅ 登录默认凭据与 Django 默认密码配置收口

**描述：** 登录/注册表单曾直接预填 `admin/123456`，Django 新增用户默认密码曾在代码中回退到 `123456`。

**解决方案：**
- 登录/注册表单改为读取 `VITE_LOGIN_DEFAULT_USERNAME` 与 `VITE_LOGIN_DEFAULT_PASSWORD`
- 仅 `frontend/.env.development` 为本地演示显式配置默认预填；生产和预发环境不配置时为空
- Django `DEFAULT_PWD` 改为必须由环境显式提供
- `backend/.env.example` 与 CI `.env.test` 使用非 `123456` 的占位值
- 新增登录默认值与 Django settings 回归测试

---

### ✅ UserStore 空态类型收口

**描述：** `frontend/src/store/modules/user-store.ts` 曾使用 `{} as UserInfo` 绕过 TypeScript 空值检查。

**解决方案：**
- 初始和重置状态统一为 `{ roles: [], perms: [] }`
- 获取用户信息时兜住缺失的 `roles/perms` 字段
- 更新 store 单测，确保 reset 后保持合法空用户信息

---

### ✅ Django 弃用警告收口

**描述：** Django 测试输出中存在 `USE_L10N` 与 drf_yasg renderer 兼容警告。

**解决方案：**
- 移除 `USE_L10N`
- 设置 `SWAGGER_USE_COMPAT_RENDERERS = False`
- 新增 `backend/drf_admin/utils/test_settings_deprecations.py` 覆盖配置回归

---

### ✅ Redis 降级支持

**描述：** 当 Redis 不可用时，系统会自动降级到内存缓存。

**解决方案：**
- Django：使用 `LocMemCache` 作为后备
- FastAPI：实现内存缓存服务
- WebSocket：使用 `InMemoryChannelLayer`

---

### ✅ JWT 双 Token 机制

**描述：** 实现了 Access Token + Refresh Token 机制，支持无感刷新。

**解决方案：**
- 后端返回双 Token
- 前端自动检测过期并刷新
- Token 存储支持"记住我"

---

### ✅ 命名自动转换

**描述：** 实现了 camelCase 和 snake_case 的自动转换。

**解决方案：**
- Django：使用 `djangorestframework_camel_case` 中间件
- FastAPI：统一响应格式
- 前端无需关心命名差异

---

### ✅ 共享 API 契约基础门禁

**描述：** Django/FastAPI 响应包裹存在历史字段差异，缺少可执行契约校验。

**解决方案：**
- 新增 `scripts/api_contracts.py` 作为共享契约断言入口
- 新增 `scripts/api_endpoint_contracts.py` 作为关键端点契约目录
- 新增 Django、FastAPI 与前端契约测试
- 新增 `scripts/validate_api_contracts.py` 并纳入 CI 文档校验阶段

---

### ✅ WebSocket 连接管理器基础抽离

**描述：** WebSocket 连接、订阅、重连和断开逻辑集中在 Vue composable 中，难以直接测试。

**解决方案：**
- 新增 `frontend/src/composables/websocket/stomp-connection-manager.ts`
- `useStomp` 保留 Vue ref API，内部委托连接管理器
- 新增 fake client 单测覆盖重复连接、授权缺失、手动断开和订阅清理

---

### ✅ 前端共享组件与测试治理收口

**描述：** 标签页、TableSelect、WebSocket STOMP manager 和主题样式测试存在边界缺口或文件职责过宽。

**解决方案：**
- 修复 `tags-view-store` 关闭左右标签时目标不存在导致 Promise 不 resolve 的边界
- 拆分 `TableSelect` 类型、搜索表单、数据表和底部动作组件，并补充类型治理与行为测试
- 拆出 WebSocket STOMP 连接 helper、类型、client factory 和订阅注册表
- 将原主题样式大测试按职责拆分为多个小测试和共享工具
- 复核 `components/CURD` 兼容层，移除旧全局组件声明并补充禁止回流守卫

---

## 技术债务处理流程

### 1. 发现债务

- 代码审查时发现
- 性能测试时发现
- 用户反馈
- 开发过程中发现

### 2. 记录债务

1. 在本文档中添加记录
2. 标注级别和影响范围
3. 评估工作量
4. 制定解决方案

### 3. 处理债务

1. 选择优先级高的债务
2. 创建任务分支
3. 实施解决方案
4. 编写测试
5. 代码审查
6. 合并主分支

### 4. 更新文档

1. 将已解决的债务移到"已解决"部分
2. 记录解决日期和方案
3. 更新相关文档

---

## 债务统计

| 状态 | 数量 |
|------|------|
| 🔴 高优先级 | 0 |
| 🟡 中优先级 | 4 |
| 🟢 低优先级 | 5 |
| ✅ 已解决 | 11 |
| **当前未解决** | **9** |
| **累计记录** | **20** |

---

## 定期审查

本文档应定期审查（建议每月一次），更新债务状态和优先级。

**上次审查日期：** 2026-05-23
**下次审查日期：** 2026-06-23

---

**最后更新：** 2026-05-23
**维护者：** DV-Admin Team
