# DV-Admin 文档导航

> 本文件是项目文档的**单一导航入口**。所有文档的用途、权威级别和阅读路径都在此定义。

---

## 文档结构总览

```
DV-Admin/
├── AGENTS.md                    # [权威] 代理工作规则入口
├── docs/
│   ├── README.md               # [本文件] 文档导航入口
│   ├── ARCHITECTURE.md         # [权威] 系统架构设计
│   ├── QUALITY_GATES_IMPLEMENTATION_PLAN.md # [计划] 质量门禁补齐实施方案
│   ├── API_ENDPOINTS.md        # [参考] API 端点文档
│   ├── DATABASE_SCHEMA.md      # [参考] 数据库模型文档
│   ├── KNOWN_PITFALLS.md       # [警告] 已知陷阱和常见错误
│   ├── TECH_DEBT.md            # [跟踪] 技术债务记录
│   ├── AGENT_STARTER_PROMPT.md # [工具] 代理启动提示词
│   ├── DOC_SYNC_CHECKLIST.md   # [流程] 文档同步检查清单
│   └── archive/                # [历史] 归档文档
│       └── README.md
├── backend/
│   └── README.md               # [模块] Django 后端说明
├── fastapi/
│   └── README.md               # [模块] FastAPI 后端说明
└── frontend/
    └── README.md               # [模块] 前端说明
```

---

## 文档权威级别

| 级别 | 含义 | 示例 |
|------|------|------|
| **权威** | 代码冲突时以文档为准，修改需谨慎 | `AGENTS.md`, `ARCHITECTURE.md` |
| **参考** | 从代码自动生成或同步，辅助理解 | `API_ENDPOINTS.md`, `DATABASE_SCHEMA.md` |
| **警告** | 必须阅读，避免重复犯错 | `KNOWN_PITFALLS.md` |
| **跟踪** | 记录待解决的问题 | `TECH_DEBT.md` |
| **计划** | 面向实施的任务拆解和执行方案 | `QUALITY_GATES_IMPLEMENTATION_PLAN.md` |
| **模块** | 模块级说明，模块内权威 | 各子目录 `README.md` |
| **历史** | 归档文档，仅供参考 | `docs/archive/` |

---

## 按任务类型的阅读路径

### 前端开发任务

```
1. AGENTS.md                    # 了解工作规则
2. docs/ARCHITECTURE.md         # 理解系统架构
3. frontend/README.md           # 前端模块说明
4. frontend/src/目标模块/        # 实际代码
5. docs/API_ENDPOINTS.md        # 查阅 API 接口
```

### 后端开发任务（Django）

```
1. AGENTS.md                    # 了解工作规则
2. docs/ARCHITECTURE.md         # 理解系统架构
3. backend/README.md            # Django 模块说明
4. backend/drf_admin/apps/目标模块/ # 实际代码
5. docs/DATABASE_SCHEMA.md      # 查阅数据模型
```

### 后端开发任务（FastAPI）

```
1. AGENTS.md                    # 了解工作规则
2. docs/ARCHITECTURE.md         # 理解系统架构
3. fastapi/README.md            # FastAPI 模块说明
4. fastapi/app/api/v1/目标模块/  # 实际代码
5. docs/DATABASE_SCHEMA.md      # 查阅数据模型
```

### API 修改任务

```
1. AGENTS.md                    # 了解 API 契约约束
2. docs/API_ENDPOINTS.md        # 查阅现有 API
3. docs/DATABASE_SCHEMA.md      # 理解数据模型
4. 搜索前端调用点                # grep -r "api/xxx" frontend/src/
5. 修改代码并测试
6. 更新 docs/API_ENDPOINTS.md   # 同步文档
```

### 权限相关任务

```
1. AGENTS.md                    # 了解权限约束
2. docs/ARCHITECTURE.md         # 权限章节
3. backend/drf_admin/apps/system/models.py  # 权限模型
4. frontend/src/store/modules/permission-store.ts  # 前端权限
```

### Bug 修复任务

```
1. AGENTS.md                    # 了解工作规则
2. docs/KNOWN_PITFALLS.md       # 检查是否已知问题
3. docs/TECH_DEBT.md            # 检查是否已记录
4. 定位问题代码
5. 修复并测试
6. 如发现新陷阱，更新 KNOWN_PITFALLS.md
```

---

## 文档用途详解

### AGENTS.md

**用途：** 代理工作规则的单一权威入口

**内容：**
- 启动检查清单
- 工作流规则
- 关键约束
- 常见任务指南
- 文档同步规则

