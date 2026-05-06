# DV-Admin 文档导航

> 本文件是项目文档的**单一导航入口**。所有文档的用途、权威级别和阅读路径都在此定义。

## 目的

为人类维护者与 AI 代理提供统一文档入口，快速定位权威文档、任务阅读路径和校验入口。

## 适合读者

- 新加入项目、需要快速上手的开发者
- 需要按任务选择上下文的 AI 代理
- 负责代码审查与文档一致性检查的维护者

## 一分钟摘要

- 主规则入口是 `AGENTS.md`，主导航入口是本文件。
- AI 快速索引入口是 `docs/AI_CONTEXT.md`，不替代规则文档。
- 架构、API、数据库、坑点、债务分别由独立文档负责，避免一个文档承载全部事实。
- 提交前用 `docs/DOC_SYNC_CHECKLIST.md` 和 `scripts/validate_docs.py` 做文档闭环检查。

```yaml
ai_summary:
  authority: "文档导航与任务阅读路径的唯一入口"
  scope: "文档职责分工、阅读顺序、权威级别和校验入口"
  read_when:
    - "进入仓库后需要确定先读什么时"
    - "开始新任务前需要装配最小上下文时"
  verify_with:
    - "AGENTS.md"
    - "docs/AI_CONTEXT.md"
    - "docs/ARCHITECTURE.md"
    - "docs/API_ENDPOINTS.md"
    - "docs/DOC_SYNC_CHECKLIST.md"
    - "scripts/validate_docs.py"
  stale_when:
    - "文档入口新增或迁移"
    - "权威文档职责边界调整"
    - "校验脚本规则或路径变化"
```

## 权威边界

- 本文件负责导航与分工，不负责替代架构/API/数据库事实正文。
- 与代码冲突时信任代码，并在同一变更修正对应权威文档。

## 如何验证

- 文档入口唯一性：确认导航入口仅为 `docs/README.md`。
- AI 索引唯一性：确认 `docs/AI_CONTEXT.md` 存在且在本文件可达。
- 校验闭环：运行 `python3 scripts/validate_docs.py`。

---

## 文档结构总览

```
DV-Admin/
├── AGENTS.md                    # [权威] 代理工作规则入口
├── docs/
│   ├── README.md               # [本文件] 文档导航入口
│   ├── AI_CONTEXT.md           # [权威] AI 任务路由短索引
│   ├── ARCHITECTURE.md         # [权威] 系统架构设计
│   ├── FRONTEND_OPTIMIZATION_BACKLOG.md # [跟踪] 当前前端优化待办
│   ├── API_ENDPOINTS.md        # [权威-概览] API 契约核心概览
│   ├── DATABASE_SCHEMA.md      # [权威-概览] 数据库模型核心概览
│   ├── KNOWN_PITFALLS.md       # [权威] 已知陷阱和常见错误
│   ├── TECH_DEBT.md            # [权威-跟踪] 技术债务记录
│   ├── AGENT_STARTER_PROMPT.md # [工具] 代理启动提示词
│   ├── DOC_SYNC_CHECKLIST.md   # [流程] 文档同步检查清单
│   └── archive/                # [历史] 归档文档
│       ├── README.md
│       ├── CODE_REVIEW_DJANGO_BACKEND.md
│       ├── BACKEND_OPTIMIZATION_PLAN.md
│       └── QUALITY_GATES_IMPLEMENTATION_PLAN.md
├── backend/
│   └── README.md               # [模块] Django 后端说明
├── fastapi/
│   └── README.md               # [模块] FastAPI 后端说明
├── 后续优化/
│   └── README.md               # [历史] 旧前端优化方案说明
├── scripts/
│   └── validate_docs.py        # [校验] 文档结构与链接校验
└── frontend/
    └── README.md               # [模块] 前端说明
```

**后端实现说明：**
- `backend/`（Django）与 `fastapi/`（FastAPI）是同一产品后端的两套替代实现
- 日常开发和部署通常二选一，不要求同时运行
- 涉及共享 API / 数据契约时，仍需同步维护两套实现的兼容性

---

## 开发环境服务启动与使用

### 服务角色与默认地址

| 服务 | 默认地址 | 说明 |
|------|----------|------|
| 前端开发服务器 | `http://localhost:9527` | Vite 开发服务器，浏览器访问入口 |
| Django 后端 | `http://localhost:8769` | `backend/` 实现，日常开发二选一 |
| FastAPI 后端 | `http://localhost:8769` | `fastapi/` 实现，日常开发二选一 |

- 前端当前会将 `/dev-api` 代理到 `http://127.0.0.1:8769`
- Django 与 FastAPI 默认端口相同，因此本地联调通常只启动其中一个
- 如果你需要切换后端实现，先停止当前后端，或显式修改其中一套后端端口并同步前端配置

### 推荐启动顺序

```text
1. 先确定本次联调使用 Django 还是 FastAPI
2. 启动选中的后端实现，并确认 http://localhost:8769 可访问
3. 启动前端开发服务器，打开 http://localhost:9527
4. 使用 admin/123456 或 visitor/123456 登录验证
5. 如需切换后端实现，先停掉当前后端再切换
```

