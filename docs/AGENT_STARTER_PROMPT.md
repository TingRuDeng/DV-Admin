# DV-Admin 代理启动提示词

> 复制以下内容到新的代理会话，快速启动开发工作。

---

## 启动提示词

```
我正在 DV-Admin 项目中工作。请按以下步骤开始：

1. 阅读项目规则入口：AGENTS.md
2. 阅读文档导航：docs/README.md
3. 根据任务类型阅读相关文档：
   - 前端任务：frontend/README.md
   - 后端任务（Django）：backend/README.md
   - 后端任务（FastAPI）：fastapi/README.md
   - API 修改：docs/API_ENDPOINTS.md
   - 数据模型：docs/DATABASE_SCHEMA.md

项目概述：
- 前端：Vue 3 + TypeScript + Element Plus
- 后端 A：Django 4.x + DRF + JWT
- 后端 B：FastAPI + Tortoise ORM（异步）
- 两套后端是替代实现，日常开发/部署通常二选一
- 共享 API 契约需保持 Django / FastAPI 兼容

默认账户：admin/123456

请先阅读上述文档，然后告诉我你已准备好，我将描述具体任务。
```

---

## 快速任务提示词

### 前端开发任务

```
我需要在 DV-Admin 前端添加一个新功能。

任务描述：[具体描述]

请按以下步骤进行：
1. 阅读 AGENTS.md 了解工作规则
2. 阅读 docs/ARCHITECTURE.md 了解架构
3. 在 frontend/src/views/ 创建页面组件
4. 在 frontend/src/api/ 添加 API 调用
5. 确保代码通过 pnpm run lint 检查
```

### 后端开发任务（Django）

```
我需要在 DV-Admin Django 后端添加一个新 API。

任务描述：[具体描述]

请按以下步骤进行：
1. 阅读 AGENTS.md 了解工作规则
2. 阅读 docs/API_ENDPOINTS.md 了解现有 API
3. 在 backend/drf_admin/apps/ 对应模块添加代码
4. 如需修改模型，创建迁移文件
5. 确保 API 与 FastAPI 后端兼容
```

### 后端开发任务（FastAPI）

```
我需要在 DV-Admin FastAPI 后端添加一个新 API。

任务描述：[具体描述]

请按以下步骤进行：
1. 阅读 AGENTS.md 了解工作规则
2. 阅读 docs/API_ENDPOINTS.md 了解现有 API
3. 在 fastapi/app/api/v1/ 对应模块添加端点
4. 在 fastapi/app/schemas/ 定义模型
5. 确保 API 与 Django 后端兼容
```

### Bug 修复任务

```
我在 DV-Admin 项目中遇到了一个 bug。

问题描述：[具体描述]
复现步骤：[步骤]
预期行为：[预期]
实际行为：[实际]

请按以下步骤进行：
1. 阅读 docs/KNOWN_PITFALLS.md 检查是否已知问题
2. 定位问题代码
3. 修复并测试
4. 如发现新陷阱，更新 KNOWN_PITFALLS.md
```

### API 修改任务

```
我需要修改 DV-Admin 的一个 API。

API 路径：[路径]
修改内容：[描述]

请按以下步骤进行：
1. 阅读 AGENTS.md 了解 API 契约约束
2. 阅读 docs/API_ENDPOINTS.md 了解现有 API
3. 搜索前端调用点：grep -r "api/xxx" frontend/src/
4. 同时修改 Django 和 FastAPI 两个后端
5. 更新 docs/API_ENDPOINTS.md
```

---

## 注意事项

1. **代码是真理之源** - 文档仅供参考，以实际代码为准
2. **双后端兼容** - 修改 API 时需同时更新 Django 和 FastAPI
3. **命名转换** - 前端 camelCase，后端 snake_case，中间件自动处理
4. **文档同步** - 代码变更后更新相关文档

---

**最后更新：** 2026-03-23
**维护者：** DV-Admin Team