**何时阅读：** 每次开始工作前

**何时更新：**
- 新增工作流规则
- 修改约束条件
- 调整启动流程

---

### ARCHITECTURE.md

**用途：** 系统架构设计的权威文档

**内容：**
- 整体架构图
- 前后端通信流程
- 认证授权机制
- RBAC 权限模型
- 数据流向

**何时阅读：**
- 新人入职
- 架构变更前
- 理解系统行为时

**何时更新：**
- 架构调整
- 新增核心模块
- 流程变更

---

### API_ENDPOINTS.md

**用途：** API 端点参考文档

**内容：**
- 端点列表
- 请求/响应格式
- 认证要求
- 错误码说明

**何时阅读：**
- 前后端联调
- API 修改
- 接口对接

**何时更新：**
- 新增/修改/删除 API
- 修改响应格式
- 修改错误码

**注意：** 此文档应与代码保持同步，代码是真理之源

---

### DATABASE_SCHEMA.md

**用途：** 数据库模型参考文档

**内容：**
- 表结构说明
- 字段定义
- 关系图
- 索引说明

**何时阅读：**
- 数据模型修改
- 查询优化
- 数据迁移

**何时更新：**
- 新增/修改/删除表
- 修改字段
- 添加/删除索引

**注意：** 此文档应与代码保持同步，代码是真理之源

---

### KNOWN_PITFALLS.md

**用途：** 已知陷阱和常见错误记录

**内容：**
- 常见错误及解决方案
- 历史踩坑记录
- 兼容性问题
- 边界情况

**何时阅读：**
- 遇到问题时
- 修改相关代码前
- 代码审查时

**何时更新：**
- 发现新陷阱
- 解决历史问题
- 添加警告提示

---

### TECH_DEBT.md

**用途：** 技术债务跟踪

**内容：**
- 已知技术债务列表
- 优先级和影响范围
- 计划解决方案

**何时阅读：**
- 规划重构时
- 评估工作量时
- 技术决策时

**何时更新：**
- 发现新债务
- 解决债务
- 调整优先级

---

### AGENT_STARTER_PROMPT.md

**用途：** 新代理会话的启动提示词

**内容：**
- 快速启动指令
- 必读文件列表
- 基本工作流程

**何时使用：**
- 开启新的代理会话时
- 复制粘贴到新对话

---

### DOC_SYNC_CHECKLIST.md

**用途：** 文档同步检查清单

**内容：**
- 代码变更与文档更新对应关系
- 检查项列表
- 完成标准

**何时使用：**
- 完成代码修改后
- 提交 PR 前
- 发布前检查

---

## 文档维护原则

### 1. 代码是真理之源

- 文档描述代码行为，不定义行为
- 文档与代码冲突时，以代码为准，并修复文档
- 不要在文档中描述"应该怎样"，只描述"实际怎样"

### 2. 单一权威来源

- 每类信息只有一个权威文档
- 其他文档引用权威文档，不重复定义
- 避免信息分散导致不一致

### 3. 及时同步

- 代码变更时同步更新文档
- 使用 `DOC_SYNC_CHECKLIST.md` 检查
- 提交 PR 前确认文档已更新

### 4. 归档而非删除

- 过时文档移入 `docs/archive/`
- 保留历史信息供参考
- 在归档文档中注明"已过时"

---

## 自动化潜力

以下文档适合未来自动化生成/更新：

| 文档 | 自动化方式 | 优先级 |
|------|-----------|--------|
| `API_ENDPOINTS.md` | 从 OpenAPI/Swagger 生成 | 高 |
| `DATABASE_SCHEMA.md` | 从模型定义生成 | 中 |
| `TECH_DEBT.md` | 从代码注释/issue 提取 | 低 |

以下文档必须人工维护：

- `AGENTS.md` - 工作流规则
- `ARCHITECTURE.md` - 架构决策
- `KNOWN_PITFALLS.md` - 陷阱记录

---

## 快速链接

- [代理工作规则](../AGENTS.md)
- [系统架构](./ARCHITECTURE.md)
- [API 端点](./API_ENDPOINTS.md)
- [数据库模型](./DATABASE_SCHEMA.md)
- [已知陷阱](./KNOWN_PITFALLS.md)
- [技术债务](./TECH_DEBT.md)
- [代理启动提示词](./AGENT_STARTER_PROMPT.md)
- [文档同步检查清单](./DOC_SYNC_CHECKLIST.md)

---

**最后更新：** 2026-03-23
**维护者：** DV-Admin Team