### 快速启动命令

**前端：**

```bash
cd frontend
pnpm install
pnpm run dev
```

**后端（Django）：**

```bash
cd backend
uv sync
cp .env.example .env.dev
uv run python manage.py migrate --env dev
uv run python manage.py loaddata init_data.json --env dev
uv run python manage.py runserver 0.0.0.0:8769 --env dev
```

**后端（FastAPI）：**

```bash
cd fastapi
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env
./scripts/dev.sh
```

### 日常使用约定

- 前端开发时始终连接“当前选中的那一套后端实现”，不是同时连接 Django 和 FastAPI
- 共享 API / 数据契约修改时，需要考虑两套后端实现的兼容性，但不代表本地联调要双开
- 如果后端端口不是 `8769`，请同步修改 [frontend/.env.development](/Users/dengtingru/Desktop/code/DV-Admin/frontend/.env.development) 中的 `VITE_APP_API_URL`
- 本地开发环境默认数据库通常是 SQLite；当前仓库的 Django 开发库位于 [backend/drf_admin/db.sqlite3](/Users/dengtingru/Desktop/code/DV-Admin/backend/drf_admin/db.sqlite3)
- 如需通过 MCP 查看本地开发数据，可为 SQLite MCP 指向该数据库文件；这类访问仅面向本地调试，不代表生产数据库类型或生产数据状态
- 更完整的启动细节分别见：
  - [AGENTS.md](/Users/dengtingru/Desktop/code/DV-Admin/AGENTS.md)
  - [frontend/README.md](/Users/dengtingru/Desktop/code/DV-Admin/frontend/README.md)
  - [backend/README.md](/Users/dengtingru/Desktop/code/DV-Admin/backend/README.md)
  - [fastapi/README.md](/Users/dengtingru/Desktop/code/DV-Admin/fastapi/README.md)

### SQLite MCP 示例

如需让支持 MCP 的客户端直接查看 Django 本地开发库，可使用类似配置：

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-sqlite",
        "/Users/dengtingru/Desktop/code/DV-Admin/backend/drf_admin/db.sqlite3"
      ]
    }
  }
}
```

- 上述配置连接的是 Django 本地开发数据库，不是生产库
- 若切换到 FastAPI 本地库，需要单独修改为它对应的 SQLite 文件
- 如果 MCP 客户端支持写操作，默认应以只读排查为主，谨慎执行写入

---

## 文档权威级别

| 级别 | 含义 | 示例 |
|------|------|------|
| **权威** | 规则、导航、架构与风险边界事实入口 | `AGENTS.md`, `docs/README.md`, `docs/AI_CONTEXT.md`, `docs/ARCHITECTURE.md`, `docs/KNOWN_PITFALLS.md` |
| **权威-概览** | 经过代码核验的核心概要，非全量清单 | `docs/API_ENDPOINTS.md`, `docs/DATABASE_SCHEMA.md` |
| **权威-跟踪** | 已确认且持续维护的治理事项 | `docs/TECH_DEBT.md`, `docs/DOC_SYNC_CHECKLIST.md` |
| **跟踪** | 迭代规划与待办，不作为当前事实规范 | `docs/FRONTEND_OPTIMIZATION_BACKLOG.md` |
| **模块** | 模块级说明，模块内权威 | 各子目录 `README.md` |
| **历史** | 归档文档，仅供参考 | `docs/archive/`, `后续优化/` |

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

**说明：** 仅在本次任务明确选择 Django 作为目标实现时进入这一路径。

### 后端开发任务（FastAPI）

```
1. AGENTS.md                    # 了解工作规则
2. docs/ARCHITECTURE.md         # 理解系统架构
3. fastapi/README.md            # FastAPI 模块说明
4. fastapi/app/api/v1/目标模块/  # 实际代码
5. docs/DATABASE_SCHEMA.md      # 查阅数据模型
```

**说明：** 仅在本次任务明确选择 FastAPI 作为目标实现时进入这一路径。

### API 修改任务

```
1. AGENTS.md                    # 了解 API 契约约束
2. docs/API_ENDPOINTS.md        # 查阅现有 API
3. docs/DATABASE_SCHEMA.md      # 理解数据模型
4. 搜索前端调用点                # grep -r "api/xxx" frontend/src/
5. 修改代码并测试
6. 更新 docs/API_ENDPOINTS.md   # 同步文档
```

**说明：** 如果本次 API 修改影响共享对外契约，需要同时评估 Django 与 FastAPI 两套替代实现。

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
- [AI 上下文索引](./AI_CONTEXT.md)
- [系统架构](./ARCHITECTURE.md)
- [API 端点](./API_ENDPOINTS.md)
- [数据库模型](./DATABASE_SCHEMA.md)
- [文档同步清单](./DOC_SYNC_CHECKLIST.md)
- [已知陷阱](./KNOWN_PITFALLS.md)
- [技术债务](./TECH_DEBT.md)
- [代理启动提示词](./AGENT_STARTER_PROMPT.md)
- [文档同步检查清单](./DOC_SYNC_CHECKLIST.md)

---

**最后更新：** 2026-04-09
**维护者：** DV-Admin Team
